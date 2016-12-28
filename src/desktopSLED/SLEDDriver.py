from __init__ import SledApp

from twisted.internet.error import CannotListenError
import  twisted.web 
import twisted.internet

from orbLib import OaF


if __name__=="__main__":
    import twisted.internet 
    root =twisted.web.resource.Resource()

    oafRoot=OaF.OafServer(None)
     
    root.putChild("sled",oafRoot)
    
    site = twisted.web.server.Site(root)
        
    sledApp = SledApp(oafRoot)

    print "Starting main loop"
    huntingPort=True
    port=80000
    while(huntingPort):
        try:
            twisted.internet.reactor.listenTCP(port,site)
            huntingPort=False
        except CannotListenError:
            port+=1
    print "Web Interface at http://localhost:%d/sled"%port 
    twisted.internet.reactor.registerWxApp(sledApp)
    twisted.internet.reactor.run()
