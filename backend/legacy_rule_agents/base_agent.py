from threading import Thread

class BaseAgent:
  def __init__(self, name):
    self.name = name
    self.coordinator = None
    self.running = False
    self.thread = None

  def set_coordinator(self, coordinator):
    self.coordinator = coordinator

  def start(self):
    self.running = True
    self.thread = Thread(target=self.run)
    self.thread.daemon = True
    self.thread.start()

  def stop(self):
    self.running = False
    if self.thread:
      self.thread.join(timeout=5)

  def send_message(self, target, message_type, payload):
    if self.coordinator:
      self.coordinator.send_message(self.name, target, message_type, payload)

  def receive_message(self, message):
    # To be implemented by subclasses
    pass

  def run(self):
    # To be implemented by subclasses
    pass
