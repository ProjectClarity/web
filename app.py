from imports import *

dev = os.environ.get('dev') == 'true' or not os.environ.get('PORT')

app = Flask(__name__)
app.secret_key = os.environ.get('SK')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login_signup_view"

@login_manager.user_loader
def load_user(access_token):
  u = User(access_token)
  return u if u.check() else None

from routes import *

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=int(os.environ.get('PORT') or 5000), debug=dev)
