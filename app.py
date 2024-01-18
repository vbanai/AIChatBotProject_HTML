import string
from flask import Flask, render_template, request, jsonify
import json
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
from google.auth import exceptions
import io
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaIoBaseDownload
from docx import Document
import tempfile
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from google.oauth2 import service_account
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from azure.storage.blob import BlobServiceClient



import logging


log_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs/')
os.makedirs(log_directory, exist_ok=True)
logging.basicConfig(filename=os.path.join(log_directory, 'app.log'), level=logging.INFO)


def flask_app(host=None, port=None):

  app=Flask(__name__)

  textvariable=""

#-----------------------------------------------------------------------------------------------
#             Reading the databases needed for the process in
#-----------------------------------------------------------------------------------------------



  def data_preparation():
    
    if os.getenv("FLASK_ENV") == "development":
      
      load_dotenv()
      connection_string = os.getenv("CONNECTION_STRING")
      database_url = os.getenv('DATABASE_URL')
      
    else:
      # Retrieve the private key from the environment variable
      #private_key_str = os.environ.get('PRIVATE_KEY')
      connection_string = os.environ.get("CONNECTION_STRING")
      database_url = os.environ.get('DATABASE_URL')

    database_url=database_url.replace('postgres', 'postgresql')
    engine = create_engine(database_url)

  
   
    sql_query2 = 'SELECT * FROM "questions_potentialcustomers"'
    df_potential_customer = pd.read_sql(sql_query2, engine)
    sql_query = 'SELECT * FROM "order_existing_clients"'
    df_existing_customer_original = pd.read_sql(sql_query, engine)
      
    sql_query_orders = text('SELECT * FROM "orders"')
    with engine.connect() as connection:
        # Execute the SQL query
        #sql_query_orders = 'SELECT * FROM "orders"'
        result = connection.execute(sql_query_orders)

        # Fetch all rows
        rows = result.fetchall()

    # Extract column names
    columns = result.keys()

    # Format data as a string
    data_rows = []
    for row in rows:
        data_rows.append(" | ".join(map(str, row)))

    # Create the final string
    df_existing_customer = " | ".join(columns) + "\n" + "\n".join(data_rows)


    # CREATING THE TXT FILE FROM THE DOWNLOADED BLOB FILE

    container_name = 'filefolder'
    filename='Cars_services.docx'

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)
    blob_content = blob_client.download_blob().readall()

    # Assuming blob_content contains the binary data of the Word file
    word_content = blob_content

    # Create a temporary file to save the Word content
    temp_dir = tempfile.gettempdir()
    temp_file_path = os.path.join(temp_dir, 'temp_word_file.docx')

    with open(temp_file_path, 'wb') as temp_file:
        temp_file.write(word_content)

    # Open the Word file as a ZIP archive
    with zipfile.ZipFile(temp_file_path, 'r') as zip_file:
        # Extract the content of 'word/document.xml'
        xml_content = zip_file.read('word/document.xml')

    # Parse the XML content
    xml_root = ET.fromstring(xml_content)

    # Extract text content from paragraphs
    text_content = []
    for paragraph in xml_root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
        text_blob = ''.join(run.text for run in paragraph.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'))
        text_content.append(text_blob)

    # Print the extracted text content
    word_text='\n'.join(text_content)

    # Optionally, remove the temporary file after processing
    os.remove(temp_file_path)


    
    
    return df_existing_customer_original, df_existing_customer, df_potential_customer, word_text

#-----------------------------------------------------------------------------------------------
#             Important variables
#-----------------------------------------------------------------------------------------------

  
  df_existing_customer_original, df_existing_customer, df_potential_customer, word_text=data_preparation()
   
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
    nonlocal textvariable
    if textvariable!="":
      output_file_creation(df_existing_customer_original, df_potential_customer, textvariable)
      textvariable=""
    return render_template('messengerchat.html')

  @app.route("/chat")
  def AIChatBot():
    return render_template('chat.html')
  textvariable=""
  @app.route("/get", methods=["GET", "POST"])
  def chat():
    nonlocal textvariable
    msg=request.form["msg"]
    input=msg
    context.append({'role':'user', 'content':f"{input}"})
    response=get_Chat_response(context)
    textvariable+=("USER: " + input + " | " + "ASSISTANT: " + response)
    context.append({'role':'assistant', 'content':f"{response}"})
    return response
  
#-----------------------------------------------------------------------------------------------
#             Updating the databases with the new conversation
#-----------------------------------------------------------------------------------------------


  def output_file_creation(df_existing_customer_original, df_potential_customer, textvariable):
    
    
    load_dotenv()
    database_url = os.environ.get('DATABASE_URL')

    current_date = datetime.now().date()
    current_date = current_date.strftime("%Y-%m-%d")
    new_column_header = 'Chat'+ current_date
    
    spotting_identifier=df_existing_customer_original["customernumber"].apply(lambda x: textvariable.lower().find(str(x).lower()) !=-1)

    if not any(spotting_identifier)==True:
      table_name='questions_potentialcustomers'
      if new_column_header not in df_potential_customer.columns.tolist():
        df_potential_customer[new_column_header]=None
        df_potential_customer.loc[0, new_column_header]=''
        df_potential_customer.loc[0, new_column_header]+=textvariable
        upload_to_ElephantSQL(database_url, table_name, df_potential_customer)
        df_potential_customer=df_potential_customer
      else:
        last_not_empty_index=df_potential_customer[new_column_header].last_valid_index()
        df_potential_customer.loc[last_not_empty_index+1, new_column_header]=''
        df_potential_customer.loc[last_not_empty_index+1, new_column_header]+=textvariable
        upload_to_ElephantSQL(database_url, table_name, df_potential_customer)
        df_potential_customer=df_potential_customer
      
    else:
      if new_column_header not in df_existing_customer_original.columns.tolist():
        df_existing_customer_original[new_column_header]=''
  
      row=df_existing_customer_original[spotting_identifier].index.item()

      existing_value = str(df_existing_customer_original.loc[row, new_column_header]) if not pd.isna(df_existing_customer_original.loc[row, new_column_header]) else ""
      df_existing_customer_original.loc[row, new_column_header]=existing_value + textvariable
      table_name='order_existing_clients'
      upload_to_ElephantSQL(database_url, table_name, df_existing_customer_original)
      df_existing_customer_original=df_existing_customer_original

  
  return app

