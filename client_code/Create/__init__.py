from ._anvil_designer import CreateTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
from anvil.tables import app_tables

import anvil.js
from anvil.js import window, get_dom_node, call_js

MAX_MB_IMG = 15
WH_IMG = 625
CARD_WIDTH = '360px'


class Point():
  def __init__(self, x, y, rad, op_id):
    self.x = x
    self.y = y
    self.rad = rad
    self.op_id = op_id


class Create(CreateTemplate):
  def __init__(self, **properties):
    # Initialize Anvil components
    self.init_components(**properties)

    # === Register JS bridges (universal method) ===
    try:
      anvil.js.call_js("anvil.callables.set", "set_canvas_ref", self.set_canvas_ref)
      anvil.js.call_js("anvil.callables.set", "file_loader_1_change", self.file_loader_1_change)
      anvil.js.call_js("anvil.callables.set", "button_create_click", self.button_create_click)
      print("✅ JS callables registered via anvil.callables.set")
    except Exception as e:
      print("⚠️ Fallback registration:", e)
      window.set_canvas_ref = self.set_canvas_ref
      window.file_loader_1_change = self.file_loader_1_change
      window.button_create_click = self.button_create_click

    # === Initialize state ===
    self.locale = "en"
    self.img = None
    self.canvas_1 = None
    self.brush_size = 10
    self.mvRatio = 1
    self.zoom = 1
    self.dz = 0
    self.sx = self.sy = self.dx = self.dy = 0
    self.erase_mode = False
    self.enhance_mode = False
    self.pointer_xy = None
    self.erase_points = []
    self.enhance_points = []
    self.curr_op_id = 0
    self.ops_history = []
    self.cvsW = 300

    # Detect mobile
    if hasattr(window.navigator, "userAgentData") and window.navigator.userAgentData is not None:
      platform = window.navigator.userAgentData.platform
    else:
      platform = window.navigator.userAgent
    self.is_mobile = any(p in platform for p in ["Android", "iPhone", "iPad", "iOS"])

    print("✅ Create form initialized. Waiting for canvas connection...")

  # === JS bridge: receive canvas reference ===
  def set_canvas_ref(self, js_canvas):
    try:
      self.canvas_1 = anvil.js.wrap_dom_element(js_canvas)
      print("🎨 Canvas connected successfully:", self.canvas_1)
    except Exception as e:
      print("❌ Failed to connect canvas:", e)

  # === File upload ===
  def file_loader_1_change(self, file, **event_args):
    print("📁 File received:", file)
    self.file_loaded(file)

  def file_loaded(self, file):
    if file is None:
      return
    if file.length < MAX_MB_IMG * 1024 * 1024:
      self.img = file
      print("🖼️ Image loaded successfully")
      if self.canvas_1:
        self.drawCanvas()
    else:
      alert(f"Max size is {MAX_MB_IMG} MB", title="File too large")

  # === Main button ===
  def button_create_click(self, **event_args):
    print("🎯 Button 'Create Artwork' clicked")
    if not self.img:
      alert("Please upload an image first!")
      return
    alert("Simulating artwork creation... (you can call anvil.server.call here)")

  # === Draw something on canvas ===
  def drawCanvas(self):
    if not self.canvas_1:
      print("⚠️ Canvas not connected yet")
      return

    ctx = self.canvas_1.getContext("2d")
    ctx.fillStyle = "#fafafa"
    ctx.fillRect(0, 0, self.canvas_1.width, self.canvas_1.height)
    ctx.beginPath()
    ctx.arc(self.canvas_1.width / 2, self.canvas_1.height / 2, 120, 0, 6.283)
    ctx.fillStyle = "#FFD48A"
    ctx.fill()
    ctx.fillStyle = "#000"
    ctx.font = "16px Inter"
    ctx.textAlign = "center"
    ctx.fillText("Your uploaded image", self.canvas_1.width / 2, self.canvas_1.height / 2 + 150)
    print("🖌️ Canvas drawn successfully.")