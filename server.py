import sys

from twisted.python import log
from twisted.internet import reactor

from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol


class SomeServerProtocol(WebSocketServerProtocol):
    
    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))

    def onOpen(self):    	
        self.factory.register(self)
        print("Client connected: {0}".format(self.peer))

    def connectionLost(self, reason):
        self.factory.unregister(self)
        print("Client disconnected: {0}".format(self.peer))

    def onMessage(self, payload, isBinary):
        self.factory.communicate(self, payload, isBinary)
        print("Client {0} sending message: {1}".format(self.peer, payload))



class ChatRouletteFactory(WebSocketServerFactory):

    def __init__(self, *args, **kwargs):
        super(ChatRouletteFactory, self).__init__(*args)
        self.clients = []
	
    def register(self, client):
        self.clients.append({ 'client-peer':client.peer, 'client':client })

    def unregister(self, client):
        for c in self.clients:
            if c['client-peer'] == client.peer: self.clients.remove(c)

    def communicate(self, client, payload, isBinary):
        for i,c in enumerate(self.clients):
            if c['client'] == client: 
                id = i
                break
        for c in self.clients:           
            msg = 'Client {0}: {1}'.format(str(id+1), payload.decode('utf-8'))
            c['client'].sendMessage(str.encode(msg))


if __name__ == "__main__":
    log.startLogging(sys.stdout)

    factory = ChatRouletteFactory(u"ws://127.0.0.1:8080")
    factory.protocol = SomeServerProtocol

    reactor.listenTCP(8080, factory)
    reactor.run()