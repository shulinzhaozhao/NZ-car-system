from flask import Flask
app = Flask(__name__, static_folder="static",static_url_path="/static")
from app import main
from app import connect
from app import admin
from app import staff
from app import customer

