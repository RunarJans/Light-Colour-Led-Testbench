import ubinascii
import machine
import ujson

class SensorDataModel:
    client_id: str
    name: str
    value: int

    def __init__(self, name: str, value: int):
        self.name = name
        self.value = value
        self.client_id = ubinascii.hexlify(machine.unique_id()).decode('utf-8')

    def toDict(self):
        return { 'name': self.name, 'value': self.value, 'clientid': self.client_id }

    def toJSON(self) -> str:
        data = self.toDict()
        return ujson.dumps(data)
