import re
from typing import List, Optional

from sqlalchemy import ForeignKey, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, scoped_session, sessionmaker

# Handle missing secrets
try:
    from .secrets import AVNAME, AVUUID
except ImportError:
    AVUUID = "default-uuid"
    AVNAME = "Default User"

uri = "sqlite:///./testdb.db"
engine = create_engine(uri)

session_factory = sessionmaker(autoflush=False, expire_on_commit=False, bind=engine)
Session = scoped_session(session_factory)


class Base(DeclarativeBase):
    pass


class DBBase(Base):
    __abstract__ = True

    @classmethod
    def get(cls, id):
        return Session.get(cls, id)

    @classmethod
    def all(cls):
        return Session.scalars(select(cls)).all()


class PageMonitor(DBBase):
    __tablename__ = "pagemonitors"

    id: Mapped[int] = mapped_column(primary_key=True)
    oaf_id: Mapped[Optional[int]] = mapped_column(ForeignKey("oafs.id"))
    path: Mapped[Optional[str]] = mapped_column(String(20))
    url: Mapped[Optional[str]] = mapped_column(String(255))

    oaf: Mapped["Oaf"] = relationship(back_populates="pagemonitors")

    def __init__(self, url, path=None):
        self.url = url
        if path is None:
            match = re.match(r"https?://(www\.)?([^/]{0,20})", url)
            if match:
                self.path = match.group(2)
            else:
                self.path = "unknown"
        else:
            self.path = path

    def __str__(self):
        return self.url

    def getSystem(self):
        from orbLib import SLOaf

        return SLOaf.PageMonitor(self.url)


class Oaf(DBBase):
    __tablename__ = "oafs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    OafName: Mapped[Optional[str]] = mapped_column(String(20))
    AVUUID: Mapped[Optional[str]] = mapped_column(String(48))

    user: Mapped["SLAvatar"] = relationship(back_populates="oafs")
    pagemonitors: Mapped[List["PageMonitor"]] = relationship(back_populates="oaf")

    def __init__(self, oafName="System", avuuid=None):
        self.OafName = oafName
        if avuuid:
            self.AVUUID = avuuid

    def getOaf(self):
        from orbLib import SLOaf

        return SLOaf.BoundSLOafServer(self)


class SLAvatar(DBBase):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    avuuid: Mapped[Optional[str]] = mapped_column(String(48))
    avname: Mapped[Optional[str]] = mapped_column(String(256))

    oafs: Mapped[List["Oaf"]] = relationship(back_populates="user")

    def __init__(self, avname, avuuid):
        self.avname = avname
        self.avuuid = avuuid

    def getServer(self):
        from orbLib import SLOaf

        return SLOaf.SLOafServer(self.id)


if __name__ == "__main__":
    print("Setting up database with test data")
    print("Creating tables")
    Base.metadata.create_all(engine)

    with Session() as session:
        apf = Oaf("Andy Fundinger")
        # apf.pagemonitors.append(PageMonitor("http://216.254.64.114:8813/factory","Gerri Lit"))
        apf.pagemonitors.append(PageMonitor("http://localhost:8813/bookstore/Wilson", "Wilhelm Lit"))
        apf.pagemonitors.append(PageMonitor("http://localhost:8956/systems/rocketLaunch", "Daes dae'mar"))

        ivm = Oaf("IVM")
        ivm.pagemonitors.append(PageMonitor("http://localhost:8293/feedServer/"))

        mmbx = Oaf("MMBX")
        mmbx.pagemonitors.append(PageMonitor("http://example.com/"))
        mmbx.pagemonitors.append(PageMonitor("http://localhost/"))

        cf = SLAvatar(AVNAME, AVUUID)
        cf.oafs.append(apf)
        cf.oafs.append(ivm)

        session.add(cf)
        session.commit()

    print(PageMonitor.all())
    print(Oaf.all())
