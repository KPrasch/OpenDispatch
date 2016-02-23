from hendrix.deploy.base import HendrixDeploy
from txsockjs.factory import SockJSResource
from hendrix.contrib.async.resources import MessageHandlerProtocol
from hendrix.facilities.resources import NamedResource
from twisted.internet.protocol import Factory

dispatch_resource = NamedResource("twitter-dispatches")
dispatch_resource.putChild("incidents", SockJSResource(Factory.forProtocol(MessageHandlerProtocol)))

message_resource = NamedResource("twilio-stream")
message_resource.putChild("responder", SockJSResource(Factory.forProtocol(MessageHandlerProtocol)))

deployer = HendrixDeploy(options={"settings": "settings"})
deployer.resources.append(dispatch_resource)
deployer.resources.append(message_resource)
deployer.run()

