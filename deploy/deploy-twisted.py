from twisted.internet import reactor
from twisted.internet.protocol import Factory, Protocol
from txsockjs.factory import SockJSFactory

class HelloProtocol(Protocol):
    def connectionMade(self):
        self.transport.write('hello')
        self.transport.write('how are you?')

    def dataReceived(self, data):
        print data

reactor.listenTCP(8080, SockJSFactory(Factory.forProtocol(HelloProtocol)))
reactor.run()

'''
class GeoJsonProtocol(Protocol):
    def connectionMade(self):
        self.transport.write('open')
        print "open"

    def dataReceived(self, data):
        print data

    def connectionLost(self, reason):
        print "closed"


root = resource.Resource()
root.putChild("twitter-dispatches", SockJSResource(Factory.forProtocol(GeoJsonProtocol)))
site = server.Site(root)

reactor.listenTCP(8080, site)
reactor.run()

'''