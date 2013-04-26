#!/usr/bin/env python

# example basictreeview.py

import pygtk
pygtk.require('2.0')
import gtk
import os
import dialogs

class SnaphuConfigEditor:
    def snaphuParser(self, set=None, setFile=None):
        if setFile is None:
            setFile=self.setFile;
        if set is None:
            set=self.set;
        f=open(setFile, 'r')
        for l in f:
            wl=l.split('#')[0].strip()      #remove comments
            if wl!='':                      #skip empty lines
                key=wl.split()[0].strip()   #get the keyword
                val=''.join(wl.split()[1:]) #get value
                #print [key, val]
                set[key]=val
        f.close()            

    def advancedChkBtnToggled(self, widget, liststore):
        #widget.get_active()
        liststore.clear()
        self.displayOptions(self.setFile, liststore);

    def displayOptions(self, setFile, liststore):
        # self.set.read(setFile)
        # we'll add some data now - 4 rows with 3 child rows each
        #for section in self.set.sections():
        #    sectionId = self.liststore.append(None, (False,section, ''))
        #    for option,value in self.set.items(section):
        #        if "_rel_" in option and not self.advancedChkBtn.get_active():
        #            continue;
        #        self.liststore.append(sectionId, (False,option,value))
        k=0;
        if os.path.exists(self.setFile):
            f=open(self.setFile, 'r')
            for l in f:
                wl=l.split('#')[0].strip()      #remove comments
                if wl!='':                      #skip empty lines
                    k=k+1;
                    key=wl.split()[0].strip()   #get the keyword
                    val=''.join(wl.split()[1:]) #get value
                    #print [key, val]
                    self.liststore.append((False, key, val))
            f.close()
            self.window.set_title(str('%d settings: %s' % (k, self.setFile)  ))
                        
    def chkbx_toggled_cb(self, cell, path, liststore):
        liststore[path][0]=not liststore[path][0]
        return

    # Handle edited value
    def edited_cb2(self, cell, path, new_text, liststore):
        #print path
        #print new_text
        #print liststore        
        liststore[path][2] = new_text
        liststore[path][0] = True
        self.window.set_title(str('! %s' % ( self.setFile)  ))
        return

#    def row_inserted(self, widget, path, iter):
#        print widget
#        print path
#        print iter
#
#        self.treeview.set_cursor(path, focus_column=self.tvcolumn2, start_editing=True)
        
    # close the window and quit
    def delete_event(self, widget, event, data=None):
        #gtk.main_quit()
        del self.set
        del self.liststore
        self.window.destroy()
        return False

    def saveAsButtonClicked(self, widget, liststore):
        chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                        buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
          filename=chooser.get_filename();
        chooser.destroy()  
        self.setFile=filename
        f=open(self.setFile, 'w')
        for row in liststore:
            f.write(str('%s\t%s\n' %(row[1], row[2])))
        f.close()            
        self.window.set_title(str('%s' % ( self.setFile)  ))

    def saveButtonClicked(self, widget, liststore):
        f=open(self.setFile, 'w')
        for row in liststore:
            f.write(str('%s\t%s\n' %(row[1], row[2])))
        f.close()            
        self.window.set_title(str('%s' % ( self.setFile)  ))
        #Let's see if this will stop the constant crashing
        #self.window.destroy();  

    def addButtonClicked(self, widget, liststore):
        dropdownlist=self.set.keys();
        for row in liststore:
            if row[1] in dropdownlist:
                dropdownlist.remove(row[1]);
        if len(dropdownlist)>0:
            response,param=dialogs.dropdown(dropdownlist, '<b>Add</b>');
            if response == gtk.RESPONSE_OK:
              liststore.prepend((False, param, self.set[param]))
              self.window.set_title(str('! %s' % ( self.setFile)  ))
            return
        else:
            dialogs.error('No more keywords to add.')
            return

    def removeButtonClicked(self, widget, liststore):
        for row in liststore:
            if row[0] == True:
                liststore.remove(row.iter)
                self.window.set_title(str('! %s' % (self.setFile)  ))
                
    def openButtonClicked(self, widget, liststore):
        liststore.clear()
        chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                        buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
          filename=chooser.get_filename();
        chooser.destroy()  
        self.setFile=filename
        self.displayOptions(self.setFile, liststore);

    def __init__(self,mainWindow):
        #Load settings 
        #self.set=ConfigParser.ConfigParser()
        self.set={}
        #Make settings case sensitive
        #self.set.optionxform = str
        #
        mainWindow.readSet();
        self.confFull=os.path.join(mainWindow.set.get('adore','ADOREFOLDER').strip('"'),'set/snaphu.conf.full')
        self.snaphuParser(setFile=self.confFull); #Initialize the set object.
        self.setFile=os.path.join(mainWindow.set.get('adore','outputFolder').strip('"'),'snaphu.conf')
        self.runcmd=mainWindow.runcmd;
