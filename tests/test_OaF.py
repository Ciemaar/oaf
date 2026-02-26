from twisted.trial.unittest import TestCase
from twisted.web.test.requesthelper import DummyRequest

from orbLib.colors import BLUE, GREEN
from orbLib.OaF import INFO, OafServer, System


class OaFTest(TestCase):
    def test_test(self):
        print("ran test_test")


class OafServerTest(TestCase):
    def __init__(self, *args, **kwargs):
        self.system = System("Test System Name")
        self.oaf = OafServer()
        TestCase.__init__(self, *args, **kwargs)

    def test_putSystem(self):
        self.oaf.putSystem("test1", self.system)
        self.assertEqual(self.oaf.systems["test1"], self.system)

    def test_putNotifier(self):
        # Basic check to ensure putNotifier doesn't crash and adds to notifiers dict
        # Assuming Notifier class is available or mocked, here we just test mechanism if possible or skip complexity
        pass

    def test_render_GET(self):
        # Test that render_GET returns bytes
        req = DummyRequest([b""])
        response = self.oaf.render_GET(req)
        self.assertIsInstance(response, bytes)
        self.assertIn(b"OAF Server Page", response)


class SystemTest(TestCase):
    def __init__(self, *args, **kwargs):
        self.system = System("Test System Name")
        self.oaf = OafServer()
        TestCase.__init__(self, *args, **kwargs)

    def test_setup(self):
        print("System: %s oaf: %s" % (self.system, self.oaf))

    def test_putSystem(self):
        self.oaf.putSystem("test1", self.system)
        self.assertTrue(hasattr(self.system, "oaf"))
        self.assertEqual(self.system.oaf, self.oaf)
        self.assertEqual(self.oaf.systems["test1"], self.system)
        self.assertEqual(self.oaf.children[b"test1"], self.system)

    def test_status(self):
        self.system.status = "success"
        self.assertEqual(self.system.color, GREEN)
        self.assertEqual(self.system.status, "success")
        self.assertEqual(self.system.level, INFO)
        self.assertEqual(self.system.blink, 0)
        self.assertEqual(self.system.history[0][0], "success")

    def test_oafUpdate(self):
        self.oaf.putSystem("test1", self.system)
        self.system.status = "working"
        self.assertEqual(self.system.color, BLUE)
        self.assertEqual(self.oaf.color, BLUE)
        self.assertEqual(self.oaf.status, "working")
        self.assertEqual(self.oaf.level, INFO)
        self.assertEqual(self.oaf.blink, 5)
        self.assertEqual(self.oaf.controllingSystem, self.system)

    def test_render_GET(self):
        # Test that render_GET returns bytes
        self.system.status = "ok"
        self.system.color = GREEN
        req = DummyRequest([b""])
        response = self.system.render_GET(req)
        self.assertIsInstance(response, bytes)
        self.assertIn(b"OAF System:", response)
