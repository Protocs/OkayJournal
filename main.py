from flask import Flask
from config import HOST, PORT

app = Flask(__name__)
app.run(port=PORT, host=HOST)
