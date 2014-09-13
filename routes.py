from app import app
from imports import *
from user import User
from helpers import get_flow

@app.route('/')
@login_required
def index_view():
  return render_template('index.html')

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
  credentials = get_flow().step2_exchange(code)
  credentials_object = json.loads(credentials.to_json())
  user_info = User.fetch_info(credentials)
  u = User(user_info['email'])
  if not u.check():
    u.create(credentials=credentials_object, **user_info)
  login_user(u, remember=True)
  return redirect(url_for('index_view'))
