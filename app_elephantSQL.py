from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import os
import pandas as pd
import os
import openai
import docx
import pandas as pd
from datetime import datetime
import inflect
from dotenv import load_dotenv, find_dotenv
from ChatGPTpart import get_Chat_response
from loadtoElephantSQL import upload_to_ElephantSQL
import psycopg2
from psycopg2 import sql



def flask_app(general_services_file_path):

  app=Flask(__name__)

  text=""

#-----------------------------------------------------------------------------------------------
#             Reading the databases needed for the process in
#-----------------------------------------------------------------------------------------------



  def data_preparation(general_services_file_path):
    load_dotenv()
    #database_url=os.getenv("DATABASE_URL")
    database_url = 'postgres://omeakqpt:xUUfVIvuZMNPUookJJXGiq4vFAwcShil@flora.db.elephantsql.com/omeakqpt'


    with psycopg2.connect(database_url) as connection:
      sql_query = 'SELECT * FROM "orders"'
      df_existing_customer_original = pd.read_sql(sql_query, connection)
      sql_query2 = 'SELECT * FROM "questions_potentialcustomers"'
      df_potential_customer = pd.read_sql(sql_query2, connection)
    
    df_existing_customer=df_existing_customer_original.to_string(index=False)

    doc=docx.Document(general_services_file_path)
    full_text=""
    for paragraph in doc.paragraphs:
      full_text+=paragraph.text+ "\n"
    word_text=full_text.strip()

    return df_existing_customer_original, df_existing_customer, df_potential_customer, word_text

#-----------------------------------------------------------------------------------------------
#             Important variables
#-----------------------------------------------------------------------------------------------

  
  df_existing_customer_original, df_existing_customer, df_potential_customer, word_text=data_preparation(general_services_file_path)
   
  context = [
  
    {'role': 'system', 'content': f"""
    You are telefonoperator in AutoDé Kft and you are answering incoming questions in English. \
    If the user has a question regarding the ongoing order, ask for the client number.\
    If the user has general questions, there's no need to ask for the client number. \            
    User: Can you give me the client number? Assistant: Please provide your client number.\
    If the client number is provided, respond to the user based on the information in the table:{df_existing_customer} \
    I will provide an example to guide you on using customer numbers in your response. \
    Check if you can find the provided customer number in the 'Customer Number' column of the table.\
    
    Please note: Customer numbers usually have three digits (e.g., 312, 412, 512). However, '112' is not a valid existing customer number, \
    even though it might be mentioned. Do not consider '112' as a valid customer number from the table.\
    
    If you find the provided customer number, retrieve the details of the corresponding order. If not, inform the user accordingly.\
    Without the client number, initiate conversation with the user using only the information from the document:{word_text}. \
    Respond briefly, and your response should be in one installment, not multiple parts. Always ask if you can help with anything else.

    
    
  """}

  ]
#-----------------------------------------------------------------------------------------------
#             Flask ROUTING
#-----------------------------------------------------------------------------------------------


  @app.route("/")
  @app.route('/home')
  def index():
    return render_template('index.html')

  @app.route("/popupchat")
  def popupchat():
    return render_template('popupchat.html')

  @app.route("/messengerchat")
  def messengerchat():
    nonlocal text
    if text!="":
      output_file_creation(df_existing_customer_original, df_potential_customer, text)
      text=""
    return render_template('messengerchat.html')

  @app.route("/chat")
  def AIChatBot():
    return render_template('chat.html')
  text=""
  @app.route("/get", methods=["GET", "POST"])
  def chat():
    nonlocal text
    msg=request.form["msg"]
    input=msg
    context.append({'role':'user', 'content':f"{input}"})
    response=get_Chat_response(context)
    text+=("USER: " + input + " | " + "ASSISTANT: " + response)
    context.append({'role':'assistant', 'content':f"{response}"})
    return response
  
#-----------------------------------------------------------------------------------------------
#             Updating the databases with the new conversation
#-----------------------------------------------------------------------------------------------


  def output_file_creation(df_existing_customer_original, df_potential_customer, text):
    
    database_url = 'postgres://omeakqpt:xUUfVIvuZMNPUookJJXGiq4vFAwcShil@flora.db.elephantsql.com/omeakqpt'

    current_date = datetime.now().date()
    current_date = current_date.strftime("%Y-%m-%d")
    new_column_header = 'Chat'+ current_date
    
    spotting_identifier=df_existing_customer_original["customernumber"].apply(lambda x: text.lower().find(str(x).lower()) !=-1)

    if not any(spotting_identifier)==True:
      table_name='questions_potentialcustomers'
      if new_column_header not in df_potential_customer.columns.tolist():
        df_potential_customer[new_column_header]=None
        df_potential_customer.loc[0, new_column_header]=''
        df_potential_customer.loc[0, new_column_header]+=text
        upload_to_ElephantSQL(database_url, table_name, df_potential_customer)
        df_potential_customer=df_potential_customer
      else:
        last_not_empty_index=df_potential_customer[new_column_header].last_valid_index()
        df_potential_customer.loc[last_not_empty_index+1, new_column_header]=''
        df_potential_customer.loc[last_not_empty_index+1, new_column_header]+=text
        upload_to_ElephantSQL(database_url, table_name, df_potential_customer)
        df_potential_customer=df_potential_customer
      
    else:
      if new_column_header not in df_existing_customer_original.columns.tolist():
        df_existing_customer_original[new_column_header]=''
  
      row=df_existing_customer_original[spotting_identifier].index.item()

      existing_value = str(df_existing_customer_original.loc[row, new_column_header]) if not pd.isna(df_existing_customer_original.loc[row, new_column_header]) else ""
      df_existing_customer_original.loc[row, new_column_header]=existing_value + text
      table_name='order_existing_clients'
      upload_to_ElephantSQL(database_url, table_name, df_existing_customer_original)
      df_existing_customer_original=df_existing_customer_original
      

  return app

