from okayjournal.config import PORT, HOST

# noinspection PyUnresolvedReferences
from okayjournal.routes import *
from okayjournal.api import *

app.run(port=PORT, host=HOST)
