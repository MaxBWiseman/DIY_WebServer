import os
import sys

# Add the correct Django project directory to Python path
sys.path.insert(0, "/workspaces/DIY_WebServer/diy_web_server")

# Import your custom WSGI server
from basic_webserver import make_server, SERVER_ADDRESS

# Set the correct Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "diy_web_server.settings")

# Import the Django WSGI application
from diy_web_server.wsgi import application

if __name__ == "__main__":
    # Create a server instance
    httpd = make_server(SERVER_ADDRESS, application)
    print(f'WSGIServer: Serving Django application on port {SERVER_ADDRESS[1]} ...\n')
    # Run the server
    httpd.serve_forever()