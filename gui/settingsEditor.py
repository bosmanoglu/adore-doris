#!/usr/bin/env python

# example basictreeview.py

import pygtk
pygtk.require('2.0')
import gtk
import ConfigParser

class SettingsEditor:


    def displayOptions(self, setFile, treestore):
        self.set.read(setFile)
        # we'll add some data now - 4 rows with 3 child rows each
        for section in self.set.sections():
            sectionId = self.treestore.append(None, (False,section, ''))
            for option,value in self.set.items(section):
                self.treestore.append(sectionId, (False,option,value))
                        
    def chkbx_toggled_cb(self, cell, path, treestore):
        treestore[path][0]=not treestore[path][0]
        return

    # Handle edited value
    def edited_cb(self, cell, path, new_text, treestore):
        #print path
        #print new_text
        #print treestore
        treestore[path][2] = new_text
        treestore[path][0] = True
        return
        
    # close the window and quit
    def delete_event(self, widget, event, data=None):
        #gtk.main_quit()
        self.window.destroy()
        return False

    def __init__(self,setFile):
        #Load settings 
        self.set=ConfigParser.ConfigParser()
        self.setFile=setFile;
#        self.set=ConfigParser.ConfigParser()
#        self.set.read(setFile)
        # Create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

        self.window.set_title("AGOOEY Settings Editor")

        self.window.set_size_request(400, 600)

        self.window.connect("delete_event", self.delete_event)

        # create a TreeStore with one string column to use as the model
        self.treestore = gtk.TreeStore(bool, str, str)
        
        #Add some data now
        self.displayOptions(self.setFile, self.treestore);

        # create the TreeView using treestore
        self.treeview = gtk.TreeView(self.treestore)

        # create a CellRendererText to render the data
        self.chkbx= gtk.CellRendererToggle();
        self.cell = gtk.CellRendererText()
        self.cell2 = gtk.CellRendererText()        
        #Make chkbox col activatable
        self.chkbx.set_property('activatable', True)
        #Make col1 editable
        self.cell2.set_property('editable', True)
        # connect the edit handling function
        self.cell2.connect('edited', self.edited_cb, self.treestore)
        self.chkbx.connect('toggled', self.chkbx_toggled_cb, self.treestore)

        # create the TreeViewColumn to display the data
        self.tvcolumn0 = gtk.TreeViewColumn('Apply', self.chkbx)
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
        # from that column in treestore
        self.tvcolumn0.add_attribute(self.chkbx, 'active', 0)
        self.tvcolumn1.add_attribute(self.cell, 'text', 1)
        self.tvcolumn2.add_attribute(self.cell2, 'text', 2)

        # make it searchable
        self.treeview.set_search_column(1)

        # Allow sorting on the column
        self.tvcolumn1.set_sort_column_id(1)

        # Allow drag and drop reordering of rows
        self.treeview.set_reorderable(True)

        self.window.add(self.treeview)

        self.window.show_all()



def main():
    gtk.main()
    return 0

if __name__ == "__main__":
    se = SettingsEditor()
    main()