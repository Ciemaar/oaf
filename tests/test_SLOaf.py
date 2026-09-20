from twisted.trial.unittest import TestCase
from twisted.web.test.requesthelper import DummyRequest

import db
from orbLib import OaF
from orbLib.SLOaf import BoundSLOafServer, SLNotifier, SLServer


class SLServerTest(TestCase):
    def __init__(self, *args, **kwargs):
        # self.system=
        self.server = SLServer("Test SLServer")
        TestCase.__init__(self, *args, **kwargs)

    def test_init(self):

        # Test that there are four of each system type
        systemCounts = {}
        for system in self.server.systems.values():
            systemCounts[system.__class__] = systemCounts.get(system.__class__, 0) + 1
        for cls, count in systemCounts.items():
            self.assertEqual(count, 4, "There are not four " + str(cls))

    def test_putSystem(self):
        system = OaF.System("TestSystem")
        self.server.putSystem("testsys", system)
        self.assertIn("testsys", self.server.systems)
        self.assertEqual(self.server.systems["testsys"], system)

    def test_putNotifier(self):
        notifier = SLNotifier(self.server)
        self.server.putNotifier("testnotifier", notifier)
        self.assertIn("testnotifier", self.server.notifiers)

    def test_render_GET(self):
        req = DummyRequest([b""])
        response = self.server.render_GET(req)
        self.assertIsInstance(response, bytes)


class BoundSLOafServerTest(TestCase):
    def __init__(self, *args, **kwargs):
        # self.system=
        self.dbOaf = db.Oaf("Test Bound Server", "skeleton")
        self.server = BoundSLOafServer(self.dbOaf)
        TestCase.__init__(self, *args, **kwargs)

    def tearDown(self):
        for system in self.server.systems.values():
            if hasattr(system, "stop"):
                system.stop()
        super(BoundSLOafServerTest, self).tearDown()

    def test_testInit(self):
        self.assertEqual(self.server.configData, self.dbOaf)
        self.assertEqual(self.server.avuuid, self.dbOaf.AVUUID)

    def test_setPageMonitors(self):
        testList = ("http://yahoo.com", "http://google.com", "http://yahoo.com", "http://microsoft.com")
        self.server.watchedUrls = testList
        self.server.updatePageMonitors()
        for system in self.server.systems.values():
            if isinstance(system, OaF.PageMonitor):
                pass

    def test_render_GET(self):
        req = DummyRequest([b""])
        response = self.server.render_GET(req)
        self.assertIsInstance(response, bytes)


class SLNotifierTest(TestCase):
    def test_render_GET_normal(self):
        notifier = SLNotifier()
        req = DummyRequest([b""])
        # Mock User-Agent to not be SL
        req.requestHeaders.addRawHeader(b"User-Agent", b"Mozilla/5.0")

        response = notifier.render_GET(req)
        self.assertIsInstance(response, bytes)
        self.assertIn(b"No Representation", response)

    def test_render_GET_sl(self):
        notifier = SLNotifier()
        req = DummyRequest([b""])
        # Mock User-Agent to be SL
        req.requestHeaders.addRawHeader(b"User-Agent", b"Second Life LSL/1.0")
        req.requestHeaders.addRawHeader(b"HTTP_X_SecondLife_Object_Key", b"uuid-key")

        # We need to set some state for _SLCSV to return valid string to encode
        notifier.color = notifier.colorToVector((1.0, 1.0, 1.0))
        notifier.blink = 0
        notifier.status = "ok"
        notifier.level = 0.0
        notifier.message = "test"

        response = notifier.render_GET(req)
        self.assertIsInstance(response, bytes)
        # Check CSV format
        self.assertIn(b'<1.000000,1.000000,1.000000>,0,ok,0.000000,"test"', response)
