import colorsys
import marshal
import sys
import time
from urllib import urlencode

from twisted.internet import reactor, task
from twisted.web import resource, server, client, error

import exampleForm
from colors import *

NONE=0
DEFAULT=1
INFO=2
WARNING=3
ALERT=4
CRITICAL=5
class System(resource.Resource,object):
    statusList={"none":(NONE,WHITE,0),"ok":(DEFAULT,GREEN,0),"working":(INFO,BLUE,5),
              "success":(INFO,GREEN,0),"failure":(WARNING,RED,0),"error":(ALERT,RED,7)}
    def render_POST(self,request):
        if(request.args.has_key('ack')):
            self.level=NONE
            self.oaf.statusChange(self)
        return self.render_GET(request)
    def render_GET(self,request):
        if(request.args.has_key('status') and (request.args['status'][0]!='')):
           if((request.args.has_key('message')) and (request.args['message'][0]!='')):
              self.message=request.args['message'][0]
           else:
               self.message=self.systemName
           self.status=request.args['status'][0]              
       
        historyTable='<table>'
        for line in self.history:
            historyTable+='<tr><td>%s</td><td>%s</td><td>%s</td></tr>'%(line[0],line[1],time.strftime("%a %d %b %Y %H:%M:%S",line[2]))
        historyTable+='</table>'
           
        return str("""<html><body bgcolor="%s">OAF System:"""%getWebColor(self.color) \
                +historyTable+self.systemName+self.form%request.uri+"""<a href=".">parent oaf</a></body></html>""")
#        return ("""<html><body bgcolor="%s">OAF System:"""%getWebColor(self.color) \
#                +historyTable+self.systemName+self.form%request.uri+"""<a href=".">parent oaf</a></body></html>""").encode('utf-8')
    def setStatus(self,value):    
        self.statusTime=time.localtime()
        self.history=[(value,self.message,self.statusTime)]+self.history[0:12]
        
        #Keeps the Acknowledgement until status changes, resetting 
        # the level to the new status
        if(value==self._status):
            return
        
        settings=self.statusList.get(value,(NONE,WHITE,0))
        self.level=settings[0]
        self.color=settings[1]
        self.blink=settings[2]
        self._status=value
        if(hasattr(self,"oaf")):
            self.oaf.statusChange(self)
    def getStatus(self):
        return self._status
    status=property(getStatus,setStatus,doc="System Status")
    def __init__(self,systemName):
        resource.Resource.__init__(self)
        self.history=[]
        self._formHeader = """
        <form ACTION="%s" METHOD="POST" ENCTYPE="application/x-www-form-urlencoded">
                 <input TYPE="SUBMIT" NAME="ack" VALUE="Acknowledge">
                 """
        self._formBody="""Status: <select NAME="status"><option></option>"""
        for status in self.statusList.keys():
            self._formBody+="<option>%s</option>"%status        
        self._formBody+="""</select><BR>
Message: <input TYPE="TEXT" NAME="message" SIZE="25">"""
        self._formFooter="""<BR><input TYPE="SUBMIT" NAME="name_submit" VALUE="Submit">
        </FORM>
        """
        self.form=self._formHeader+self._formBody+self._formFooter
        self.message=systemName
        print "initting "+systemName
        self.systemName=systemName;
        
        self._status=""
        self.status="none"
