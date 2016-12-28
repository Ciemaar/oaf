import cPickle

import wx

from ids import *
from orbLib import OaF
from orbLib.SerialIndy import SerialIndyNotifier


class ConfigWindow(wx.Frame):
    pklFilename="sledConfig.cfg"
    def __init__(self,parent,id,title,oafRoot):
        wx.Frame.__init__(self,parent,id, title)
        self.oafRoot=oafRoot

        self.CreateStatusBar() # A Statusbar in the bottom of the window
        # Setting up the menu.
        filemenu= wx.Menu()
        filemenu.Append(ID_ABOUT, "&About"," Information about this program")
        filemenu.AppendSeparator()
        filemenu.Append(ID_CLOSE,"E&xit"," Terminate the program")
        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        wx.EVT_MENU(self, ID_ABOUT, self.onAbout)
        wx.EVT_MENU(self, ID_CLOSE, self.onExit)
        
        self.sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        self.buttons=[]
    
        buttonLabels= (
#                      (ID_PREV,"Prev",self.onPrev),
                      #(ID_DISCARD,"Discard",self.onDiscard),
                      (ID_OPEN_PORT,"Open",self.onOpen),
                      #(ID_NEXT,"Next",self.onNext),
                      (ID_CLOSE,"Close",self.onExit),
                      )
        for id,label,eventHandler in buttonLabels:
            newButton=wx.Button(self, id, label)
            self.sizer2.Add(newButton,1,wx.EXPAND)
            wx.EVT_BUTTON(self,id,eventHandler)
                # Use some sizers to see layout options
        self.sizer=wx.BoxSizer(wx.VERTICAL)
                 
        self.fieldSection=self.makeFieldSection([])
        
        self.sizer.Add(self.sizer2,1,wx.EXPAND)
        self.sizer.Add(self.fieldSection,0,wx.EXPAND)
        
        #Layout sizers
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)
    def makeFieldSection(self,fieldNames): 
        try:              
            pkl=cPickle.Unpickler(open(self.pklFilename,'r')).load()
        except:
            pkl={"port":"","oaf":""} 
        panel=wx.ScrolledWindow(self,style=wx.TAB_TRAVERSAL)
        section=wx.FlexGridSizer(0,1, 2, 2)
        
        
        label=wx.StaticText(panel,ID_FIELD1+1,"Serial Port")#,size=(200,-1))        
        self.serialPortField=wx.TextCtrl(panel,ID_FIELD1,size=(200,20),name="Serial Port",value=pkl["port"])

        section.Add(label)
        section.Add(self.serialPortField)

        label2=wx.StaticText(panel,ID_FIELD1+3,"Oaf")#,size=(200,-1))        
        self.oafField=wx.TextCtrl(panel,ID_FIELD1+2,size=(200,20),name="OAF",value=pkl["oaf"])

        section.Add(label2)
        section.Add(self.oafField)
        
        panel.SetSizer(section)
        #panel.AdjustScrollbars()
        
        panel.SetAutoLayout(True)

        panel.Layout()
        panel.Fit()
        return (panel)
    def onAbout(self,e):
        d= wx.MessageDialog( self, " SLED Driver","About SLED Driver", wx.OK)
                            # Create a message dialog box
        d.ShowModal() # Shows it
        d.Destroy() # finally destroy it when finished.
    def onExit(self,e):
        self.Close(True)  # Close the frame.
    def onOpen(self,e):
        # oafRoot.putSystem("WilhelmPickle", OaF.PickledSystem("http://localhost:8000/oaf/pickle",oafRoot))
        oafUrl=self.oafField.GetValue()
        sledPort=self.serialPortField.GetValue()
        self.oafRoot.putSystem("ConfigedPickle", OaF.PickledSystem(oafUrl+"/pickle",self.oafRoot))
        try:
            self.oafRoot.putNotifier("sled", SerialIndyNotifier(sledPort))
        except:
            self.oafRoot.putNotifier("sled",None)
        pkl={"oaf":oafUrl,"port":sledPort}
        cPickle.Pickler(open(self.pklFilename,"w")).dump(pkl)
