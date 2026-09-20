from twisted.internet.error import CannotListenError

from orbLib import OaF

from .__init__ import SledApp

if __name__ == "__main__":
    from twisted.internet import reactor
    from twisted.web import resource, server

    root = resource.Resource()

    oafRoot = OaF.OafServer(OaF.System)

    root.putChild(b"sled", oafRoot)  # type: ignore

    site = server.Site(root)

    sledApp = SledApp(oafRoot)

    print("Starting main loop")
    huntingPort = True
    port = 80000
    while huntingPort:
        try:
            reactor.listenTCP(port, site)  # type: ignore
            huntingPort = False
        except CannotListenError:
            port += 1
    print("Web Interface at http://localhost:%d/sled" % port)
    reactor.registerWxApp(sledApp)
    reactor.run()  # type: ignore
