import sys

from twisted.internet import reactor
from twisted.web import resource, server, xmlrpc

import OaF
import exampleForm
from OaF import PageMonitor

#import xmlrpclib

PRIMARY=1
SECONDARY=2
ATTACHMENT=3
TEMPORB=4

class SLNotifier(OaF.Notifier):
    def __init__(self,rptSystem=None):
        OaF.Notifier.__init__(self,rptSystem)
        self.xmlProxy=xmlrpc.Proxy("http://xmlrpc.secondlife.com/cgi-bin/xmlrpc.cgi")
        self.rptSystem=rptSystem
    def setState(self,color,blink,message,level,status):
        self.color=self.colorToVector(color)
        self.blink=blink
        self.message=message
        self.level=level
        self.status=status
        
        if(hasattr(self,"SLChannel")):
            #print "sending on: "+self.SLChannel

            #xmlrpclib.ServerProxy("http://xmlrpc.secondlife.com/cgi-bin/xmlrpc.cgi").llRemoteData(self.SLChannel,'[%d,%d,"%s","%s","%s",%d]'%(self.color,self.blink,self.message,self.status,self.systemName,self.level),self.color)
            #xmlrpclib.ServerProxy("http://xmlrpc.secondlife.com/cgi-bin/xmlrpc.cgi").llRemoteData(Channel=self.SLChannel,StringValue='[%d,%d,"%s","%s","%s",%d]'%(self.color,self.blink,self.message,self.status,self.systemName,self.level),IntValue=self.color)
            #print xmlrpc.Proxy("http://xmlrpc.secondlife.com/cgi-bin/xmlrpc.cgi").callRemote("llRemoteData",Channel=self.SLChannel,StringValue='[%d,%d,"%s","%s","%s",%d]'%(self.color,self.blink,self.message,self.status,self.systemName,self.level),IntValue=self.color)
            
            self.xmlProxy.callRemote("llRemoteData",{"Channel":self.SLChannel,"StringValue":self._SLCSV(),"IntValue":42}) \
                .addErrback(self.setStateFailed).addCallback(self.setStateSuccess)
    def _SLCSV(self):
            return '%s,%d,%s,%f,"%s"'%(self.color,self.blink,self.status,self.level,self.message)
    def colorToVector(self,color):
        return "<%f,%f,%f>"%color
    colors={OaF.RED:"<1.0,0.0,0.0>",OaF.GREEN:"<0.0,1.0,0.0>",
            OaF.BLUE:"<0,0,1>",OaF.WHITE:"<1,1,1>",OaF.VIOLET:"<1,0,1>"}
    def render_GET(self,request):
        if(request.getHeader("User-Agent")[0:15]=="Second Life LSL"):
            print "Got SL Request"
            self.SLOrbID=request.getHeader("HTTP_X_SecondLife_Object_Key")
            if(request.args.has_key("channel")):
                self.SLChannel=request.args["channel"][0]
                self.SLType=int(request.args.get("type",(1,))[0])
                print "SLType: %d"%self.SLType
            return self._SLCSV()
        return OaF.Notifier.render_GET(self,request)
    def render_POST(self,request):
        return self.render_GET(self,request)
##    def render_GET(self,request):
    def setStateFailed(self,failure):
        """If a temporary indicator fails wipe out the connection and report status 
        as none, if permanent indicator fails, dump it to reporting system."""        
        failure.trap(xmlrpc.Fault)
        
        if((self.SLType==TEMPORB) and (failure.value.faultCode==1)):
            del self.SLChannel
            print "clearing non-responsive temporary orb"
            if self.rptSystem != None:
                self.rptSystem.message="No Connection"
                self.rptSystem.status="none"
            return failure
        else:
            return OaF.Notifier.setStateFailed(self,failure)
    def setStateSuccess(self,data):
        if data and (self.rptSystem != None):
            #print "data: "+str(data)
            self.rptSystem.message=data["StringValue"]
            self.rptSystem.status="ok"
    def setSLStatus(self,data,status):
        #print "data:  %s  status: %s"%(data,status)
        self.SLLink.message=data
        self.SLLink.status=status

class PrimarySLNotifier(SLNotifier):
    def _SLCSV(self):
        if(hasattr(self,"oaf")and self.oaf.needsConfig):
            return SLNotifier._SLCSV(self)+"\nNeeds Config"
        return SLNotifier._SLCSV(self)   
    def render_POST(self,request):
        if hasattr(self,"oaf"):
            self.oaf.updateFromRequest(request)
        return super(PrimarySLNotifier,self).render_POST(request)

