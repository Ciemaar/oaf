from twisted.trial.unittest import TestCase
from orbLib.OaF import *

class OaFTest(TestCase):
    def test_test(self):
        print "ran test_test"
class OafServerTest(TestCase):
    def __init__(self, *args, **kwargs):
        self.system=System("Test System Name")
        self.oaf=OafServer()
        TestCase.__init__(self, *args,**kwargs)
    def test_putSystem(self):
        pass
    def test_putNotifier(self):
        pass
class SystemTest(TestCase):
    def __init__(self, *args, **kwargs):
        self.system=System("Test System Name")
        self.oaf=OafServer()
        TestCase.__init__(self, *args,**kwargs)
    def test_setup(self):
        print "System: %s oaf: %s"%(self.system,self.oaf)
    def test_putSystem(self):
        self.oaf.putSystem("test1", self.system)
        self.assertTrue(hasattr(self.system,"oaf"))
        self.assertEquals(self.system.oaf,self.oaf)
        self.assertEquals(self.oaf.systems["test1"],self.system)
        self.assertEquals(self.oaf.children["test1"],self.system)
    def test_status(self):
        self.system.status="success"
        self.assertEquals(self.system.color,GREEN)
        self.assertEquals(self.system.status,"success")
        self.assertEquals(self.system.level,INFO)
        self.assertEquals(self.system.blink,0)
        self.assertEquals(self.system.history[0][0],"success")
    def test_oafUpdate(self):
        self.oaf.putSystem("test1", self.system)
        self.system.status="working"
        self.assertEquals(self.system.color,BLUE)
        self.assertEquals(self.oaf.color,BLUE)
        self.assertEquals(self.oaf.status,"working")
        self.assertEquals(self.oaf.level,INFO)
        self.assertEquals(self.oaf.blink,5)
        self.assertEquals(self.oaf.controllingSystem,self.system)