class OafServer(object,resource.Resource):
    def __init__(self,defaultSystemType=System):
        resource.Resource.__init__(self)
        self.systems={}
        self.notifiers={}
        self.controllingSystem=None
        self.updateState()
        self.defaultSystemType=defaultSystemType

    def render_GET(self,request):
        #print "called render"
        head="""<html><head><title>OAF status: %s system: %s</title></head><body bgcolor="%s">"""%(self.status,self.systemName,getWebColor(self.color))
        currState =""" status: %s system: %s message: %s <br/>color: %s blink: %d<br/>OAF Server Page"""% \
            (self.status,self.systemName,self.message,str(self.color),self.blink)
        systemTable="<table>"
        systemPaths=self.systems.keys()
        systemPaths.sort()
        for path in systemPaths:
            currSystem=self.systems[path]
            systemTable+="""<tr bgcolor="white"><td><a href="%s/%s">%s</a></td><td bgcolor="%s">%s</td><td>%s</td><td>%s</td></tr>"""%(request.uri,path,currSystem.systemName,getWebColor(currSystem.color),currSystem.status,currSystem.message,time.strftime("%a %d %b %Y %H:%M:%S",currSystem.statusTime))
        systemTable+="</table>"
        foot="</body></html>"
        request.setHeader("Content-type", 'text/html; charset=UTF-8')
        return (head+currState+systemTable+foot).encode('utf-8')
    def putSystem(self,path,system):
        #print "adding "+str(system.__class__)
        if(not hasattr(system,"oaf")):
            system.oaf=self        
        self.systems[path]=system
        self._statusChange(system)
        self.putChild(path, system)
    def removeSystem(self,path):
        system=self.systems[path]
        del system.oaf
        del self.systems[path]
    
    def putNotifier(self,path,notifier):
        if(notifier==None):
            if(path in self.notifiers):
                del self.notifiers[path]
            if(path in self.children):
                del self.children[path]
        else:
            self.notifiers[path]=notifier
            notifier.setState(self.color,self.blink,self.systemName+": "+self.message,self.level,self.status)
            self.putChild(path,notifier)
    def getChild(self,path,request):
        #print "called getChild"+path
        if(path==""):
            return self
        if(path in self.children):
            return self.children[path]
        self.putSystem(path, self.defaultSystemType(path,self))
        return self.getChild(path, request)
    def updateState(self):
        self.color=WHITE
        self.message=""
        self.blink=0
        self.level=-1
        self.systemName=""
        self.status=""
        for currSystem in self.systems.values():
            self._statusChange(currSystem)
        self.setIndys()
    def _statusChange(self,system):        
        """Private updater of status information, returns true if status actually changed"""
        effectiveSystemLevel=system.level*self._getLevelScaler(system)
        if(system==self.controllingSystem):
            self.level=effectiveSystemLevel
            self.controllingSystem=None #prevent infinate loop
            self.updateState()
            return False #Called within updateState
        if(effectiveSystemLevel<self.level):
            return False
        self.statusTime=system.statusTime
        self.controllingSystem=system
        self.color=system.color
        self.message=system.message
        self.blink=system.blink
        self.level=effectiveSystemLevel
        self.systemName=system.systemName
        self.status=system.status
        return True
    def _getLevelScaler(self,system):
        return 1
    def statusChange(self,system):
        if self._statusChange(system):
            self.setIndys()
    def setIndys(self):
        print "setting color "+str(self.color) + " from system "+self.systemName
        for notifier in self.notifiers.values(): 
            notifier.setState(self.color,self.blink,self.systemName+": "+self.message,self.level,self.status)

class Notifier(resource.Resource,object):
    "A basic notifier class which optionally takes a System and reports failures to it, *DOES NOT IMPLEMENT setState"
    def __init__(self,rptSystem=None):
        resource.Resource.__init__(self)   
        self.rptSystem=rptSystem
    def setStateFailed(self,failure):
        if(self.rptSystem!=None):
            self.rptSystem.message="Unable to set state for "+self.__class__.__name__+str(failure)
            self.rptSystem.status="error"
        return failure
    def setStateSuccess(self,data):
        if(self.rptSystem!=None):
            self.rptSystem.message="State set sucessfully"
            self.rptSystem.status="ok"
    def render_GET(self,request):
        request.setResponseCode(415)
        return "No Representation<br/>Internal state:<br/>%s"%(str(self.state))
class OrbNotifier(Notifier):
    def __init__(self,devId,rptSystem=None):
        Notifier.__init__(self,rptSystem)
        self.devId=devId
        self.setState(WHITE,0,"",NONE,"none")  
    def setState(self,color,blink,message,level,status):
        hsvColor=colorsys.rgb_to_hsv(*color)
        if(hsvColor[2]<.1):
            colorCode=36
        else:
            colorCode=int(hsvColor[0]*36)
        client.getPage("http://www.myambient.com:8080/java/my_devices/submitdata.jsp?"+ \
           urlencode({'devID':self.devId,'anim':int(blink),'color':colorCode,'comment':message}))\
            .addErrback(self.setStateFailed).addCallback(self.setStateSuccess)
##    def render_GET(self,request):
class PickleNotifier(resource.Resource):
    def __init__(self):
        resource.Resource.__init__(self)   
        self.setState(WHITE,0,"",NONE,"none")       
    def setState(self,color,blink,message,level,status):
        self.state={"color":color,"blink":blink,"message":message,"level":level,"status":status}
        #print "set state"+str(self.state)
    def render_GET(self,request):
        return marshal.dumps(self.state)
