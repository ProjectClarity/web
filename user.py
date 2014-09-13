from remote import users
import random

class User():
  def __init__(self, access_token):
    self.user = users.find_one({'access_token': access_token})

  def get(self, key):
    return self.user.get(key, '')

  def set(self, key, value):
    users.update({'_id': self.user['_id']}, {'$set': {key: value}})
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
    return str(self.user['_id'])

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
