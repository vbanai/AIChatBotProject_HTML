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


load_dotenv()
openai.api_key=os.getenv("OPENAI_KEY")

def data_preparation(existing_customers_xls_path, potential_customers_xls_path, general_services_file_path):

  df_existing_customer_original=pd.read_excel(existing_customers_xls_path)
  df_existing_customer=df_existing_customer_original.to_string(index=False)
  df_potential_customer=pd.read_excel(potential_customers_xls_path)

  doc=docx.Document(general_services_file_path)
  full_text=""
  for paragraph in doc.paragraphs:
    full_text+=paragraph.text+ "\n"
  word_text=full_text.strip()

  return df_existing_customer_original, df_existing_customer, df_potential_customer, word_text

def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0):
  response = openai.ChatCompletion.create(
      model=model,
      messages=messages,
      temperature=temperature, 
  )
  return response.choices[0].message["content"]


def get_Chat_response(context):
  response=get_completion_from_messages(context) 
  context.append({'role':'assistant', 'content':f"{response}"})
  return response