class SubServer(OafServer):          
    def __init__(self,systemName,oaf=None,defaultSystemType=System):
        self.message=systemName
        print "initting "+systemName
        if(oaf!=None):
            self.oaf=oaf
        self.status="none"
        self.statusTime=time.localtime()
        OafServer.__init__(self)
        self.systemName=systemName
        self.defaultSystemType=defaultSystemType
    def setIndys(self):
        """On a SubServer, sets all the notifiers with the super of this method 
        and also sets its parent Oaf as a System would"""
        OafServer.setIndys(self)
        if(hasattr(self,"oaf")):
           self.oaf.statusChange(self)
class ScaledSubServer(SubServer):
    def __init__(self,systemName,oaf,defaultSystemType,scaling,devID=None):
        self.scaling=scaling
        SubServer.__init__(self,systemName,oaf,defaultSystemType)    
    def _getLevelScaler(self,system):
        return self.scaling  
class CountSystem(System):
    statusList={"innactive":(NONE,WHITE,0),
                "active":(DEFAULT,GREEN,0),
                "triggered":(WARNING,VIOLET,5)}

    def __init__(self,systemName,threshold=3):
        System.__init__(self,systemName)
        self._count=None
        self._threshold=threshold
        self._formBody="""Message: <INPUT TYPE="TEXT" NAME="message" SIZE="25"><br>
                        Count: <INPUT TYPE="TEXT" NAME="count" SIZE="25">"""
    def render_GET(self,request):
        if(request.args.has_key('count')):
            self.count=request.args['count'][0]
        if(request.args.has_key('threshold')):
            self.threshold=int(request.args['threshold'][0])
        self.form=self._formHeader+self._formBody+"""<br>Threshold:  <input type="TEXT" name="threshold" value="%d">"""%self.threshold+self._formFooter
        return System.render_GET(self,request)
    def setCount(self,value):
        newCount=int(value)
        if (newCount==self._count):
            return
        
        self._count=newCount        
        self.updateStatus()
    def getCount(self):
        return self._count    
    count=property(getCount,setCount,doc="Count of whatever is being counted")
    def setThreshold(self,value):
        if(value!=self._threshold):
            self._threshold=value    
            self.updateStatus()    
    def getThreshold(self):
        return self._threshold    
    threshold=property(getThreshold,setThreshold,doc="Threshold for triggering")
    def updateStatus(self): 
        self.message="Count: %d Threshold: %d"%(self.count,self.threshold)       
        if(self.count<=0):
            self.status="innactive"
        elif(self.count<self.threshold):
            self.status="active"
        else:
            self.status="triggered"
    
class GoalSystem(CountSystem):
    def updateStatus(self):                 
        if(self.count==None):
            newStatus="none"
            self.level=NONE
            self.message="No Count Yet"        
        elif(self.threshold==0 or self.threshold==None):
            newStatus="none"
            self.level=NONE
            self.message="Count: %f No Goal"%self.count
        else:
            self.message="Count: %f Goal: %f"%(self.count,self.threshold)       
            scaleLevel=float(self.count)/self.threshold
            print "scaleLevel: "+str(scaleLevel)
            
            if(scaleLevel<1):
                newStatus="behind"
                self.level=(1-scaleLevel)*WARNING+scaleLevel*INFO
                self.color=tuple(map(lambda x,y: scaleLevel*x+(1-scaleLevel)*y, GREEN, RED))
            elif(scaleLevel<2):
                self.level=INFO
                newStatus="ahead"            
                scaleLevel-=1
                self.color=tuple(map(lambda x,y: scaleLevel*x+(1-scaleLevel)*y, BLUE, GREEN))
            else:
                self.level=INFO
                newStatus="ahead"
                self.color=BLUE
        if(self._status!=newStatus):
            self.history=[(newStatus,self.message,self.statusTime)]+self.history[0:12]
            self._status=newStatus
        self.oaf.statusChange(self)
class GoalNetworkElement(GoalSystem):
    def updateStatus(self):        
        GoalSystem.updateStatus(self) 
        self.oaf.updateNetwork()
