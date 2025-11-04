from ._anvil_designer import CreateTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..Creation import Creation

import time
import anvil.js
from anvil.js import get_dom_node, call_js
from anvil.js.window import navigator

MAX_MB_IMG = 15
WH_IMG = 625
CARD_WIDTH = '360px'  

class Point():
  def __init__(self,x,y,rad,op_id):
    self.x = x
    self.y = y
    self.rad = rad
    self.op_id = op_id

class Create(CreateTemplate):
  def __init__(self, **properties):
    url_params = anvil.js.call_js('getUrlParams')
    self.locale = url_params.get('locale', 'en')
    self.current_step = 1  # Текущий этап: 1, 2 или 3
    self.brush_size = 10
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Состояние
    self.locale = "en"
    self.img = None
    self.mvRatio = 1
    self.resetMoveAndZoom()  
    self.cvsW = 300

    print("✅ Create initialized (awaiting canvas)")

  # ====== JS → Python мост через anvil.call(...) ======

  @anvil.js.callable
  def set_canvas_ref(self, js_canvas):
    """Получаем canvas из HTML и сохраняем ссылку"""
    try:
      # Если пришёл "сырой" DOM-элемент — оборачиваем
      if not hasattr(js_canvas, "getContext"):
        js_canvas = anvil.js.wrap_dom_element(js_canvas)
      self.canvas_1 = js_canvas
      print("🎨 Canvas connected successfully.")
      self.drawCanvas()
    except Exception as e:
      print("❌ Canvas init error:", e)

  @anvil.js.callable
  def file_loader_1_change(self, file, **event_args):
    """Получаем загруженный файл из HTML input"""
    try:
      print("📁 File received:", file)
      self.file_loaded(file)
    except Exception as e:
      print("❌ file_loader_1_change error:", e)

  @anvil.js.callable
  def button_create_click(self, **event_args):
    """Нажатие Download / Create — вызывается из HTML"""
    print("🚀 Starting artwork creation...")
    if not self.img:
      alert("Please upload an image first!")
      return
    try:
      # Здесь твоя прежняя логика — параметры генерации
      speedText = "very fast"
      effectIntensity = 2
      effectType = "clahe"
      noMask = True
      mask_img = None
      cloth = False
      discDiam = 400

      # subRect — как раньше (если надо — доработаем позже)
      zoom = self.zoom + self.dz
      left = round(self.sx + self.dx)
      top = round(self.sy + self.dy)
      right = left + int(self.minWH * zoom)
      bot = top + int(self.minWH * zoom)
      subRect = (left, top, right, bot)

      cropped_img = self.get_cropped_img()

      paramsDict = {
        "speedText": speedText,
        "effectType": effectType,
        "effectIntensity": effectIntensity,
        "cloth": cloth,
        "noMask": noMask,
        "subRect": subRect,
        "discDiam": discDiam
      }

      print("📡 Calling backend...")
      row = anvil.server.call('create', cropped_img, paramsDict, mask_img, getattr(self.img, "name", "uploaded.jpg"))
      print("✅ Product created ssuccessfully in Shopify!")
      alert("Product created successfully!")

      # Если хочешь — здесь можно показать превью / добавить в список
      # comp = Creation(locale=self.locale, item=row)

    except Exception as e:
      print("❌ Error:", e)
      alert("Server is currently unreachable. Please try again soon.")

  # ====== Клиентская логика работы с картинкой ======

  def file_loaded(self, file):
    if not file:
      return
    if button == 2 and self.zooming:
      self.zooming = False
      self.save_zoom_canvas((y-self.zys)/500)
      self.drawCanvas()
    if button != 2 and self.dragging:
      self.dragging = False
      if not self.erase_mode and not self.enhance_mode:
        self.move_canvas(x,y)
      self.drawCanvas()

  #mouse leave
  def canvas_1_mouse_leave(self, x, y, **event_args):
    self.pointer_xy = None
    if self.dragging:
      self.dragging = False
      if not self.erase_mode and not self.enhance_mode:
        self.move_canvas(x,y)      
    if self.zooming:
      self.zooming = False
      self.save_zoom_canvas((y-self.zys)/500)
    self.drawCanvas()

  def canvas_1_mouse_move(self, x, y, **event_args):
    if self.img is None:
      return

    self.img = file
    print("🖼️ Image loaded successfully")

    if self.canvas_1:
      self.drawCanvas()

  def button_reset_mask_click(self, **event_args):
    self.erase_points = []
    self.enhance_points = []
    self.drawCanvas()

  def refresh_edit_mode(self):
    self.button_mask_eraser.foreground = 'theme:Black' if self.erase_mode else ''
    self.button_mask_enhancer.foreground = 'theme:Black' if self.enhance_mode else ''
    self.button_drag.foreground = '' if self.enhance_mode or self.erase_mode else 'theme:Black'
    if self.erase_mode or self.enhance_mode:
      self.canvas_1.role = 'canvas-none'
    else:
      print("⚠️ Canvas not ready yet — skipping draw.")

  def drawCanvas(self):
    """Простая отрисовка-заглушка: круг + подпись.
       Реальный crop/zoom/drag добавим отдельным шагом."""
    if not self.canvas_1:
      print("⚠️ Canvas not connected yet.")
      return

    try:
      ctx = self.canvas_1.getContext("2d")
      ctx.clearRect(0, 0, self.canvas_1.width, self.canvas_1.height)

      if not self.img:
        # Placeholder до загрузки
        ctx.fillStyle = "#f3f3f3"
        ctx.fillRect(0, 0, self.canvas_1.width, self.canvas_1.height)
        ctx.fillStyle = "#777"
        ctx.font = "16px Inter"
        ctx.textAlign = "center"
        ctx.fillText("Upload your image", self.canvas_1.width / 2, self.canvas_1.height / 2)
        return

      # Пока просто рисуем «рамку»
      ctx.fillStyle = "#FFD48A"
      ctx.beginPath()
      ctx.arc(self.canvas_1.width / 2, self.canvas_1.height / 2, 120, 0, 6.283)
      ctx.fill()
      ctx.fillStyle = "#000"
      ctx.font = "16px Inter"
      ctx.textAlign = "center"
      ctx.fillText("Your uploaded image", self.canvas_1.width / 2, self.canvas_1.height / 2 + 150)
      print("🖌️ Canvas drawn successfully.")
    except Exception as e:
      print("❌ drawCanvas error:", e)

  def get_cropped_img(self):
    """Если используешь Anvil-Canvas API на клиенте — можно кропнуть здесь.
       Сейчас возвращаем исходный файл, чтобы не блокировать сценарий.
       (Позже добавим реальный crop из HTML5 canvas → BlobMedia → Python)"""
    return self.img