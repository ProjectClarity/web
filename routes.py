from app import app
from imports import *
from user import User
from helpers import get_flow, humanize
from remote import processed_data
import requests

@app.route('/')
@login_required
def index_view():
  events = processed_data.find({'user_id': current_user.get('_id')}).limit(5)
  events = [{k:str(v) if k.endswith('_id') else v for k,v in event.iteritems()} for event in events]
  return render_template('index.html', events=events)

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
  if u.get('disabled', False):
    u.update({'disabled': False, 'credentials': credentials_object})
  login_user(u, remember=True)
  return redirect(url_for('index_view'))

@app.route('/user/<int:pin>/calendars')
def user_calendars_view(pin):
  user = User.from_token(pin)
  if not user:
    return jsonify({'error': True, 'message': 'User not found'})
  return jsonify({'calendars': user.get_calendars()})

@app.route('/user/<int:pin>/calendar/events/<int:n>')
def user_calendar_events_view(pin, n):
  user = User.from_token(pin)
  if not user:
    return jsonify({'error': True, 'message': 'User not found'})
  events, page_token, sync_token = user.get_calendar_events(n, calendar_id=request.args.get('calendar_id', user.get_clarity_calendar()), page_token=request.args.get('page_token'), sync_token=request.args.get('sync_token'))
  return jsonify({'events': events, 'page_token': page_token, 'sync_token': sync_token})

@app.route('/user/<int:pin>/calendar/events/<event_id>/destroy', methods=['POST'])
def event_destroy_view(pin, event_id):
  user = User.from_token(pin)
  if not user:
    return jsonify({'error': True, 'message': 'User not found'})
  try:
    user.destroy_calendar_event(event_id, calendar_id=request.args.get('calendar_id', user.get_clarity_calendar()))
    processed_data.remove({'event_id': event_id})
  except:
    pass
  return jsonify({'status': 'ok'})

@app.route('/events/create', methods=['POST'])
def events_create_view():
  event_ids = request.json['event_ids']
  field_excludes = ['_id', 'email_id', 'title', 'user_id', 'datetime', 'end', 'location', 'url', 'source', 'latitude', 'longitude', 'original_body']
  processed_event_ids = []
  events = []
  for event_id in event_ids:
    event_obj = processed_data.find_one({'_id': ObjectId(event_id)})
    user = User.from_id(event_obj['user_id'])
    event_obj_filtered = {k:v for k,v in event_obj.iteritems() if k not in field_excludes}
    description = "\n".join(["{}: {}".format(humanize(k), v) for k,v in event_obj_filtered.iteritems()])
    if event_obj.get('original_body'):
      description += "\n\nOriginal Email:\n" + event_obj.get('original_body')
    event = {
      'summary': event_obj['title'],
      'start': {
        'dateTime': event_obj['datetime'].isoformat("T"),
        'timeZone': user.get_timezone()
      },
      'end': {
        'dateTime': (event_obj.get('end',[None])[0] or event_obj['datetime'] + datetime.timedelta(hours=1)).isoformat("T"),
        'timeZone': user.get_timezone()
      },
      'description': description,
      'extendedProperties': {
        'shared': event_obj_filtered
      }
    }
    if event_obj.get('latitude') and event_obj.get('longitude'):
      event['location'] = event_obj.get('latitude') + "," + event_obj.get('longitude')
    elif event_obj.get('location'):
      event['location'] = event_obj.get('location')
    if event_obj.get('source') or event_obj.get('url'):
      event['source'] = {}
      event['source']['title'] = event_obj.get('source', event_obj['title'])
      event['source']['url'] = event_obj.get('url', url_for('index_view', _external=True))
    event_id = user.insert_calendar_event(event, calendar_id=user.get_clarity_calendar())
    user.tag_message(event_obj['email_id'], [os.getenv('TAG_NAME')])
    processed_event_ids.append(event_id)
    events.append(event)
    processed_data.update({'_id': event_obj['_id']}, {'$set': {'event_id': event_id}, '$unset': {'original_body': True}})
  return jsonify({'status': 'ok', 'ids': processed_event_ids, 'events': events})

@app.route('/user/distance')
def user_distance_view():
  GOOGLE_API_ROOT = 'https://maps.googleapis.com/maps/api/distancematrix/json'
  UBER_API_ROOT = 'https://api.uber.com/v1'

  origin = request.args.get('current_location')
  distances = {}
  destinations = request.args.get('destinations').split(';')
  for destination in destinations:
    distances[destination] = {}
    headers = {'Authorization': 'Token ' + os.getenv('UBER_API_KEY')}
    query = {
      'start_latitude': origin.split(',')[0],
      'start_longitude': origin.split(',')[1],
      'end_latitude': destination.split(',')[0],
      'end_longitude': destination.split(',')[1],
    }
    price_resp = requests.get(UBER_API_ROOT + '/estimates/price', params=query, headers=headers).json()
    for price in price_resp.get('prices', []):
      if price['display_name'] == 'uberX':
        distances[destination]['uber_price'] = price['estimate']
        break
    time_resp = requests.get(UBER_API_ROOT + '/estimates/time', params=query, headers=headers).json()
    for time in time_resp.get('times', []):
      if time['display_name'] == 'uberX':
        distances[destination]['uber_time'] = time['estimate']
        break

  parameters = {
    'origins': origin,
    'destinations': '|'.join(destinations),
    'key': os.getenv('GOOGLE_API_KEY')
  }
  for mode in ['driving', 'walking']:
    parameters.update({'mode': mode})
    resp = requests.get(GOOGLE_API_ROOT, params=parameters).json()
    if len(resp['rows']) == 0:
      return jsonify({'error': True, 'message': 'Request timed out'})
    for i,destination in enumerate(resp['rows'][0]['elements']):
      try:
        distances[destinations[i]][mode] = destination['duration']['text']
      except:
        distances[destinations[i]][mode] = "N/A"
  return jsonify(distances)

