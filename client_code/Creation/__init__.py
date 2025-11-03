from ._anvil_designer import CreationTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..AddFramePopup import AddFramePopup

WH_IMG_CARD = 350

def send_add_to_cart(variant_id, anvil_id, add_frame):
  """Отправляем postMessage родительскому окну для добавления товара в корзину"""
  frame_variant = 43092453359731 # product id 8003777167475
  
  message = {
    'sender': "https://poy3xlkm3h3flba5.anvil.app",
    'action': 'add',
    'variant_id': int(variant_id),
    'anvil_id': anvil_id,
    'add_frame': add_frame,
    'frame_id': frame_variant,
  }
  
  print(f"Sending postMessage to parent window: {message}")
  anvil.js.window.parent.postMessage(message, '*')

class Creation(CreationTemplate):
  def __init__(self, locale, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.image_1.height = WH_IMG_CARD
    # self.image_1.width = WH_IMG_CARD
    self.image_1.source = self.item['out_image_medium']
    length_meters = int(self.item['wire_len_km']*1000)
    self.text_length.text = 'String length: ' + str(length_meters) + ' meters'
    self.locale = locale
    if locale == 'he':
      self.button_add_to_cart.text = 'הוספה לעגלה'
      self.button_add_to_cart.font_family = 'Rubik'
      self.text_length.text = f'אורך חוט: {length_meters} מטרים'
      self.text_length.font_family = 'Rubik'

  def link_delete_click(self, **event_args):
    self.remove_from_parent()
    anvil.server.call_s('delete_creation', self.item)

  def button_add_to_cart_click(self, **event_args):
    self.linear_progress_cart.visible = True
    self.spacer_bottom.visible = True
    self.button_add_to_cart.visible = False
    
    try:
      task = anvil.server.call_s('launch_add_to_cart_task', self.item, self.locale)

      popup = AddFramePopup(locale=self.locale)
      add_frame = alert(content=popup, large=True, buttons=[])
      if add_frame is None:
        add_frame = False
      
      while task.is_completed() is False:
        waitHere = 1
      
      # Получаем результат: variant_id, anvil_id
      variant_id, anvil_id = task.get_return_value()
      
      print(f"Received variant_id: {variant_id}, anvil_id: {anvil_id}")
      
      # Отправляем postMessage родительскому окну для добавления в корзину
      send_add_to_cart(variant_id, anvil_id, add_frame)
      
      # Показываем сообщение об успехе
      alert("Product added to cart successfully!", title="Success")
      
    except Exception as e:
      print(f"Error adding to cart: {e}")
      alert(f"Failed to add product to cart: {str(e)}", title="Error")
    
    finally:
      self.button_add_to_cart.visible = True
      self.linear_progress_cart.visible = False
      self.spacer_bottom.visible = False

    