#        self.set=ConfigParser.ConfigParser()
#        self.set.read(setFile)
        # Create a new window
        
        self.window = gtk.Window()#hadjustment=None, vadjustment=None)
        self.swindow = gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
        self.swindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        self.window.set_title("AGOOEY Snaphu Configuration Editor")

        self.window.set_size_request(500, 600)

        self.window.connect("delete_event", self.delete_event)
        self.vbox = gtk.VBox(homogeneous=False, spacing=0);
        self.hbox = gtk.HBox(homogeneous=False, spacing=0);

        # create a TreeStore with one string column to use as the model
        self.liststore = gtk.ListStore(bool, str, str)

        ##### SET THE HBOX #####
        self.saveButton=gtk.Button(label='Save', stock=None, use_underline=True);        
        self.saveButton.connect("clicked", self.saveButtonClicked, self.liststore)
        self.saveButton.set_flags(gtk.CAN_DEFAULT);
        self.saveButton.show();

        self.saveAsButton=gtk.Button(label='Save As', stock=None, use_underline=True);        
        self.saveAsButton.connect("clicked", self.saveAsButtonClicked, self.liststore)
        self.saveAsButton.set_flags(gtk.CAN_DEFAULT);
        self.saveAsButton.show();

#        self.refreshButton=gtk.Button(label='Refresh', stock=None, use_underline=True);        
#        self.refreshButton.connect("clicked", self.refreshButtonClicked, self.liststore)
#        self.refreshButton.set_flags(gtk.CAN_DEFAULT);
#        self.refreshButton.show();

        self.openButton=gtk.Button(label='Open', stock=None, use_underline=True);        
        self.openButton.connect("clicked", self.openButtonClicked, self.liststore)
        self.openButton.set_flags(gtk.CAN_DEFAULT);
        self.openButton.show();

        self.addButton=gtk.Button(label='Add', stock=None, use_underline=True);        
        self.addButton.connect("clicked", self.addButtonClicked, self.liststore)
        self.addButton.set_flags(gtk.CAN_DEFAULT);
        self.addButton.show();

        self.removeButton=gtk.Button(label='Remove', stock=None, use_underline=True);        
        self.removeButton.connect("clicked", self.removeButtonClicked, self.liststore)
        self.removeButton.set_flags(gtk.CAN_DEFAULT);
        self.removeButton.show();

#        self.advancedChkBtn=gtk.CheckButton("Advanced");
#        self.advancedChkBtn.connect("toggled", self.advancedChkBtnToggled, self.liststore)
#        self.advancedChkBtn.show();

        self.hbox.pack_start(self.openButton, expand = False, fill = False, padding = 5);
        self.hbox.pack_start(self.saveButton, expand = False, fill = False, padding = 5);
        self.hbox.pack_start(self.saveAsButton, expand = False, fill = False, padding = 5);
        self.hbox.pack_start(self.addButton, expand = False, fill = False, padding = 5);
        self.hbox.pack_start(self.removeButton, expand = False, fill = False, padding = 5);
#        self.hbox.pack_start(self.refreshButton, expand = False, fill = False, padding = 5);
#        self.hbox.pack_start(self.advancedChkBtn, expand = False, fill = False, padding = 20);

        ##### SET THE VBOX #####

#        adj = gtk.Adjustment(0.0, 0.0, 100.0, 1.0, 10.0, 0.0)
#        scrollbar = gtk.HScale(adj)
#        self.vbox.pack_start(scrollbar, False, False, 0)

        
        #Add some data now
        self.displayOptions(self.setFile, self.liststore);

        # create the TreeView using liststore
        self.treeview = gtk.TreeView(self.liststore)

        # create a CellRendererText to render the data
        self.chkbx= gtk.CellRendererToggle();
        self.cell = gtk.CellRendererText()
        self.cell2 = gtk.CellRendererText()        
        #Make chkbox col activatable
        self.chkbx.set_property('activatable', True)
        #Make col1 editable
        self.cell2.set_property('editable', True)
        # connect the edit handling function
        self.cell2.connect('edited', self.edited_cb2, self.liststore)
        self.chkbx.connect('toggled', self.chkbx_toggled_cb, self.liststore)
        #self.liststore.connect('row_inserted', self.row_inserted)

        # create the TreeViewColumn to display the data
        self.tvcolumn0 = gtk.TreeViewColumn('Remove', self.chkbx)
        self.tvcolumn1 = gtk.TreeViewColumn('Settings', self.cell, text=1)
        self.tvcolumn2 = gtk.TreeViewColumn('Values', self.cell2, text=2)

        # add tvcolumn to treeview
        self.treeview.append_column(self.tvcolumn0)
        self.treeview.append_column(self.tvcolumn1)
        self.treeview.append_column(self.tvcolumn2)

        # add the cell to the tvcolumn and allow it to expand
        #self.tvcolumn.pack_start(self.cell, True)
        #self.tvcolumn2.pack_start(self.cell2, True)

        # set the cell "text" attribute to column 0 - retrieve text
        # from that column in liststore
        self.tvcolumn0.add_attribute(self.chkbx, 'active', 0)
        self.tvcolumn1.add_attribute(self.cell, 'text', 1)
        self.tvcolumn2.add_attribute(self.cell2, 'text', 2)

        # make it searchable
        self.treeview.set_search_column(1)

        # Allow sorting on the column
        self.tvcolumn1.set_sort_column_id(1)

        # Allow drag and drop reordering of rows
        self.treeview.set_reorderable(True)
        self.treeview.show()

        self.vbox.pack_start(self.hbox);
        self.vbox.pack_end(self.treeview);
        self.window.set_default(self.saveButton);
        
        self.swindow.add_with_viewport(self.vbox)
        self.window.add(self.swindow)
        #self.vbox.show()
        self.window.show_all();

def main():
    gtk.main()
    return 0

if __name__ == "__main__":
    se = SnaphuConfigEditor()
    main()
