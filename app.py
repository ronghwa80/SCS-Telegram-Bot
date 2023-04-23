# A Telegram Webhook Service for SCS Cyber Community Chat Group
# This service support a) testing of running service, b) setting up of webhook, and c) processing of telegram messages
# * A HOOK_TOKEN is a "share secret" with the provider. Recommend to update its value whenever required
# ! Set HOOK_TOKEN to be at least 64 characters long to mitigate against 'bot' command injection
# ! To setup, trigger the setwebhook command by visiting https://{WEBHOOK_URL_BASE}/setwebhook
# Baseline environment variables for app.py: HOOK_URL, HOOK_TOKEN
# Baseline environment variables for SCSTelegramBot: OPENAI_API_KEY,  FINETUNED_MODEL, BOT_TOKEN, MODE

import os
import telebot
import logging
from SCSTelegramBot import SCSBotWrapper
from flask import Flask, request

# Initialise global variable
app = Flask(__name__)
scsbot = SCSBotWrapper()
# Production HOOK_URL needs to be https with TLS 1.2 and above
HOOK_URL = os.environ.get('HOOK_URL', "http://127.0.0.1:8080");
# HOOK_TOKEN is a shared secret set with a default example for reference and basic protection
# *This default token for production environment must be changed
HOOK_TOKEN = os.environ.get('HOOK_TOKEN',"Tknq4p3ZfQXJBfzBAxQsekuHPaaUzvr3akZ8yq3LMsxoDtGK6XnFhHAznjbWnpde");

# Process webhook calls
@app.route('/{}'.format(HOOK_TOKEN), methods=["POST"])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        scsbot.process_webhook(json_string)
    return ''

# Setup webhook
@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    endpoint_url = '{hook_url}/{hook_token}'.format(hook_url = HOOK_URL, hook_token=HOOK_TOKEN)
    s = scsbot.set_webhook(endpoint_url)
    if s:
        return "Webhook setup ok"
    else:
        return "webhook setup failed"
    
# Setup webhook
@app.route('/removewebhook', methods=['GET', 'POST'])
def remove_webhook():
    s = scsbot.remove_webhook()
    if s:
        return "Webhook is removed"
    else:
        return "webhook cannot be removed"

# Testing hosting
@app.route('/', methods = ['GET', 'POST'])
def index():
    return 'It works!'

# Run service on port 8080
if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')

    # ! Flask should not be run in debugging mode for production
    isdebug = True if os.environ.get ('DEBUG') == 'true' else False
    app.run(debug=isdebug, port=server_port, host='0.0.0.0')