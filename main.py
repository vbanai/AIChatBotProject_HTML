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

load_dotenv()
openai.api_key=os.getenv("OPENAI_KEY")

existing_customers_xls_path=r"C:\Users\vbanai\Documents\Programming\Dezsi porject\ChatFrontEnd\tutorial4\Order_existing_clients.xlsx"
potential_customers_xls_path=r"C:\Users\vbanai\Documents\Programming\Dezsi porject\ChatFrontEnd\tutorial4\Questions_PotentialCustomers.xlsx"
general_services_file_path = r"C:\Users\vbanai\Documents\Programming\Dezsi porject\ChatFrontEnd\tutorial4\Cars_services.docx"



app = flask_app(existing_customers_xls_path, potential_customers_xls_path, general_services_file_path)

if __name__ == "__main__":
    app.run(debug=True)



