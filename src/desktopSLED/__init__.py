import wx
from twisted.internet import wxreactor
wxreactor.install()
from twisted.internet.error import CannotListenError
from twisted.web import resource, server

from TrayIcon import TrayIcon
from orbLib import OaF

class SledApp(wx.App):
    def __init__(self,oafRoot):
        self.oafRoot=oafRoot 
        super(SledApp,self).__init__()
    def OnInit(self):
        self.sysIcon=TrayIcon(self)
        self.oafRoot.putNotifier("tray", self.sysIcon)
        return True

if __name__=="__main__":
    from twisted.internet import reactor
    root =resource.Resource()

    oafRoot=OaF.OafServer(None)
    # http://localhost:8000/oaf
    # oafRoot.putSystem("WilhelmPickle", OaF.PickledSystem("http://localhost8000/oaf/pickle",oafRoot))
    #orbRoot.putNotifier("sled", SerialIndyNotifier(sys.argv[1]))
     
    root.putChild("sled",oafRoot)
    
    site = server.Site(root)
        
    sledApp = SledApp(oafRoot)

    print "Starting main loop"
    huntingPort=True
    port=80000
    while(huntingPort):
        try:
            reactor.listenTCP(port,site)
            huntingPort=False
        except CannotListenError:
            port+=1
    print "Web Interface at http://localhost:%d/sled"%port 
    reactor.registerWxApp(sledApp)
    reactor.run()
