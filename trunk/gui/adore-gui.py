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
import ConfigParser

try:
  import vte
except:
  print >> sys.stderr, "You need to have python-libvte installed."
  sys.exit(1)

class MyGUI:

  #ui_file = open('adore-gui.ui', 'r')
  #ui = ui_file.read()

  def __init__( self, title,argv):
    self.argv=argv or "/scr/adore -g -i"
    self.set = ConfigParser.ConfigParser()
    self.setFile="/tmp/adore.set"
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
       ('Quit', None, '_Quit', '<ALT>q', 'Quit ADORE.', self.file_quit),
       ('Edit', None, '_Edit'),
       ('Copy', None, '_Copy', '<CTRL><SHIFT>c', 'Copy selected text.', self.edit_copy),
       ('Paste', None, '_Paste','<CTRL><SHIFT>v', 'Paste text from clipboard.', self.edit_paste),
       ('Check', None, '_Check'),
       ('checkProcess', None, 'Process', None, '', self.runMenuCmd),
       ('checkSetup', None, 'Setup', None, '', self.runMenuCmd),
       ('Process', None, '_Process'),
       ('Master', None, '_Master'),
       ('m_readfiles', None, 'm__readfiles', None, '', self.runMenuName),
       ('m_porbits', None, 'm__porbits', None, '', self.runMenuName),
       ('m_crop', None, 'm__crop', None, '', self.runMenuName),
       ('m_simamp', None, 'm__simamp', None, '', self.runMenuName),
       ('m_timing', None, 'm__timing', None, '', self.runMenuName),
       ('m_ovs', None, 'm__ovs', None, '', self.runMenuName),
       ('m_filtazi', None, 'm__filtazi', None, 'Run after coarsecorr', self.runMenuName),
       ('Slave', None, '_Slave'),
       ('s_readfiles', None, 's__readfiles', None, '', self.runMenuName),
       ('s_porbits', None, 's__porbits', None, '', self.runMenuName),
       ('s_crop', None, 's__crop', None, '', self.runMenuName),
       ('s_ovs', None, 's__ovs', None, '', self.runMenuName),
       ('s_filtazi', None, 's__filtazi', None, 'Run after coarsecorr', self.runMenuName),
       ('Interferogram', None, '_Interferogram'),
       ('coarseorb', None, 'coarseorb', None, '', self.runMenuName),
       ('coarsecorr', None, 'coarsecorr', None, '', self.runMenuName),
       ('fine', None, 'fine', None, '', self.runMenuName),
       ('reltiming', None, 'reltiming', None, '', self.runMenuName),
       ('demassist', None, 'demassist', None, '', self.runMenuName),
       ('coregpm', None, 'coregpm', None, '', self.runMenuName),
       ('resample', None, 'resample', None, '', self.runMenuName),
       ('filtrange', None, 'filtrange', None, '', self.runMenuName),
       ('interfero', None, 'interfero', None, '', self.runMenuName),
       ('comprefpha', None, 'comprefpha', None, '', self.runMenuName),
       ('subtrrefpha', None, 'subtrrefpha', None, '', self.runMenuName),
       ('comprefdem', None, 'comprefdem', None, '', self.runMenuName),
       ('subtrrefdem', None, 'subtrrefdem', None, '', self.runMenuName),
       ('coherence', None, 'coherence', None, '', self.runMenuName),
       ('filtphase', None, 'filtphase', None, '', self.runMenuName),
       ('unwrap', None, 'unwrap', None, '', self.runMenuName),
       ('dinsar', None, 'dinsar', None, '', self.runMenuName),
       ('slant2htrick', None, 'slant2htrick', None, '', self.runMenuName),
       ('slant2h', None, 'slant2h', None, '', self.runMenuName),
       ('geocode', None, 'geocode', None, '', self.runMenuName),
       #('', None, '_', None, '', self.process_),
       ('Settings', None, '_Settings'),
       ('settingsCheck', None, '_Check', None, 'Check settings against default values.', self.settings_check),
       ('settingsFix', None, '_Fix', None, 'Fix settings using default relations.', self.settings_fix),
       ('settingsLoad', None, '_Load', None, 'Load settings from current folder.', self.settings_load),
       ('settingsSave', None, '_Save', None, 'Save settings to current folder.', self.settings_save),
       ('settingsReset',  None, '_Reset',  None, 'Reset settings to defaults', self.settings_reset),
       ('ShowAbout', gtk.STOCK_ABOUT, '_About', None, 'Show about information', self.show_about),
       ])
    # the uimanager
    self.uimanager = gtk.UIManager()
    accelgroup = self.uimanager.get_accel_group()
    self.window.add_accel_group( accelgroup)

    self.uimanager.insert_action_group( self.actiongroup, 0)
    #self.uimanager.add_ui_from_string(self.ui)
    self.uimanager.add_ui_from_file(ADOREFOLDER + '/gui/adore-gui.ui')
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
    #self.argv="adore -i -u /home/bosmanoglu/tmp/test/settings.set"
    #self.v.fork_command("sh", ["/bin/bash", "-c", "adore -i" ])
    #self.v.fork_command("sh", ["/bin/bash", "-c", "adore -i -u /home/bosmanoglu/tmp/test/settings.set"])
    self.v.fork_command("sh", ["/bin/bash", "-c", self.argv])
    #self.v.fork_command("sh", shlex.split(self.argv))
    self.mainbox.pack_start(self.v)
    
    # show the box
    self.mainbox.show()

  def main(self):
    gtk.main()

  def readSet(self): #readSettings
    self.set.read(self.setFile)

  def runcmd(self, cmd):
    self.v.feed_child(cmd+'\n');
#  def runMenuCmd #Is located at the bottom... Long function
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
    #os.system("echo ADORE-GUI")#self.answer_label.set_label( "Created by Beda Kosata")
    about = gtk.AboutDialog()
    about.set_program_name("ADORE-GUI")
    about.set_version("0.0.0")
    about.set_copyright("(c) Batuhan Osmanoglu")
    about.set_license("GNU_GPL v2")
    about.set_comments("Automated Doris Environment")
    about.set_website("http://code.google.com/p/adore-doris/")
    self.readSet();
    about.set_logo(gtk.gdk.pixbuf_new_from_file(self.set.get('adore','ADOREFOLDER').strip('\'"') +"/man/adoreDoris_tud_um.png"))
    about.run()
    about.destroy()

  def runMenuCmd(self, w):
    if w.get_name() == "checkProcess":
      self.runcmd('check')
    elif w.get_name() == "checkSetup":
      self.runcmd('check setup');
    #else:
      #do nothing.

if __name__ == "__main__":
  ADOREGUIFOLDER=os.path.split(os.path.realpath(sys.argv[0]))[0]
  ADOREFOLDER=os.path.split(ADOREGUIFOLDER)[0]
  #print ADOREFOLDER
  argv=ADOREFOLDER + "/scr/adore -g -i "
  if len(sys.argv[1:]) >0:
    argv+= " ".join(sys.argv[1:]);
    #print argv
  m = MyGUI("ADORE GUI",argv)  
  m.main()

  
