from flask import Flask

app = Flask(__name__)
app.secret_key = 'sitebio_ifrn_secret_key_completa'

from app import routes