class SLServer(OaF.SubServer):
    """Server with limited options to be sold in as an SL product"""
    def __init__(self,systemName,avuuid=None,oaf=None,watchedUrls=None):
        OaF.SubServer.__init__(self,systemName,oaf,None)
        self.avuuid=avuuid
        self.needsConfig=True

        for type in (OaF.System,OaF.CountSystem,OaF.GoalSystem,OaF.GoalNetworkSystem):
            for x in range(0,4):
                name=type.__name__+str(x)
                self.putSystem(name, type(name))
        for x in range(0,4):
            name="Indy"+str(x)
            self.putNotifier(name, SLNotifier(self))
        self.putNotifier("pickle", OaF.PickleNotifier())
        if(watchedUrls==None):
            watchedUrls=[]
        self.watchedUrls=watchedUrls
        self.monitorCount=0
        self.updatePageMonitors()
        self.configVersion=-1
    def updatePageMonitors(self):
        curr=[]
        for key,system in self.systems.iteritems():
            if isinstance(system,PageMonitor):
                if(system.page not in self.watchedUrls):
                    self.removeSystem(key)
                else:
                    curr.append(system.page)
        for url in self.watchedUrls:
            if(url not in curr):
                self.putSystem("PageMonitor%d"%self.monitorCount, PageMonitor(url))
    def updateFromRequest(self,request):
        if request.args.has_key('config') and int(request.args['config'][0])>self.configVersion:
            self.watchedUrls=request.args.get('watchedUrls',[])[0:4]
            self.configVersion=int(request.args['config'][0])
            self.needsConfig=False
        return self.render_GET(request)

#===============================================================================
#    def restoreTransitiveState(self):
#        """ This is a striped down constructor for calling when getting the Serever
#        back from SQLAlchemy or other storage systems, this was an illconsidered idea"""
#        if(not hasattr(self, "systems")):
#           self.systems={}
#           self.notifiers={}
#        OaF.OafServer.updateState(self)
#===============================================================================
        
class BoundSLOafServer(SLServer):
    def __init__(self,configData,*args,**kwargs):
        super(BoundSLOafServer,self).__init__("loading from db",configData.AVUUID,watchedUrls=[x.url for x in configData.pagemonitors],*args,**kwargs)
        self.db_id = configData.id
        self.configData = configData

class SLOafServer(OaF.OafServer):
    def __init__(self,db_id):
        OaF.OafServer.__init__(self,SLServer)
        self.db_id=db_id
if __name__=="__main__":
    
    root =resource.Resource()
    #root.putChild('',HomePage())
    oafRoot=OaF.OafServer()
    
    
    if(len(sys.argv)>2):        
        ambientMonitor=OaF.System("Ambient Tech",oafRoot)
        oafRoot.putSystem("AmbientMonitor", ambientMonitor)
        oafRoot.putNotifier("orb", OaF.OrbNotifier(sys.argv[2],ambientMonitor))
    else:
        # orbRoot.putSystem("WilhelmPickle", OaF.PickledSystem("http://localhost:8000/orb/pickle",orbRoot))
        pass
        
    slIndyMonitor=OaF.System("SL Indy")
        
    oafRoot.putNotifier("SLIndy", SLNotifier(slIndyMonitor))
    oafRoot.putSystem("SLIndyMonitor", slIndyMonitor)
    oafRoot.putSystem("google", OaF.PageMonitor("http://google.com/"))
    oafRoot.putSystem("yahoo", OaF.PageMonitor("http://yahoo.com/", allowedErrors=("401",)))
    oafRoot.putSystem("litfactory",
                      OaF.PageMonitor("http://localhost:8813/bookstore/Wilson", "Wilhelm Lit", allowedErrors=("405",)))
    oafRoot.putSystem("OAF Main", OaF.PageMonitor("http://localhost:8000/oaf"))
    oafRoot.putSystem("RedBlackTest", OaF.GoalSystem("RedBlackTest",500))
    
    slSub=OaF.ScaledSubServer("Second Life systems",oafRoot,OaF.CountSystem,1)

    slSub.putSystem("shop", OaF.CountSystem("Areum Shop Counter",2))
    slSub.putSystem("office", OaF.CountSystem("Pi Office Counter",2))
    oafRoot.putSystem("slsystems", slSub)
    oafRoot.putSystem("sldev", SLServer("Second Life Dev",oafRoot))
  
    dsexport=OaF.SubServer("dsexport",oafRoot,OaF.ProcessMonitor)
    #dsexport.putChild("fill", OaF.System("phil",dsexport))
    oafRoot.putSystem("dsexport", dsexport)

    oafRoot.putNotifier("pickle", OaF.PickleNotifier())
  
    root.putChild("oaf",oafRoot)
    root.putChild("exform",exampleForm.Simple())
    site = server.Site(root)
    if(len(sys.argv)>1):
        reactor.listenTCP(int(sys.argv[1]),site)
    else:
        reactor.listenTCP(8585,site)
    reactor.run()
    print "Reactor stopped."        