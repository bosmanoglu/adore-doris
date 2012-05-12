#!/usr/bin/env python


import pygtk
pygtk.require('2.0')
import gtk
import ConfigParser

class ProcessSelector:

    def advancedChkBtnToggled(self, widget):
        self.processEntry.set_editable(self.advancedChkBtn.get_active())
        
    # close the window and quit
    def delete_event(self, widget, event, data=None):
        #gtk.main_quit()
        self.window.destroy()
        return False

    def processButtonClicked(self, widget):
        self.processEntry.set_text(self.processEntry.get_text() + widget.get_label().replace('__','_') +';')
        
    def applyButtonClicked(self, widget):
        self.runcmd(self.processEntry.get_text());

    def refreshButtonClicked(self, widget):
        self.processEntry.set_text('');
        
    def __init__(self,mainWindow):
        self.runcmd=mainWindow.runcmd;
        # Create a new window
        
        self.window = gtk.Window()#hadjustment=None, vadjustment=None)
        self.swindow = gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
        self.swindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        self.window.set_title("AGOOEY Process Selector")

        self.window.set_size_request(600, 240)

        self.window.connect("delete_event", self.delete_event)
        self.vbox = gtk.VBox(homogeneous=False, spacing=0);
        self.hbox = gtk.HBox(homogeneous=False, spacing=0);
        rows=6
        cols=6
        self.table = gtk.Table(rows, cols, False);
        
        button_strings=['m__readfiles','s__readfiles','coarseorb' ,'demassist' ,'subtrrefpha' ,'dinsar',
                        'm__porbits'  ,'s__porbits'  ,'coarsecorr','coregpm'   ,'comprefdem'  ,'slant2h',
                        'm__crop'     ,'s__crop'     ,'m__filtazi','resample'  ,'subtrrefdem' ,'geocode',
                        'm__simamp'   ,''            ,'s__filtazi','filtrange' ,'coherence', '',
                        'm__timing'   ,''            ,'fine'      ,'interfero' ,'filtphase', '',
                        'm__ovs'      ,'s__ovs'      ,'reltiming' ,'comprefpha','unwrap'];
        button = map(lambda i:gtk.Button(button_strings[i]), range(len(button_strings)))

        ##### SET THE HBOX #####
        self.processEntry=gtk.Entry();
        self.processEntry.set_editable(False);
        self.processEntry.show();
        
        self.applyButton=gtk.Button(label='Apply', stock=None, use_underline=True);        
        self.applyButton.connect("clicked", self.applyButtonClicked)
        self.applyButton.set_flags(gtk.CAN_DEFAULT);
        self.applyButton.show();

        self.refreshButton=gtk.Button(label='Clear', stock=None, use_underline=True);        
        self.refreshButton.connect("clicked", self.refreshButtonClicked)
        self.refreshButton.set_flags(gtk.CAN_DEFAULT);
        self.refreshButton.show();

        self.advancedChkBtn=gtk.CheckButton("Advanced");
        self.advancedChkBtn.connect("toggled", self.advancedChkBtnToggled)
        self.advancedChkBtn.show();

        self.hbox.pack_start(self.refreshButton, expand = False, fill = False, padding = 10);
        self.hbox.pack_start(self.applyButton, expand = False, fill = False, padding = 10);
        self.hbox.pack_end(self.advancedChkBtn, expand = False, fill = False, padding = 20);

        #### SET THE TABLE ####
        for i in range(len(button_strings)):
            y,x=divmod(i, cols)
            if not button_strings[i]:
                continue
            button[i].connect("clicked", self.processButtonClicked)
            self.table.attach(button[i], x, x+1, y,y+1)
            button[i].show()

        ### SET THE VBOX ####
        self.vbox.pack_start(self.processEntry, expand = False, fill = False,);
        self.vbox.pack_start(self.hbox, expand = False, fill = False,);
        self.vbox.pack_start(self.table, expand = False, fill = False, );
        self.window.set_default(self.applyButton);
        
        self.swindow.add_with_viewport(self.vbox)
        self.window.add(self.swindow)
        #self.vbox.show()
        self.window.show_all();

def main():
    gtk.main()
    return 0

if __name__ == "__main__":
    se = ProcessSelector()
    main()
