import anvil.secrets
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import Shopify_API
import requests

@anvil.server.callable
def send_telegram_message(message):
  BOT_TOKEN = '7125646035:AAFyT7KcJx0FSBQG5KJ-xhEnxuSRYAfhaPQ'
  CHAT_ID = '909283054'
  url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
  response = requests.get(url)
  return response.json()

@anvil.server.callable
def get_session_id():
  return anvil.server.get_session_id()

@anvil.server.callable
def get_my_creations():
  session_id = get_session_id()
  if session_id is not None:
    return app_tables.creations.client_writable(session_id=session_id)

@anvil.server.background_task
def get_my_creations_bg_task(session_id):
  if session_id is not None:
    return app_tables.creations.client_writable(session_id=session_id)

@anvil.server.callable
def launch_bg_get_creations():
  task = anvil.server.launch_background_task('get_my_creations_bg_task', get_session_id())
  return task
    
@anvil.server.callable
def delete_creation(item):
  item.delete()

@anvil.server.callable
def launch_add_to_cart_task(item, locale):
  task = anvil.server.launch_background_task('add_to_cart_bg_task',item, locale)
  return task

@anvil.server.background_task
def add_to_cart_bg_task(item, locale):
  row = app_tables.cart_added.add_row(**item)
  anvil_id = row.get_id()
  # create a product and return the product variant
  string_len_meters = int(row['wire_len_km']*1000)
  variant_id = Shopify_API.anvil_to_shopify(row['out_image'], anvil_id, locale, string_len_meters)
  return variant_id, anvil_id
