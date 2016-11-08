import wx
import thread
import os
import webbrowser
import logging

def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.AppendItem(item)
    return item

class TaskBarIcon(wx.TaskBarIcon):

    def __init__(self, frame):
        self.frame = frame
        super(TaskBarIcon, self).__init__()
        #self.set_icon(icon, title)
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.on_left_down)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        create_menu_item(menu, 'Fullscan', self.on_fullscan)
        create_menu_item(menu, 'Search missing media', self.on_search_missing_media)
        menu.AppendSeparator()
        create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    def set_icon(self, path, title):
        icon = wx.IconFromBitmap(wx.Bitmap(path))
        self.SetIcon(icon, title)

    def on_left_down(self, event):
        for rs in self.database.execute("SELECT value FROM config WHERE config='general_flask_port'", None):
            webbrowser.open_new('http://127.0.0.1:' + rs[0])
        

    def on_fullscan(self, event):
        thread.start_new_thread(self.library.scan_full, ())

    def on_search_missing_media(self, event):
        thread.start_new_thread(self.library.search_missing_media, ())

    def on_exit(self, event):
        self.ffmpeg.stop_all_transcoding()
        self.database.close()

        os._exit(0)

        wx.CallAfter(self.Destroy)
        self.frame.Close()

    def set_classes(self, database, library, ffmpeg):
        self.database = database
        self.library = library
        self.ffmpeg = ffmpeg


class App(wx.App):

    tbi = None

    def OnInit(self):
        frame=wx.Frame(None)
        self.SetTopWindow(frame)
        self.tbi = TaskBarIcon(frame)
        return True

    def set_icon(self, icon, title):
        self.tbi.set_icon(icon, title)

    def set_classes(self, database, library, ffmpeg):
        self.tbi.set_classes(database, library, ffmpeg)