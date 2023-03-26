# _*_ encoding: utf-8
import json
import logging

from flask import Flask

app = Flask(__name__)
try:
    app.config.from_file("config.json", load=json.load)
except FileNotFoundError:
    raise RuntimeError("Configuration file not found")
app.logger.setLevel(logging.INFO)

from app import views
