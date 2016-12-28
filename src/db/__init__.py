import re

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.session import Session

import orbLib.SLOaf as SLOaf
from secrets import AVUUID, AVNAME

uri="sqlite:///./testdb.db"
engine = create_engine(uri)

# Global session manager.  Session() returns the session object
# appropriate for the current web request.
Session = scoped_session(sessionmaker(autoflush=False, transactional=True,
                                      bind=engine))

meta = MetaData()

print "Connecting to database %s" % uri
meta.bind=engine


class DBBase(object):
    @classmethod
    def query(cls):
        return Session.query(cls)
    @classmethod
    def get(cls,id):
        return cls.query().get(id)
    @classmethod
    def all(cls):
        return cls.query().all()
    
pagemonitors_table = Table('pagemonitors', meta,                           
                Column('id', Integer, primary_key=True),
                Column('oaf_id',Integer,ForeignKey('oafs.id')),
                Column('path', String(20)),
                Column('url', String(255,convert_unicode=True))
                )

class PageMonitor(DBBase):
    def __init__(self, url, path=None):
        
        self.url = url
        if(path==None):
            self.path=re.match(r'https?://(www\.)?([^/]{0,20})', url).group(2)
        else:
            self.path=path
    def __str__(self):
        return self.url
    def getSystem(self):
        return SLOaf.PageMonitor(self.url)

oafs_table = Table('oafs', meta, 
                  Column('id',Integer, primary_key=True),
                  Column('user_id',Integer,ForeignKey('users.id')),
                  Column('OafName',String(20)),
                  Column('AVUUID',String(48))
                  )
class Oaf(DBBase):
    def __init__(self, oafName="System", avuuid=None):
        self.OafName=oafName
        if(avuuid):
            self.AVUUID=avuuid
    def getOaf(self):
        return SLOaf.BoundSLOafServer(self)
            
users_table=Table('users',meta,
                  Column('id',Integer, primary_key=True),
                  Column('avuuid', String(48)),
                  Column('avname',String(256))
                  )

class User(DBBase):
    def __init__(self,avname,avuuid):
        self.avname=avname
        self.avuuid=avuuid
#    def restoreRunVars(self):
#        self.level=SLOaf.NONE
#        self.statusTime=0
#        self.color=SLOaf.WHITE
#        self.message="Newly Loaded"
#        self.blink=SLOaf.NONE
#        self.systemName=self.avname
#        self.status=SLOaf.NONE
#        self.systems={}
#        self.notifiers={}
#        self.controllingSystem=None
#        self.children={}
    def getServer(self):
        return SLOaf.SLOafServer(self.id)
        

user_mapper= mapper( User, users_table, properties= {"oafs":relation(Oaf)})            
oaf_mapper= mapper( Oaf, oafs_table, properties= {"pagemonitors":relation(PageMonitor)})            
page_mapper = mapper( PageMonitor, pagemonitors_table)

            
if __name__=="__main__":
    print "Setting up database with test data"
    print "Creating tables"
    meta.create_all()
    
    apf = Oaf("Andy Fundinger")
    #apf.pagemonitors.append(PageMonitor("http://216.254.64.114:8813/factory","Gerri Lit"))
    apf.pagemonitors.append(PageMonitor("http://localhost:8813/bookstore/Wilson", "Wilhelm Lit"))
    apf.pagemonitors.append(PageMonitor("http://localhost:8956/systems/rocketLaunch", "Daes dae'mar"))
    
    ivm = Oaf("IVM")
    ivm.pagemonitors.append(PageMonitor("http://localhost:8293/feedServer/"))
    
    mmbx = Oaf("MMBX")
    mmbx.pagemonitors.append(PageMonitor("http://example.com/"))
    mmbx.pagemonitors.append(PageMonitor("http://localhost/"))

    cf = User(AVNAME, AVUUID)
    cf.oafs.append(apf)
    cf.oafs.append(ivm)    
    Session.save(cf)
    Session.commit()
    
    print PageMonitor.all()
    print Oaf.all()
