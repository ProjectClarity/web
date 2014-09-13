from imports import *
from oauth2client.client import flow_from_clientsecrets

def get_flow():
  return flow_from_clientsecrets('./client_secrets.json', scope='https://www.googleapis.com/auth/gmail.modify', redirect_uri=url_for('login_signup_callback_view', _external=True))
