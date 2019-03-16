from okayjournal.config import PORT, HOST
from okayjournal.routes import *
from okayjournal.api import *

app.run(port=PORT, host=HOST)
