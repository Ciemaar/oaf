from sqlalchemy import select
from twisted.trial.unittest import TestCase

from db import Base, Oaf, PageMonitor, Session, SLAvatar, engine


class DBTest(TestCase):
    def setUp(self):
        Base.metadata.create_all(engine)
        self.session = Session()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(engine)

    def test_user_creation(self):
        user = SLAvatar("TestUser", "uuid-1234")
        self.session.add(user)
        self.session.commit()

        fetched = self.session.scalars(select(SLAvatar).filter_by(avname="TestUser")).first()
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.avuuid, "uuid-1234")

    def test_oaf_creation(self):
        user = SLAvatar("TestUser", "uuid-1234")
        oaf = Oaf("TestOaf", "uuid-5678")
        user.oafs.append(oaf)
        self.session.add(user)
        self.session.commit()

        fetched = self.session.scalars(select(Oaf).filter_by(OafName="TestOaf")).first()
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.user.avname, "TestUser")

    def test_pagemonitor_creation(self):
        oaf = Oaf("TestOaf", "uuid-5678")
        pm = PageMonitor("http://example.com/test", "TestPath")
        oaf.pagemonitors.append(pm)
        self.session.add(oaf)
        self.session.commit()

        fetched = self.session.scalars(select(PageMonitor).filter_by(path="TestPath")).first()
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.url, "http://example.com/test")
        self.assertEqual(fetched.oaf.OafName, "TestOaf")
        self.assertEqual(str(fetched), "http://example.com/test")

    def test_pagemonitor_no_path(self):
        pm = PageMonitor("http://example.com/test")
        self.assertEqual(pm.path, "example.com")
