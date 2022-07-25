import base64
from datetime import datetime, timedelta
import json
import os
import requests


def notification_pubsub(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    #decode base64 string to string
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    
    #send notification message to telegram channel
    response = telegram_bot_send_message(pubsub_message)
    print(response)

def telegram_bot_send_message(pubsub_message: str):
    #set local variables from environment variables
    bot_token = os.environ.get('BOT_TOKEN')
    chat_id = os.environ.get('CHAT_ID')
    
    #set request post options
    send_message_url = 'https://api.telegram.org/bot' + bot_token + '/sendMessage'
    send_message_headers = {
        'Content-Type':'application/json'
        }
    send_message_body = {
        'chat_id': chat_id, 
        'parse_mode':'HTML', 
        'text': message_template(pubsub_message)
        }

    #send request post to telegram api
    response = requests.post(send_message_url, headers=send_message_headers, json=send_message_body)

    #return the response from telegram api
    return response.json()

def message_template(pubsub_message: str):
    #convert string to json object
    json_object = json.loads(pubsub_message)
    
    #convert UTC timestamp to formated local datetime WIB (GMT+7)
    #added 7 hours to the given time
    start_time = datetime.utcfromtimestamp(json_object['incident']['started_at']) + timedelta(hours=7)
    
    #create human-readable message templates
    bot_message = '❗️<strong>Alert Firing</strong>\n\n'
    bot_message += '<strong>' + json_object['incident']['condition_name'] + '</strong>\n\n'
    bot_message += json_object['incident']['summary']+'\n\n'
    bot_message += '<strong>Start time</strong>\n' + start_time.strftime('%A, %d %b %Y at %H:%M WIB') + '\n\n'
    bot_message += '<strong>Policy</strong>\n' + json_object['incident']['policy_name'] + '\n\n'
    bot_message += '<strong>Metric</strong>\n<a>' + json_object['incident']['metric']['type'] + '</a>\n\n'
    bot_message += '<a href="' + json_object['incident']['url'] + '" target="_blank" rel="noopener">Go To Incident Details</a>\n\n'
    
    #return formated message text
    return bot_message