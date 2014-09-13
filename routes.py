from app import app
from imports import *
from user import User
from helpers import get_flow, humanize
from remote import processed_data

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

@app.route('/user/<int:pin>/calendar/events/<int:n>')
def user_calendar_view(pin, n):
  user = User.from_token(pin)
  if not user:
    return jsonify({'error': True, 'message': 'User not found'})
  events, page_token, sync_token = user.get_calendar_events(n, page_token=request.args.get('page_token'), sync_token=request.args.get('sync_token'))
  return jsonify({'events': events, 'page_token': page_token, 'sync_token': sync_token})

@app.route('/events/create', methods=['POST'])
def events_create_view():
  event_ids = request.json['event_ids']
  field_excludes = ['_id', 'email_id', 'title', 'user_id', 'datetime', 'end', 'location', 'url', 'source']
  for event_id in event_ids:
    event_obj = processed_data.find_one({'_id': ObjectId(event_id)})
    user = User.from_id(event_obj['user_id'])
    event_obj_filtered = {k:v for k,v in event_obj.iteritems() if k not in field_excludes}
    description = "\n".join(["{}: {}".format(humanize(k), v) for k,v in event_obj_filtered.iteritems()])
    event = {
      'summary': event_obj['title'],
      'start': {
        'dateTime': event_obj['datetime'][0].isoformat("T"),
        'timeZone': user.get_timezone()
      },
      'end': {
        'dateTime': event_obj.get('end', event_obj['datetime'][0] + datetime.timedelta(hours=1)).isoformat("T"),
        'timeZone': user.get_timezone()
      },
      'description': description,
      'extendedProperties': {
        'shared': event_obj_filtered
      }
    }
    if event.get('location'):
      event['location'] =  event_obj.get('location')
    if event.get('source') or event_obj.get('url'):
      event['source'] = {}
      if event.get('source'):
        event['source']['title'] = event_obj.get('source')
      if event.get('url'):
        event['source']['url'] = event_obj.get('url')
    _id = user.insert_calendar_event(event)
    # processed_data.remove({'_id': event_obj['_id']})
    return jsonify({'status': 'ok', 'id': _id, 'event': event})
