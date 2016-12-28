from twisted.internet import protocol, defer, reactor
from twisted.mail import imap4
from twisted.mail import pop3client

from OaF import Monitor


class POP3CountProtocol(pop3client.POP3Client):
    allowInsecureLogin=True
    def serverGreeting(self,greeting):
        pop3client.POP3Client.serverGreeting(self, greeting)
        login = self.login(self.factory.username,self.factory.password)
        login.addCallback(self._loggedIn)
        login.chainDeferred(self.factory.deferred)
    def _loggedIn(self,result):
        return self.stat().addCallback(self.gotStat)
    def gotStat(self,stat):
        return stat[0]
class POP3CountFactory(protocol.ClientFactory):
    protocol = POP3CountProtocol
    def __init__(self,username,password):
        self.username=username
        self.password=password
        self.deferred=defer.Deferred()
    def clientConnectionFailed(self,connection,reason):
        self.deferred.errback(reason)

    
class IMAPMailCountProtocol(imap4.IMAP4Client):
    def serverGreeting(self,capabilities):
        login = self.login(self.factory.username,self.factory.password)
        login.addCallback(self.__loggedIn)
        login.chainDeferred(self.factory.deferred)
    def __loggedIn(self,results):
        return self.list("","*").addCallback(self.__gotMailboxInfo)
    def __getMailboxList(self,list):
        for flags,hierarchy,name in list:
            if(list.lower()=="inbox"):
                print flags
                self.examine(name).addCallback(self.__gotMailboxInfo)
    def __gotMailboxInfo(self,info):
        return info['UNSEEN']
    def connectionLost(self,reason):
        if not self.factory.deferred.called:
            self.factory.deferred.errback(reason)

class IMAPMailCountFactory(protocol.ClientFactory):
    protocol=IMAPMailCountProtocol
    def __init__(self,username,password):
        self.username=username
        self.password=password
        self.deferred=defer.Deferred()
    def clientConnectionFailed(self,connection,reason):
        self.deferred.errback(reason)

class MailMonitor(Monitor):
    def __init__(self,systemName):
        super(MailMonitor,self).__init__(systemName)
        self.baseNew=0
    def checkSystem(self):
        self.getNewMailCount().addCallback(self.gotNewMailCount).addErrback(self.errorInMailCheck)
    def gotNewMailCount(self,count):
        if(count==self.baseNew):
            return
        elif(count<self.baseNew):
            self.baseNew=count
            self.status="ok"
        else:
            self.message="%d new messages including %d messages kept as new."%(count,self.baseNew)
            self.status="working"
    def errorInMailCheck(self,failure):
        self.message=str(failure)
        self.status="error"
    def getNewMailCount(self):
        d =defer.Deferred()
        d.callback(0)
        return d
class IMAPMailMonitor(MailMonitor):
    def __init__(self,server,username,password):
        super(IMAPMailMonitor,self).__init__("Mail monitor for %s@%s (IMAP)"%(username,server))
        self.server=server
        self.username=username
        self.password=password
    def getNewMailCount(self):
        factory = IMAPMailCountFactory(self.username,self.password)
        reactor.connectTCP(self.server,143,factory)
        return factory.deferred
class POP3MailMonitor(MailMonitor):
    def __init__(self,server,username,password):
        super(POP3MailMonitor,self).__init__("Mail monitor for %s@%s (POP3)"%(username,server))
        self.server=server
        self.username=username
        self.password=password
    def getNewMailCount(self):
        factory = POP3CountFactory(self.username, self.password)
        reactor.connectTCP(self.server,110,factory)
        return factory.deferred
