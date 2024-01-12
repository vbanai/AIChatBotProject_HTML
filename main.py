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

load_dotenv()
openai.api_key=os.getenv("OPENAI_KEY")


app = flask_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)



