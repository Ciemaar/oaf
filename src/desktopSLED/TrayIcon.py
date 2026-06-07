import wx  # type: ignore

from orbLib import OaF

from .ConfigWindow import ConfigWindow
from .ids import ID_ABOUT, ID_CONFIG, ID_EXIT


class TrayIcon(wx.TaskBarIcon, OaF.Notifier):
    def __init__(self, app):
        self.app = app
        wx.TaskBarIcon.__init__(self)
        OaF.Notifier(self)
        self.message = "Starting..."
        self.color = OaF.WHITE
        self.updateIcon()

    def updateIcon(self):
        image = wx.EmptyImage(16, 16)
        rect = wx.Rect(0, 0, 16, 16)
        image.SetRGBRect(rect, self.color[0] * 0xFF, self.color[1] * 0xFF, self.color[2] * 0xFF)
        bitmap = wx.BitmapFromImage(image)
        # iconFile=wx.Icon("tank2.ico",wx.BITMAP_TYPE_ICO)
        iconFile = wx.IconFromBitmap(bitmap)
        self.SetIcon(iconFile, self.message)

    def setState(self, color, blink, message, level, status):
        self.message = message
        self.color = color
        self.updateIcon()

    def CreatePopupMenu(self):

        menu = wx.Menu()
        menu.Append(ID_ABOUT, "&About", " Information about this program")
        menu.Append(ID_CONFIG, "&Config", " Configure SLED")
        menu.AppendSeparator()
        menu.Append(ID_EXIT, "E&xit", " Terminate the program")

        self.Bind(wx.EVT_MENU, self.onAbout, id=ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.onConfig, id=ID_CONFIG)
        self.Bind(wx.EVT_MENU, self.onExit, id=ID_EXIT)

        return menu

    def onConfig(self, e):
        frame = ConfigWindow(None, -1, "SL:LED Driver", self.app.oafRoot)
        frame.Show(True)

    def onAbout(self, e):
        d = wx.MessageDialog(None, " SLED Driver", "About SLED Driver", wx.OK)
        # Create a message dialog box
        d.ShowModal()  # Shows it
        d.Destroy()  # finally destroy it when finished.

    def onExit(self, e):
        self.app.Exit()
