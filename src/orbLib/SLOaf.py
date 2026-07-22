import sys
import xmlrpc.client as xmlrpclib  # nosec B411
from io import BytesIO

import defusedxml.xmlrpc

defusedxml.xmlrpc.monkey_patch()

from twisted.internet import reactor
from twisted.web import resource, server
from twisted.web.client import Agent, FileBodyProducer, readBody
from twisted.web.http_headers import Headers

from . import OaF, exampleForm
from .OaF import PageMonitor

PRIMARY = 1
SECONDARY = 2
ATTACHMENT = 3
TEMPORB = 4


class SLNotifier(OaF.Notifier):
    def __init__(self, rptSystem=None):
        OaF.Notifier.__init__(self, rptSystem)
        self.agent = Agent(reactor)
        self.rpc_url = b"http://xmlrpc.secondlife.com/cgi-bin/xmlrpc.cgi"
        self.rptSystem = rptSystem
        self.state = {}

    async def _callRemote(self, method, *args):
        payload = xmlrpclib.dumps(args, methodname=method).encode("utf-8")
        body = FileBodyProducer(BytesIO(payload))
        headers = Headers({b"Content-Type": [b"text/xml"]})

        try:
            response = await self.agent.request(b"POST", self.rpc_url, headers, body)  # type: ignore
            response_body = await readBody(response)
            result = xmlrpclib.loads(response_body.decode("utf-8"))[0][0]
            self.setStateSuccess(result)
        except Exception as e:
            self.setStateFailed(e)

    def setState(self, color, blink, message, level, status):
        self.color = self.colorToVector(color)
        self.blink = blink
        self.message = message
        self.level = level
        self.status = status

        if hasattr(self, "SLChannel"):
            from twisted.internet.defer import ensureDeferred

            ensureDeferred(
                self._callRemote(
                    "llRemoteData",
                    {"Channel": self.SLChannel, "StringValue": self._SLCSV().decode("utf-8"), "IntValue": 42},
                )
            )

    def _SLCSV(self):
        return ('%s,%d,%s,%f,"%s"' % (self.color, self.blink, self.status, self.level, self.message)).encode("utf-8")

    def colorToVector(self, color):
        return "<%f,%f,%f>" % color

    colors = {
        OaF.RED: "<1.0,0.0,0.0>",
        OaF.GREEN: "<0.0,1.0,0.0>",
        OaF.BLUE: "<0,0,1>",
        OaF.WHITE: "<1,1,1>",
        OaF.VIOLET: "<1,0,1>",
    }

    def render_GET(self, request):
        user_agent = request.getHeader(b"User-Agent")
        if user_agent and user_agent[0:15] == b"Second Life LSL":
            print("Got SL Request")
            self.SLOrbID = request.getHeader(b"HTTP_X_SecondLife_Object_Key")
            if b"channel" in request.args:
                self.SLChannel = request.args[b"channel"][0].decode("utf-8")
                self.SLType = int(request.args.get(b"type", (1,))[0])
                print("SLType: %d" % self.SLType)
            return self._SLCSV()
        return OaF.Notifier.render_GET(self, request)

    def render_POST(self, request):
        return self.render_GET(request)

    ##    def render_GET(self,request):
    def setStateFailed(self, failure):
        """If a temporary indicator fails wipe out the connection and report status
        as none, if permanent indicator fails, dump it to reporting system."""

        # Note: In the new async/await architecture, failure might be a direct Exception
        faultCode = getattr(failure, "faultCode", None)

        if (getattr(self, "SLType", None) == TEMPORB) and (faultCode == 1):
            del self.SLChannel
            print("clearing non-responsive temporary orb")
            if self.rptSystem is not None:
                self.rptSystem.message = "No Connection"
                self.rptSystem.status = "none"
            return failure
        else:
            return OaF.Notifier.setStateFailed(self, failure)

    def setStateSuccess(self, data):
        if data and (self.rptSystem is not None):
            # print "data: "+str(data)
            self.rptSystem.message = data["StringValue"]
            self.rptSystem.status = "ok"

    def setSLStatus(self, data, status):
        # print "data:  %s  status: %s"%(data,status)
        self.SLLink.message = data  # type: ignore
        self.SLLink.status = status  # type: ignore


class PrimarySLNotifier(SLNotifier):
    def _SLCSV(self):
        if hasattr(self, "oaf") and self.oaf.needsConfig:  # type: ignore
            return SLNotifier._SLCSV(self) + b"\nNeeds Config"
        return SLNotifier._SLCSV(self)

    def render_POST(self, request):
        if hasattr(self, "oaf"):
            self.oaf.updateFromRequest(request)  # type: ignore
        return super(PrimarySLNotifier, self).render_POST(request)


