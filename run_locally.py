from os import environ
from app import app

with open('.env') as file_:
    for line in file_:
        variable = [x.strip() for x in line.split('=')]
        environ['{0}'.format(variable[0])] = '{0}'.format(variable[1])

port = int(environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port, debug=True)
app.debug=True
