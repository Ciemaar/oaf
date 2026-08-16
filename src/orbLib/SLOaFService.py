import sys

from twisted.internet import reactor
from twisted.web import resource, server

import db

from . import MailOaf, OaF, SLOaf

MAIL_SERVER = ""
MAIL_USER = ""
MAIL_PASSWORD = ""

root = resource.Resource()
# root.putChild('',HomePage())
oafRoot = OaF.OafServer(OaF.System)

slIndyMonitor = OaF.System("SL Indy")

oafRoot.putNotifier("SLIndy", SLOaf.SLNotifier(slIndyMonitor))
oafRoot.putSystem("SLIndyMonitor", slIndyMonitor)
oafRoot.putSystem("RedBlackTest", OaF.GoalSystem("RedBlackTest", 500))
oafRoot.putSystem("IMAPtest", MailOaf.IMAPMailMonitor(MAIL_SERVER, MAIL_USER, MAIL_PASSWORD))
oafRoot.putSystem("POP3test", MailOaf.POP3MailMonitor(MAIL_SERVER, MAIL_USER, MAIL_PASSWORD))

slSub = OaF.ScaledSubServer("Second Life systems", oafRoot, OaF.CountSystem, 1)

slSub.putSystem("shop", OaF.CountSystem("Areum Shop Counter", 2))
slSub.putSystem("office", OaF.CountSystem("Pi Office Counter", 2))
oafRoot.putSystem("slsystems", slSub)
oafRoot.putSystem("sldev", SLOaf.SLServer("Second Life Dev"))

from sqlalchemy import select
from sqlalchemy.exc import OperationalError

try:
    for user in db.Session.scalars(select(db.SLAvatar)).all():
        print(("SLAvatar %s" % (user.avname)))
        # user.restoreRunVars()
        userServer = user.getServer()
        oafRoot.putSystem(user.avname, userServer)
        for oaf in user.oafs:
            print("placing " + str(oaf.OafName))
            # must place before init because update is called in init and changes
            # the system name to that of the currently active systems
            oafResource = oaf.getOaf()
            userServer.putSystem(oaf.OafName, oafResource)

    print("Database load complete")
except OperationalError as e:
    print("Warning: Database tables are missing. Skipping user load.")
    print(f"Details: {e}")
    print('To initialize the database, you can run: python -c "import db; db.Base.metadata.create_all(db.engine)"')

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
