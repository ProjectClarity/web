from helpers import build as helpers_build
from remote import users
from oauth2client.client import OAuth2Credentials
import random, json, datetime

class User():
  def __init__(self, email):
    self.user = users.find_one({'email': email})

  @staticmethod
  def from_token(token):
    u = users.find_one({'token': token})
    if not u:
      return None
    return User(u.get('email'))

  @staticmethod
  def from_id(_id):
    u = users.find_one({'_id': _id})
    if not u:
      return None
    return User(u.get('email'))

  def get(self, key):
    return self.user.get(key, '')

  def set(self, key, value):
    self.update({key: value})

  def update(self, d):
    users.update({'_id': self.user['_id']}, {'$set': d})
    self.user = users.find_one({'_id': self.get('_id')})

  def check(self):
    try:
      return self.user is not None
    except:
      return False

  def create(self, **kwargs):
    _id = users.insert(kwargs)
    self.user = users.find_one({'_id': _id})

  def logged_in(self):
    return self.check()

  def get_id(self):
    return self.get('email')

  def is_anonymous(self):
    return False

  def is_active(self):
    return self.is_authenticated()

  def is_authenticated(self):
    return self.check() and self.logged_in()

  def token(self):
    token = self.get('token')
    if not token:
      while not token:
        token = random.randint(1000, 10000)
        if users.find_one({'token': token}):
          token = None
      self.update({'token': token})
    return token

  def get_credentials(self):
    return OAuth2Credentials.from_json(json.dumps(self.get('credentials')))

  def build(self, service, **kwargs):
    return helpers_build(service, self.get_credentials(), **kwargs)

  def get_timezone(self):
    timezone = self.get('timezone')
    if not timezone:
      calendar_service = self.build('calendar', v='v3')
      default_calendar = calendar_service.calendars().get(calendarId='primary').execute()
      self.set('timezone', default_calendar['timeZone'])
    return timezone

  def get_calendars(self):
    calendar_service = self.build('calendar', v='v3')
    calendar_list = calendar_service.calendarList().list().execute()
    return calendar_list['items']

  def get_calendar_events(self, n, calendar_id='primary', page_token=None, sync_token=None):
    calendar_service = self.build('calendar', v='v3')
    now = datetime.datetime.utcnow().isoformat("T") + "Z"
    events = calendar_service.events().list(calendarId=calendar_id, orderBy='startTime', maxResults=n, pageToken=page_token, syncToken=sync_token, singleEvents=True, timeMin=now).execute()
    return events['items'], events.get('nextPageToken'), events.get('nextSyncToken')

  def insert_calendar_event(self, event):
    calendar_service = self.build('calendar', v='v3')
    return calendar_service.events().insert(calendarId='primary', body=event).execute()['id']

  @staticmethod
  def fetch_info(credentials):
    user_info_provider = helpers_build('oauth2', credentials)
    user_info = user_info_provider.userinfo().get().execute()
    return user_info
