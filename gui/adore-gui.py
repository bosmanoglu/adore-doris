#!/usr/bin/env python
#http://python.zirael.org/e-gtk-uimanager1.html
# ensure that PyGTK 2.0 is loaded - not an older version
import pygtk
pygtk.require('2.0')
# import the GTK module
import gtk

import os
import sys
import subprocess
import shlex

try:
  import vte
except:
  print >> sys.stderr, "You need to have python-libvte installed."
  sys.exit(1)

class MyGUI:

  ui_file = open('adore-gui.ui', 'r')
  ui = ui_file.read()

  def __init__( self, title):
    self.window = gtk.Window()
    self.title = title
    self.window.set_title( title)
    self.window.set_size_request( 800, 600)
    self.window.connect( "destroy", self.destroy)
    self.create_interior()
    self.window.show_all()

  def create_interior( self):
    self.mainbox = gtk.VBox()
    self.window.add( self.mainbox)
    # vte term
    # create action group
    self.actiongroup = gtk.ActionGroup('MyActionGroup')
    self.actiongroup.add_actions(
      [('About', None, '_About'),
       ('File', None, '_File'),
       ('Quit', None, '_Quit', None, 'Quit ADORE.', self.file_quit),
       ('Edit', None, '_Edit'),
       ('Copy', None, '_Copy', None, 'Copy selected text.', self.edit_copy),
       ('Paste', None, '_Paste', None, 'Paste text from clipboard.', self.edit_paste),
       ('Process', None, '_Process'),
       ('m_readfiles', None, 'm_readfiles', None, '', self.runMenuName),
       ('m_porbits', None, 'm_porbits', None, '', self.runMenuName),
       ('m_crop', None, '_m_crop', None, '', self.runMenuName),
       ('m_simamp', None, '_m_simamp', None, '', self.runMenuName),
       ('m_timing', None, '_m_timing', None, '', self.runMenuName),
       ('m_ovs', None, '_m_ovs', None, '', self.runMenuName),
       ('s_readfiles', None, 's_readfiles', None, '', self.runMenuName),
       ('s_porbits', None, 's_porbits', None, '', self.runMenuName),
       ('s_crop', None, '_s_crop', None, '', self.runMenuName),
       ('s_ovs', None, '_s_ovs', None, '', self.runMenuName),
       #('', None, '_', None, '', self.process_),
       ('Settings', None, '_Settings'),
       ('Check', None, '_Check', None, 'Check settings against default values.', self.settings_check),
       ('Fix', None, '_Fix', None, 'Fix settings using default relations.', self.settings_fix),
       ('Load', None, '_Load', None, 'Load settings from current folder.', self.settings_load),
       ('Save', None, '_Save', None, 'Save settings to current folder.', self.settings_save),
       ('Reset',  None, '_Reset',  None, 'Reset settings to defaults', self.settings_reset),
       ('ShowAbout', gtk.STOCK_ABOUT, '_About', None, 'Show about information', self.show_about),
       ('Version', gtk.STOCK_INDEX, '_Version', None, 'Show version', self.show_version),
       ])
    # the uimanager
    self.uimanager = gtk.UIManager()
    accelgroup = self.uimanager.get_accel_group()
    self.window.add_accel_group( accelgroup)

    self.uimanager.insert_action_group( self.actiongroup, 0)
    self.uimanager.add_ui_from_string(self.ui)
    # menu bar
    self.menu_bar = self.uimanager.get_widget( "/MenuBar")
    self.mainbox.pack_start( self.menu_bar, expand=False, fill=False)
    self.menu_bar.show()
    # right justify the about menu
#    self.uimanager.get_widget('/MenuBar/AboutMenu').set_right_justified( True)
    # label for answer
#    self.answer_label = gtk.Label( "Hello menus")
#    self.mainbox.pack_start( self.answer_label, padding=10)
#    self.answer_label.show()
    # vte term
    self.v = vte.Terminal()
    self.v.connect("child-exited", lambda term: gtk.main_quit())
    self.v.fork_command("sh", ["/bin/bash", "-c", "adore -i"])
    self.mainbox.pack_start(self.v)
    
    # show the box
    self.mainbox.show()

  def main( self):
    gtk.main()

  def runcmd(self, cmd):
    self.v.feed_child(cmd+'\n');
  def runMenuName(self, w):
    self.runcmd(w.get_name());
  def destroy( self, w):
    gtk.main_quit()

  def file_quit( self, w):
    gtk.main_quit();

  def edit_copy( self, w):
    self.v.copy_clipboard();
    
  def edit_paste( self, w):
    self.v.paste_clipboard();

  def settings_check( self, w):
    self.runcmd('settings check');

  def settings_fix( self, w):
    self.runcmd('settings fix');

  def settings_load( self, w):
    self.runcmd('settings load');

  def settings_save( self, w):
    self.runcmd('settings save');

  def settings_reset( self, w):
    self.runcmd('settings reset');

  def show_about( self, w):
    os.system("echo ADORE-GUI")#self.answer_label.set_label( "Created by Beda Kosata")

  def show_version( self, w):
    os.system("echo alpha 0.0.0") #self.answer_label.set_label( "2.1")

if __name__ == "__main__":
  m = MyGUI( "ADORE GUI - alpha 0.0.0")  
  m.main()
  