class GoalNetworkSystem(GoalSystem):
    def statusChange(self,system):
        pass
    def getChild(self,path,request):
        #print "called getChild"+path
        if(path==""):
            return self
        newElement=GoalNetworkElement(path,self,0)
        self.putChild(path, newElement)
        return newElement
    def updateNetwork(self):
        self.threshold=0
        self.count=0
        for element in self.children.values():
            if(element.threshold!=None):
                self.threshold+=element.threshold
            if(element.count!=None):
                self.count+=element.count
        self.updateStatus()
    def render_GET(self,request):
        #print "called render"
        head="""<html><head><title>OAF status: %s system: %s</title></head><body bgcolor="%s">"""%(self.status,self.systemName,getWebColor(self.color))
        currState =""" status: %s system: %s message: %s <br/>color: %s blink: %d<br/>OAF Server Page"""% \
            (self.status,self.systemName,self.message,str(self.color),self.blink)
        systemTable="<table>"
        for path,currSystem in self.children.items():
            systemTable+="""<tr bgcolor="white"><td><a href="%s/%s">%s</a></td><td bgcolor="%s">%s</td><td>%s</td><td>%s</td></tr>"""%(request.uri,path,currSystem.systemName,getWebColor(currSystem.color),currSystem.status,currSystem.message,time.strftime("%a %d %b %Y %H:%M:%S",currSystem.statusTime))
        systemTable+="</table>"
        foot="""<a href="..">parent oaf</a></body></html>"""
        return head+currState+systemTable+foot
class Monitor(System):
    def __init__(self,name,interval=600):
        super(Monitor,self).__init__(name)
        
        self.interval=interval        
        task.LoopingCall(self.checkSystem).start(self.interval)
    def checkSystem(self):
        #print "Called Monitor.checkSystem for "+self.systemName
        pass

class ChangeMonitor(Monitor):
    def __init__(self,name):
        Monitor.__init__(self,"Change Monitor for "+name,600)
        self.message="System started at: "+time.strftime("%a %d %b %Y %H:%M:%S")
    def checkSystem(self):
        #print "Checking, no change for: %d"%(time.mktime(time.localtime())-time.mktime(self.statusTime))
        if((self.status=="working")and ((time.mktime(time.localtime())-time.mktime(self.statusTime))>self.interval)):
            self.message="No change recieved for %d seconds."%(time.mktime(time.localtime())-time.mktime(self.statusTime))
            self.status="error"
        Monitor.checkSystem(self)            
class ProcessMonitor(Monitor):
    statusList={"none":(NONE,WHITE,0),"ok":(DEFAULT,GREEN,0),"working":(INFO,GREEN,5),
              "success":(INFO,GREEN,0),"failure":(WARNING,RED,0),"error":(ALERT,RED,7)}
    def __init__(self,name,range=2400):
        Monitor.__init__(self,"Process Monitor for "+name,100)
        self.lastStepTime=time.localtime()
        self.range=range
        self.lagLevel=0
        self.message="System started at: "+time.strftime("%a %d %b %Y %H:%M:%S")
    def render_GET(self,request):
        if(request.args.has_key('status')and (request.args['status'][0]!='')):
            self.lastStepTime=time.localtime()           
        return System.render_GET(self,request)

    def checkSystem(self):
        #print "Checking, no change for: %d"%(time.mktime(time.localtime())-time.mktime(self.statusTime))
        if(self.status=="working"):            
            lagLevel=(time.mktime(time.localtime())-time.mktime(self.lastStepTime))/self.range
            if(lagLevel>1):
                lagLevel=1
            #if the system has gotten better or Level has been set to none
            # update the level
            #This implements the ACK function, clearing the ACK iff
            # the system has cleared its error
            if((lagLevel<self.lagLevel) or (self.level!=NONE)):
                self.level=INFO+lagLevel*(WARNING-INFO)
            self.lagLevel=lagLevel
            self.color=tuple(map(lambda x,y: lagLevel*x+(1-lagLevel)*y, RED, GREEN))
            self.blink=7*lagLevel+1
            self.oaf.statusChange(self)
        Monitor.checkSystem(self)            
