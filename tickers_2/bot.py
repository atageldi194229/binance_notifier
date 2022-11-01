import requests

def bot_send_message(msg):
    try:
        x = requests.get(f'http://127.0.0.1:3001/message/{msg}')
    except Exception as e:
        print(e)