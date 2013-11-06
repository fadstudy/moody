from os import environ
from app import app

port = int(environ.get('PORT', 5001))
app.run(host='0.0.0.0', port=port, debug=True)
