import sys
import time

import serial
from twisted.internet import reactor, task
from twisted.web import resource, server

import OaF


def ooColors():
    for red in range(0,0x3F):
        for green in range(0,0x3F):
            for blue in range(0,0x3F):
                for blue_offset in (0x00,0x40,0x80,0xC0):
                    for green_offset in (0x00,0x40,0x80,0xC0):
                        for red_offset in (0x00,0x40,0x80,0xC0):
                                yield (red+red_offset)*0x010000+(green+green_offset)*0x0100+(blue+blue_offset)

burstCount=0
zeroDelayCount=1000000
def delayCount():
    global burstCount    
    global zeroDelayCount
    
    if(burstPeriod==None):
        yield normalDelay
    else:    
        for x in range(0,burstPeriod):
            print "Burst mode %d of %d"%(x,burstPeriod)
            yield normalDelay
        
        burstCount=burstCount+1
        burstCountDown=burstCount
           
        while(burstCountDown>0):
            burstDelay = normalDelay/(2**burstCountDown)
            print "Burst Count Down "+str(burstCountDown)
            burstCountDown-=zeroDelayCount   
            if((burstDelay<.001)and(zeroDelayCount>burstCount)):
                zeroDelayCount=burstCount
            yield burstDelay



class SerialIndyNotifier(OaF.Notifier):
    def __init__(self,portDev,rptSystem=None):        
        super(SerialIndyNotifier,self).__init__(rptSystem)   
        self.serialPort=serial.Serial(portDev)
        self.setState(OaF.WHITE,0,"",OaF.NONE,"none")
        task.LoopingCall(self.updateSLED).start(10)
        
    def updateSLED(self):
        statusCode= OaF.getWebColor(self.state["color"])+"000%01X\r"%round(2.0*self.state["blink"]/9.0)
        print statusCode
        try:
            self.serialPort.write(statusCode)
        except Exception, e:
            self.setStateFailed(e)
        
    def setState(self,color,blink,message,level,status):
        self.state={"color":color,"blink":blink,"message":message,"level":level,"status":status}
        print "set state"+str(self.state)
        self.updateSLED()
        
if __name__=="__main__":
    root =resource.Resource()
    #root.putChild('',HomePage())
    
    
    if(len(sys.argv)>2):
        portname= sys.argv[1]
        if(portname != "/dev/null"):
            ser = serial.Serial(sys.argv[1],9600)
            print "Using "+ser.portstr       #check which port was really used
        setting=sys.argv[2]
        if(len(sys.argv)<3):                
            if(portname != "/dev/null"):  
                ser.write(setting)      #write a string
        else:
            testPattern=sys.argv[3]
            if (testPattern in ("1","4")):
                colorSet=(0xFF0000,0x00FF00,0x0000FF,0xFFFF00,0x00FFFF,0xFF00FF,0xFFFFFF,0x000000)
                transSet=range (0,3)
                transRates=range(0,0xFF)
                if(testPattern=="1"):
                    pulseSet=range(0,4)
                else:
                    pulseSet=(0,)
                
                normalDelay=0.0
            elif(testPattern in ("2","3","5")):
                colorSet=ooColors()
                transSet=range (0,3)
                transRates=range(0,0xFF)
                if(testPattern=="5"):
                    pulseSet=(0,)
                else:
                    pulseSet=range(0,4)
                if(testPattern=="3"):
                    normalDelay=1.0               
                else:
                    normalDelay=0.0
            else:
                colorSet=range(0,0xFFFFFF)
                transSet=range (0,3)
                transRates=range(0,0xFF)
                pulseSet=range(0,4)
                normalDelay=2.0
                
            if(len(sys.argv)>4):
                normalDelay=float(sys.argv[4]) 
                           
            if(len(sys.argv)>5):
                burstPeriod=int(sys.argv[5]) 
            else:
                burstPeriod=None
                            
            delaySeq= delayCount()
            for transRate in transRates:
                for trans in transSet:
                    for pulse in pulseSet :                                 
                        for color in colorSet:           
                            currSet= "#%06X%01X%02X%01X\r"%(color,trans,transRate,pulse)                            
                            if(portname != "/dev/null"):
                                ser.write(currSet)
                            print currSet
                            try:
                                delay=delaySeq.next()
                            except StopIteration:
                                delaySeq= delayCount()
                                delay=delaySeq.next()
                            print "Delaying "+str(delay)
                            time.sleep(delay)
        ser.close()
    elif(len(sys.argv)>1):
        root =resource.Resource()
        orbRoot=OaF.OafServer(None)
        orbRoot.putSystem("WilhelmPickle", OaF.PickledSystem("http://localhost:8000/oaf/pickle", orbRoot))
        orbRoot.putNotifier("sled", SerialIndyNotifier(sys.argv[1]))
         
        root.putChild("oaf",orbRoot)
        
        site = server.Site(root)
    
        reactor.listenTCP(8000,site)
        reactor.run()
        print "Reactor stopped."        

    else:
        print "usage: "
        print " SerialIndy portname string"        
        print " SerialIndy portname Test [TestNo] [Rate] [BurstPeriod]"
        print " SerialIndy portname - orb relay setup"