class SLServer(OaF.SubServer):
    """Server with limited options to be sold in as an SL product"""

    def __init__(self, systemName, avuuid=None, oaf=None, watchedUrls=None):
        OaF.SubServer.__init__(self, systemName, oaf, OaF.System)
        self.avuuid = avuuid
        self.needsConfig = True

        for type in (OaF.System, OaF.CountSystem, OaF.GoalSystem, OaF.GoalNetworkSystem):
            for x in range(0, 4):
                name = type.__name__ + str(x)
                self.putSystem(name, type(name))
        for x in range(0, 4):
            name = "Indy" + str(x)
            self.putNotifier(name, SLNotifier(self))
        self.putNotifier("pickle", OaF.PickleNotifier())
        if watchedUrls is None:
            watchedUrls = []
        self.watchedUrls = watchedUrls
        self.monitorCount = 0
        self.updatePageMonitors()
        self.configVersion = -1

    def updatePageMonitors(self):
        curr = []
        for key, system in list(self.systems.items()):
            if isinstance(system, PageMonitor):
                if system.page not in self.watchedUrls:
                    self.removeSystem(key)
                else:
                    curr.append(system.page)
        for url in self.watchedUrls:
            if url not in curr:
                self.putSystem("PageMonitor%d" % self.monitorCount, PageMonitor(url))
                self.monitorCount += 1

    def updateFromRequest(self, request):
        if b"config" in request.args and int(request.args[b"config"][0]) > self.configVersion:
            self.watchedUrls = [u.decode("utf-8") for u in request.args.get(b"watchedUrls", [])[0:4]]
            self.configVersion = int(request.args[b"config"][0])
            self.needsConfig = False
        return self.render_GET(request)


# ===============================================================================
#    def restoreTransitiveState(self):
#        """ This is a striped down constructor for calling when getting the Serever
#        back from SQLAlchemy or other storage systems, this was an illconsidered idea"""
#        if(not hasattr(self, "systems")):
#           self.systems={}
#           self.notifiers={}
#        OaF.OafServer.updateState(self)
# ===============================================================================


class BoundSLOafServer(SLServer):
    def __init__(self, configData, *args, **kwargs):
        super(BoundSLOafServer, self).__init__(
            "loading from db", configData.AVUUID, watchedUrls=[x.url for x in configData.pagemonitors], *args, **kwargs
        )
        self.db_id = configData.id
        self.configData = configData


class SLOafServer(OaF.OafServer):
    def __init__(self, db_id):
        OaF.OafServer.__init__(self, SLServer)  # type: ignore
        self.db_id = db_id


if __name__ == "__main__":
    root = resource.Resource()
    # root.putChild('',HomePage())
    oafRoot = OaF.OafServer()

    if len(sys.argv) > 2:
        ambientMonitor = OaF.System("Ambient Tech")
        oafRoot.putSystem("AmbientMonitor", ambientMonitor)
        oafRoot.putNotifier("orb", OaF.OrbNotifier(sys.argv[2], ambientMonitor))
    else:
        # orbRoot.putSystem("WilhelmPickle", OaF.PickledSystem("http://localhost:8000/orb/pickle",orbRoot))
        pass

    slIndyMonitor = OaF.System("SL Indy")

    oafRoot.putNotifier("SLIndy", SLNotifier(slIndyMonitor))
    oafRoot.putSystem("SLIndyMonitor", slIndyMonitor)
    oafRoot.putSystem("google", OaF.PageMonitor("http://google.com/"))
    oafRoot.putSystem("yahoo", OaF.PageMonitor("http://yahoo.com/", allowedErrors=("401",)))
    oafRoot.putSystem("litfactory", OaF.PageMonitor("http://localhost:8813/bookstore/Wilson", allowedErrors=("405",)))
    oafRoot.putSystem("OAF Main", OaF.PageMonitor("http://localhost:8000/oaf"))
    oafRoot.putSystem("RedBlackTest", OaF.GoalSystem("RedBlackTest", 500))

    slSub = OaF.ScaledSubServer("Second Life systems", oafRoot, OaF.CountSystem, 1)

    slSub.putSystem("shop", OaF.CountSystem("Areum Shop Counter", 2))
    slSub.putSystem("office", OaF.CountSystem("Pi Office Counter", 2))
    oafRoot.putSystem("slsystems", slSub)
    oafRoot.putSystem("sldev", SLServer("Second Life Dev", oaf=oafRoot))

    dsexport = OaF.SubServer("dsexport", oafRoot, OaF.ProcessMonitor)
    # dsexport.putChild("fill", OaF.System("phil",dsexport))
    oafRoot.putSystem("dsexport", dsexport)

    oafRoot.putNotifier("pickle", OaF.PickleNotifier())

    root.putChild(b"oaf", oafRoot)  # type: ignore
    root.putChild(b"exform", exampleForm.Simple())  # type: ignore
    site = server.Site(root)
    if len(sys.argv) > 1:
        reactor.listenTCP(int(sys.argv[1]), site)  # type: ignore
    else:
        reactor.listenTCP(8585, site)  # type: ignore
    reactor.run()  # type: ignore
    print("Reactor stopped.")
