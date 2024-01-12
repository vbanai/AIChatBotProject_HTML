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
from app import flask_app
import psycopg2
from psycopg2 import sql
from flask_basicauth import BasicAuth

load_dotenv()
openai.api_key=os.getenv("OPENAI_KEY")

existing_customers_xls_path=r"C:\Users\vbanai\Documents\Programming\Dezsi porject\ChatFrontEnd\tutorial4\Order_existing_clients.xlsx"
potential_customers_xls_path=r"C:\Users\vbanai\Documents\Programming\Dezsi porject\ChatFrontEnd\tutorial4\Questions_PotentialCustomers.xlsx"
general_services_file_path = r"C:\Users\vbanai\Documents\Programming\Dezsi porject\ChatFrontEnd\tutorial4\Cars_services.docx"



app = flask_app(existing_customers_xls_path, potential_customers_xls_path, general_services_file_path)

app.config['BASIC_AUTH_USERNAME'] = 'asdf'
app.config['BASIC_AUTH_PASSWORD'] = 'asdf'
basic_auth = BasicAuth(app)

@basic_auth.required 
@app.route("/secured_route")
def secured_route():
    return "This route requires Basic Authentication"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)




