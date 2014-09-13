echo "$CLIENT_SECRETS_JSON" > client_secrets.json

if [ "$dev" == "true" ]; then
  python app.py
else
  gunicorn -b "0.0.0.0:$PORT" --workers $WEB_CONCURRENCY app:app
fi
