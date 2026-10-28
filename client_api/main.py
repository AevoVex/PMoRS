import os

from dotenv import load_dotenv
from pyrogram import Client

load_dotenv()

api_id = int(os.environ['TELEGRAM_API_ID'])
api_hash = os.environ['TELEGRAM_API_HASH']

app = Client('my_account', api_id, api_hash, workdir=os.path.dirname(__file__))

app.start()
app.send_message('me', 'Привет, это я!')
app.stop()
