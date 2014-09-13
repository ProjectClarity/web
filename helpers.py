from imports import *
from oauth2client.client import flow_from_clientsecrets
import apiclient.discovery, httplib2

def build(service, credentials, v='v2'):
  return apiclient.discovery.build(serviceName=service, version=v, http=credentials.authorize(httplib2.Http()))

def get_flow():
  return flow_from_clientsecrets('./client_secrets.json',
                                  scope=['https://www.googleapis.com/auth/gmail.modify', 'https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile'],
                                  redirect_uri=url_for('login_signup_callback_view', _external=True))
