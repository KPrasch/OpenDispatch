from hendrix.deploy.base import HendrixDeploy
from txsockjs.factory import SockJSResource
from hendrix.contrib.async.resources import MessageHandlerProtocol
from hendrix.facilities.resources import NamedResource
from twisted.internet.protocol import Factory
import logging
import datetime

logger = logging.getLogger('django')

dispatch_resource = NamedResource("twitter-dispatches")
dispatch_resource.putChild("incidents", SockJSResource(Factory.forProtocol(MessageHandlerProtocol)))

message_resource = NamedResource("twilio-stream")
message_resource.putChild("responder", SockJSResource(Factory.forProtocol(MessageHandlerProtocol)))

deployer = HendrixDeploy(options={"settings": "settings"})
deployer.resources.append(dispatch_resource)
deployer.resources.append(message_resource)
logger.info("Starting Hendrix at %s" % str(datetime.datetime.now()))


from apps.collect.views import stream_twitter
# Do once on Django startup. Let's do Auth here too?
stream_twitter()

deployer.run()



