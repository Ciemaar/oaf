import colorsys
from urllib.parse import urlencode

from .colors import WHITE
from .OaF import NONE, Notifier, get_page


class OrbNotifier(Notifier):
    def __init__(self, devId, rptSystem=None):
        Notifier.__init__(self, rptSystem)
        self.devId = devId
        self.setState(WHITE, 0, "", NONE, "none")

    def setState(self, color, blink, message, level, status):
        hsvColor = colorsys.rgb_to_hsv(*color)
        if hsvColor[2] < 0.1:
            colorCode = 36
        else:
            colorCode = int(hsvColor[0] * 36)
        from twisted.internet.defer import ensureDeferred

        async def _do_request():
            try:
                res = await get_page(
                    "http://www.myambient.com:8080/java/my_devices/submitdata.jsp?"
                    + urlencode({"devID": self.devId, "anim": int(blink), "color": colorCode, "comment": message})
                )
                self.setStateSuccess(res)
            except Exception as e:
                self.setStateFailed(e)

        ensureDeferred(_do_request())


if __name__ == "__main__":
    import sys

    from twisted.internet import reactor
    from twisted.web import resource, server

    from . import OaF, exampleForm

    root = resource.Resource()
    # root.putChild('',HomePage())
    oafRoot = OaF.OafServer()
    # oafRoot.putSystem('name', PageMonitor('https://example.com',oafRoot))
    # oafRoot.putSystem('name1', PageMonitor('https://example.com',oafRoot))
    # oafRoot.putSystem('name2', PageMonitor('https://example.com',oafRoot))
    # oafRoot.putSystem('name3', PageMonitor('https://example.com',oafRoot))
    # oafRoot.putSystem('name4', PageMonitor('https://example.com',oafRoot))

    if len(sys.argv) > 2:
        oafRoot.putNotifier("orb", OrbNotifier(sys.argv[2]))

    root.putChild(b"orb", oafRoot)  # type: ignore
    root.putChild(b"exform", exampleForm.Simple())  # type: ignore
    site = server.Site(root)

    if len(sys.argv) > 1:
        reactor.listenTCP(int(sys.argv[1]), site)  # type: ignore
    else:
        reactor.listenTCP(8000, site)  # type: ignore

    reactor.run()  # type: ignore
    print("Reactor stopped.")
