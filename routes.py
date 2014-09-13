from app import app
from imports import *
from user import User
from helpers import get_flow

@app.route('/')
@login_required
def index_view():
  return render('index.html')

@app.route('/auth/go')
def login_signup_view():
  flow = get_flow()
  flow.params['access_type'] = 'offline'
  return redirect(flow.step1_get_authorize_url())

@app.route('/auth/callback')
def login_signup_callback_view():
  error = request.args.get('error')
  code = request.args.get('code')
  if not code:
    return error or 'error'
  credentials = get_flow().step2_exchange(code).to_json()
  u = User(credentials['access_token'])
  if not u.check():
    u.create(credentials)
  login_user(u, remember=True)
  return redirect(url_for('index_view'))

