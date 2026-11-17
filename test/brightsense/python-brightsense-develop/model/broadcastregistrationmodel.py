import ujson
from configuration import Configuration


class BroadcastRegistrationModel:
  
    def __init__(self, client_id: str, ip: str, mac: str, type: str, method: str):
        self._client_id = client_id
        self._type = type
        self._ip = ip
        self._mac = mac
        self._method = method
    
    def getIP(self):
        return self._ip
    
    def setIP(self, ip):
        self._ip = ip

    ip = property(getIP, setIP)

    def getClientID(self):
        return self._client_id
    
    def setClientID(self, client_id):
        self._client_id = client_id

    client_id = property(getClientID, setClientID)

    def getMAC(self):
        return self._mac
    
    def setMAC(self, mac):
        self._mac = mac

    mac = property(getMAC, setMAC)

    def getType(self):
        return self._type
    
    def setType(self, type):
        self._type = type

    type = property(getType, setType)

    def getMethod(self):
        return self._method

    def setMethod(self, method):
        self._method = method

    method = property(getMethod, setMethod)

    def toDict(self):
        return { 'client_id': self._client_id, 'mac': self._mac, 'ip': self._ip , "type": self._type, "version": Configuration.FRAMEWORK_VERSION, "method": self._method}

    def toJSON(self) -> str:
        data = self.toDict()
        return ujson.dumps(data)
    