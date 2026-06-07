import wx  # type: ignore
from twisted.internet import wxreactor
from twisted.internet.error import CannotListenError
from twisted.web import resource, server

wxreactor.install()

from orbLib import OaF

from .TrayIcon import TrayIcon


class SledApp(wx.App):
    def __init__(self, oafRoot):
        self.oafRoot = oafRoot
        super(SledApp, self).__init__()

    def OnInit(self):
        self.sysIcon = TrayIcon(self)
        self.oafRoot.putNotifier("tray", self.sysIcon)
        return True


def main():
    from twisted.internet import reactor

    root = resource.Resource()

    oafRoot = OaF.OafServer(OaF.System)
    # http://localhost:8000/oaf
    # oafRoot.putSystem("WilhelmPickle", OaF.PickledSystem("http://localhost8000/oaf/pickle",oafRoot))
    # orbRoot.putNotifier("sled", SerialIndyNotifier(sys.argv[1]))

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


if __name__ == "__main__":
    main()
