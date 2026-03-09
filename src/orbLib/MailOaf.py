from twisted.internet import defer, protocol, reactor
from twisted.mail import imap4, pop3client

from .OaF import Monitor


class POP3CountProtocol(pop3client.POP3Client):
    allowInsecureLogin = True

    def serverGreeting(self, greeting):
        from twisted.internet.defer import ensureDeferred

        pop3client.POP3Client.serverGreeting(self, greeting)

        async def _do_login():
            try:
                await self.login(self.factory.username, self.factory.password)
                stat = await self.stat()
                self.factory.deferred.callback(stat[0])
            except Exception as e:
                self.factory.deferred.errback(e)

        ensureDeferred(_do_login())


class POP3CountFactory(protocol.ClientFactory):
    protocol = POP3CountProtocol

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.deferred = defer.Deferred()

    def clientConnectionFailed(self, connection, reason):
        self.deferred.errback(reason)


class IMAPMailCountProtocol(imap4.IMAP4Client):
    def serverGreeting(self, capabilities):
        from twisted.internet.defer import ensureDeferred

        async def _do_login():
            try:
                await self.login(self.factory.username, self.factory.password)
                # Note: list() returns a tuple containing the list of mailboxes
                mailbox_list = await self.list("", "*")
                inbox_name = "inbox"
                for _flags, _hierarchy, name in mailbox_list:
                    if name.lower() == "inbox":
                        inbox_name = name
                        break

                info = await self.examine(inbox_name)
                self.factory.deferred.callback(info.get("UNSEEN", 0))
            except Exception as e:
                self.factory.deferred.errback(e)

        ensureDeferred(_do_login())

    def connectionLost(self, reason):
        if not self.factory.deferred.called:
            self.factory.deferred.errback(reason)


class IMAPMailCountFactory(protocol.ClientFactory):
    protocol = IMAPMailCountProtocol

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.deferred = defer.Deferred()

    def clientConnectionFailed(self, connection, reason):
        self.deferred.errback(reason)


class MailMonitor(Monitor):
    def __init__(self, systemName):
        super(MailMonitor, self).__init__(systemName)
        self.baseNew = 0

    def checkSystem(self):
        from twisted.internet.defer import ensureDeferred

        async def _do_check():
            try:
                count = await self.getNewMailCount()
                self.gotNewMailCount(count)
            except Exception as e:
                self.errorInMailCheck(e)

        ensureDeferred(_do_check())

    def gotNewMailCount(self, count):
        if count == self.baseNew:
            return
        elif count < self.baseNew:
            self.baseNew = count
            self.status = "ok"
        else:
            self.message = "%d new messages including %d messages kept as new." % (count, self.baseNew)
            self.status = "working"

    def errorInMailCheck(self, failure):
        self.message = str(failure)
        self.status = "error"

    def getNewMailCount(self):
        d = defer.Deferred()
        d.callback(0)
        return d


class IMAPMailMonitor(MailMonitor):
    def __init__(self, server, username, password):
        self.server = server
        self.username = username
        self.password = password
        super(IMAPMailMonitor, self).__init__("Mail monitor for %s@%s (IMAP)" % (username, server))

    def getNewMailCount(self):
        factory = IMAPMailCountFactory(self.username, self.password)
        reactor.connectTCP(self.server, 143, factory)
        return factory.deferred


class POP3MailMonitor(MailMonitor):
    def __init__(self, server, username, password):
        self.server = server
        self.username = username
        self.password = password
        super(POP3MailMonitor, self).__init__("Mail monitor for %s@%s (POP3)" % (username, server))

    def getNewMailCount(self):
        factory = POP3CountFactory(self.username, self.password)
        reactor.connectTCP(self.server, 110, factory)
        return factory.deferred
