from flask import Flask, render_template, request, jsonify

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






if __name__ == "__main__":
    app = flask_app()
    app.run(host='0.0.0.0', port=5000, debug=True)



