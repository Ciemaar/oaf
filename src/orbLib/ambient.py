import colorsys
from urllib import urlencode

from twisted.web import client

from colors import WHITE
from orbLib.OaF import Notifier, NONE


class OrbNotifier(Notifier):
    def __init__(self, devId, rptSystem=None):
        Notifier.__init__(self, rptSystem)
        self.devId = devId
        self.setState(WHITE, 0, "", NONE, "none")

    def setState(self, color, blink, message, level, status):
        hsvColor = colorsys.rgb_to_hsv(*color)
        if (hsvColor[2] < .1):
            colorCode = 36
        else:
            colorCode = int(hsvColor[0] * 36)
        client.getPage(
            "http://www.myambient.com:8080/java/my_devices/submitdata.jsp?" + \
            urlencode(
                {'devID': self.devId, 'anim': int(blink), 'color': colorCode,
                 'comment': message})) \
            .addErrback(self.setStateFailed).addCallback(self.setStateSuccess)


if __name__ == "__main__":
    root = resource.Resource()
    # root.putChild('',HomePage())
    oafRoot = OafServer()
    # oafRoot.putSystem('name', PageMonitor('https://example.com',oafRoot))
    # oafRoot.putSystem('name1', PageMonitor('https://example.com',oafRoot))
    # oafRoot.putSystem('name2', PageMonitor('https://example.com',oafRoot))
    # oafRoot.putSystem('name3', PageMonitor('https://example.com',oafRoot))
    # oafRoot.putSystem('name4', PageMonitor('https://example.com',oafRoot))

    if (len(sys.argv) > 2):
        oafRoot.putNotifier("orb", OrbNotifier(sys.argv[2]))

    root.putChild("orb", oafRoot)
    root.putChild("exform", exampleForm.Simple)
    site = server.Site(root)

    if (len(sys.argv) > 1):
        reactor.listenTCP(int(sys.argv[1]), site)
    else:
        reactor.listenTCP(8000, site)

    reactor.run()
    print "Reactor stopped."
