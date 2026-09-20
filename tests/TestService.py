import sys

from twisted.internet import reactor
from twisted.web import resource, server

from orbLib import OaF

MAIL_SERVER = ""
MAIL_USER = ""
MAIL_PASSWORD = ""

root = resource.Resource()
# root.putChild('',HomePage())
oafRoot = OaF.OafServer(None)

oafRoot.putSystem("BasicSystem", OaF.System("Basic System"))
oafRoot.putNotifier("BasicNotifier", OaF.Notifier("Basic Notifier"))
oafRoot.putNotifier("JsonNotifier", OaF.JsonNotifier("Json Notifier"))

oafRoot.putSystem("RedBlackTest", OaF.GoalSystem("RedBlackTest", 500))

slSub = OaF.ScaledSubServer("Second Life systems", oafRoot, OaF.CountSystem, 1)

slSub.putSystem("shop", OaF.CountSystem("Areum Shop Counter", 2))
slSub.putSystem("office", OaF.CountSystem("Pi Office Counter", 2))
oafRoot.putSystem("slsystems", slSub)

dsexport = OaF.SubServer("dsexport", oafRoot, OaF.ProcessMonitor)
# dsexport.putChild("fill", OaF.System("phil",dsexport))
oafRoot.putSystem("dsexport", dsexport)

oafRoot.putNotifier("pickle", OaF.PickleNotifier())

root.putChild(b"oaf", oafRoot)  # type: ignore
site = server.Site(root)
if len(sys.argv) > 1:
    reactor.listenTCP(int(sys.argv[1]), site)  # type: ignore
else:
    reactor.listenTCP(8585, site)  # type: ignore
reactor.run()  # type: ignore
print("Reactor stopped.")
