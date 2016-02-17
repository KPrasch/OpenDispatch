from hendrix.deploy.base import HendrixDeploy
from txsockjs.factory import SockJSResource
from hendrix.contrib.async.resources import MessageHandlerProtocol
from hendrix.facilities.resources import NamedResource
from twisted.internet.protocol import Factory

message_resource = NamedResource("twitter-dispatches")
message_resource.putChild("dispatch-stream", SockJSResource(Factory.forProtocol(MessageHandlerProtocol)))

deployer = HendrixDeploy(options={"settings": "settings"})
deployer.resources.append(message_resource)
deployer.run()

