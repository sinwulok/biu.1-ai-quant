from . import BaseAgent, time, datetime, Queue


class AgentCoordinator:
  def __init__(self):
    self.agents = {}
    self.message_queue = Queue()
    self.running = False

  def register_agent(self, agent_name, agent):
    self.agents[agent_name] = agent
    agent.set_coordinator(self)

  def start(self):
    self.running = True
    for agent in self.agents.values():
      agent.start()
    self._process_messages()

  def stop(self):
    self.running = False
    for agent in self.agents.values():
      agent.stop()

  def send_message(self, sender, target, message_type, payload):
    self.message_queue.put({
        'sender': sender,
        'target': target,
        'type': message_type,
        'payload': payload,
        'timestamp': datetime.now()
    })

  def _process_messages(self):
    while self.running:
      if not self.message_queue.empty():
        message = self.message_queue.get()
        if message['target'] in self.agents:
          self.agents[message['target']].receive_message(message)
        elif message['target'] == 'all':
          for agent in self.agents.values():
            agent.receive_message(message)
      time.sleep(0.01)
