import json

class CommandModel:
    sensor_id: int
    cliend_id: str
    command: str
    state: str

    def __init__(self, sensor_id: int, client_id: str, command: str, state: str):
        self.cliend_id = client_id
        self.sensor_id = sensor_id
        self.command = command
        self.state = state
    
    def fromJSON(self, text: str):
        return json.loads(text)

