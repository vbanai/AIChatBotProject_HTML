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



# from transformers import AutoModelForCausalLM, AutoTokenizer
# import torch

# tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
# model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

# df_existing_customer_original=pd.read_excel(r"C:\Users\vbanai\Documents\Programming\Dezsi porject\ChatFrontEnd\tutorial4\Order_existing_clients.xlsx")
# df_existing_customer=df_existing_customer_original.to_string(index=False)
# df_potential_customer=pd.read_excel(r"C:\Users\vbanai\Documents\Programming\Dezsi porject\ChatFrontEnd\tutorial4\Questions_PotentialCustomers.xlsx")

# print(df_existing_customer)

# doc=docx.Document(r"C:\Users\vbanai\Documents\Programming\Dezsi porject\ChatFrontEnd\tutorial4\Cars_services.docx")
# full_text=""
# for paragraph in doc.paragraphs:
#   full_text+=paragraph.text+ "\n"
# word_text=full_text.strip()

# def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0):
#   response = openai.ChatCompletion.create(
#       model=model,
#       messages=messages,
#       temperature=temperature, 
#   )
#   return response.choices[0].message["content"]

# context = [
#   {'role': 'system', 'content': f"""
#   You are telefonoperator in AutoDé Kft and you are answering incoming questions in English. Provide a complete response in a single message\
#   If the user has question regarding the ongoing order, ask the client number. Consider each client number individually.\
#   If the user has general questions don't need to ask the client number \            
#   User: Can you give me the client number? Assistant: Please give me your client number.\
#   If the client number is provided, answer the user according to  the table:{df_existing_customer} \
#   Without the client number, start chatting with the user, you can't use external sources, only the 
#   document:{word_text}. \
#   Respond briefly, and always ask if you can help with anything else. 
  
# """}]

def flask_app(df_existing_customer, word_text):

  app=Flask(__name__)

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

  @app.route("/")
  @app.route('/home')
  def index():
    return render_template('index.html')

  @app.route("/popupchat")
  def popupchat():
    return render_template('popupchat.html')

  @app.route("/messengerchat")
  def messengerchat():
    return render_template('messengerchat.html')

  @app.route("/chat")
  def AIChatBot():
    return render_template('chat.html')

  @app.route("/get", methods=["GET", "POST"])
  def chat():
    msg=request.form["msg"]
    input=msg
    context.append({'role':'user', 'content':f"{input}"})
    response=get_Chat_response(context)
    context.append({'role':'assistant', 'content':f"{response}"})
    return response

# def get_Chat_response(context):
#   response=get_completion_from_messages(context) 
#   context.append({'role':'assistant', 'content':f"{response}"})
#   return response

# def get_Chat_response(text):
#   # Let's chat for 5 lines
#   for step in range(5):
#       # encode the new user input, add the eos_token and return a tensor in Pytorch
#       new_user_input_ids = tokenizer.encode(str(text) + tokenizer.eos_token, return_tensors='pt')

#       # append the new user input tokens to the chat history
#       bot_input_ids = torch.cat([chat_history_ids, new_user_input_ids], dim=-1) if step > 0 else new_user_input_ids

#       # generated a response while limiting the total chat history to 1000 tokens, 
#       chat_history_ids = model.generate(bot_input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)

#       # pretty print last ouput tokens from bot
#       return tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
  return app