class PageMonitor(Monitor):
    def __init__(self,page,threshold=3,interval=600,allowedErrors=None):
        "Setup before init so that check page can run in init"
        
        self.page=str(page)
        self.warningLevel=0
        self.threshold=3
        self.pingCount=0
        if(allowedErrors==None):
            allowedErrors=[]
        self.allowedErrors=allowedErrors

        super(PageMonitor,self).__init__("Monitor for "+page,interval)
        
        self.message="System started at: "+time.strftime("%a %d %b %Y %H:%M:%S")
        
    def checkSystem(self):
        self.pingCount=0
        self.getPage()
        Monitor.checkSystem(self)
    def getPage(self):
        if(self.pingCount<=3*self.threshold):
            self.pingCount+=1
            client.getPage(self.page).addErrback(self.pageError).addCallback(self.pageRetrieved)
    def pageRetrieved(self,data):

        self.message="Page retrieved at: "+time.strftime("%a %d %b %Y %H:%M:%S")
        if(self._pageRetrieved()):
            self.status="ok"
        else:
            reactor.callLater(5,self.getPage)
    #returns true if system can be considered up
    def _pageRetrieved(self):
        """Adjusts internal counts, returns true if system can now be considered up or 
        or false if the the system should be considered iffy"""
        if(self.warningLevel>0):
            self.warningLevel-=.5
        
        if(self.warningLevel>0): 
            return False
        else:
            return True
    def pageError(self,failure):
        self.message="Page not retrieved at: "+time.strftime("%a, %d %b %Y %H:%M:%S")+" warning level: "+(str)(self.warningLevel)
        if(isinstance(failure, error.Error)): 
            if (failure.value.status in self.allowedErrors):
                print "Found status %s in allowedErrors"%failure.value.status
                return None
            else:
                print "%s is a genuine failure"%(failure.value.status)
        if(self.pingCount>3*self.threshold):
            self.message="Ping count exceeded"
            self.status="error"        
        elif(self.warningLevel>self.threshold):
            self.status="error"
        else:
            self.warningLevel+=1
            reactor.callLater(5,self.getPage)
class PickledSystem(PageMonitor):
    def __init__(self,page,threshold=3):
        super(PickledSystem,self).__init__(page,threshold,interval=10)
        self.color=WHITE
        self.blink=0
        self.level=NONE
        self.systemName="Remote OaF from "+page     
    def pageRetrieved(self,data):
        
        PageMonitor._pageRetrieved(self) #NB iffy systems are not rechecked until sucesss
                                        # a PickledSystem uses the PageMonitor 
                                        # mechanism to retry only on failure. 
        try:
            self.remoteStatus=marshal.loads(data)        #print self.remoteStatus
            if((self.color==self.remoteStatus['color']) \
               and (self.message==self.remoteStatus['message']) \
               and (self.blink==self.remoteStatus['blink']) \
               and (self.level==self.remoteStatus['level']) \
               and (self.status==self.remoteStatus['status'])):
                return
            
            
            
            self.color=self.remoteStatus['color']
            self.message=self.remoteStatus['message']
            self.level=self.remoteStatus['level']
            self.blink=self.remoteStatus['blink']  
            self._status=self.remoteStatus['status']        
            self.statusTime=time.localtime()
            self.history=[(self._status,self.message,self.statusTime)]+self.history[0:12]
            self.oaf.statusChange(self)        #print "set status "+value
        except:
            #if there is any exception, assume garbled data, increment the warning level
            self._status="Exception in pickle parsing."
            self.warningLevel+=1
if __name__=="__main__":
    
    root =resource.Resource()
    #root.putChild('',HomePage())
    oafRoot=OafServer()
    # oafRoot.putSystem('name', PageMonitor('https://example.com',oafRoot))
    # oafRoot.putSystem('name1', PageMonitor('https://example.com',oafRoot))
    # oafRoot.putSystem('name2', PageMonitor('https://example.com',oafRoot))
    # oafRoot.putSystem('name3', PageMonitor('https://example.com',oafRoot))
    # oafRoot.putSystem('name4', PageMonitor('https://example.com',oafRoot))
    
    
    if(len(sys.argv)>2):        
        oafRoot.putNotifier("orb", OrbNotifier(sys.argv[2]))
    
    root.putChild("orb",oafRoot)
    root.putChild("exform",exampleForm.Simple)
    site = server.Site(root)

    if(len(sys.argv)>1):
        reactor.listenTCP(int(sys.argv[1]),site)
    else:
        reactor.listenTCP(8000,site)
    
    reactor.run()
    print "Reactor stopped."        
    