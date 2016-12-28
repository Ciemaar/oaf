from twisted.trial.unittest import TestCase

import db
from orbLib.SLOaf import *


class SLServerTest(TestCase):
    def __init__(self, *args, **kwargs):
        #self.system=
        self.server=SLServer("Test SLServer")
        TestCase.__init__(self, *args,**kwargs)
    def test_init(self):
        
        #Test that there are four of each system type
        systemCounts={}
        for system in self.server.systems.itervalues():
            systemCounts[system.__class__]=systemCounts.get(system.__class__,0)+1
        for cls,count in systemCounts.iteritems():
            self.assertEquals(count,4,"There are not four "+str(cls))
    def test_putSystem(self):
        pass
    def test_putNotifier(self):
        pass
    
class BoundSLOafServerTest(TestCase):
    def __init__(self, *args, **kwargs):
        #self.system=
        self.dbOaf = db.Oaf("Test Bound Server", "skeleton")
        self.server=BoundSLOafServer(self.dbOaf)
        TestCase.__init__(self, *args,**kwargs)
    def test_testInit(self):
        self.assertEquals(self.server.configData,self.dbOaf)
        self.assertEquals(self.server.avuuid,self.dbOaf.AVUUID)
    def test_setPageMonitors(self):
        testList = ("http://yahoo.com", "http://google.com", "http://yahoo.com", "http://microsoft.com")
        self.server.setMonitors(testList)
        for system in self.server.systems:
            if(isinstance(system, OaF.PageMonitor)):
                pass
                
            
    
