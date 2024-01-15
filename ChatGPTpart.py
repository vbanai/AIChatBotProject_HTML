
import os
import pandas as pd
import os
import openai
import docx
import pandas as pd
from datetime import datetime
import inflect
from dotenv import load_dotenv, find_dotenv


if os.getenv("FLASK_ENV") == "development":
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_KEY")
else:
    
    openai.api_key = os.environ.get('OPENAI_KEY')


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


