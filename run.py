from config import PORT, HOST, FORM_SECRET_KEY
from okayjournal.routes import *

app.config['SECRET_KEY'] = FORM_SECRET_KEY
app.run(port=PORT, host=HOST)
