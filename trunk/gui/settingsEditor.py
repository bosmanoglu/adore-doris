#!/usr/bin/env python

# example basictreeview.py

import pygtk
pygtk.require('2.0')
import gtk
import ConfigParser

class SettingsEditor:

    # close the window and quit
    def delete_event(self, widget, event, data=None):
        #gtk.main_quit()
        self.window.destroy()
        return False

    def __init__(self,setFile):
        #Load settings 
        self.setFile=setFile;
        self.set=ConfigParser.ConfigParser()
        self.set.read(setFile)
        # Create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

        self.window.set_title("AGOOEY Settings Editor")

        self.window.set_size_request(200, 400)

        self.window.connect("delete_event", self.delete_event)

        # create a TreeStore with one string column to use as the model
        self.treestore = gtk.TreeStore(str, str)

        # we'll add some data now - 4 rows with 3 child rows each
        for section in self.set.sections():
        #for parent in range(4):
            sectionId = self.treestore.append(None, (section, section))
            for option,value in self.set.items(section):
                self.treestore.append(sectionId, (option,value))

        # create the TreeView using treestore
        self.treeview = gtk.TreeView(self.treestore)

        # create the TreeViewColumn to display the data
        self.tvcolumn = gtk.TreeViewColumn('Settings')
        self.tvcolumn2 = gtk.TreeViewColumn('Values')

        # add tvcolumn to treeview
        self.treeview.append_column(self.tvcolumn)
        self.treeview.append_column(self.tvcolumn2)

        # create a CellRendererText to render the data
        self.cell = gtk.CellRendererText()
        self.cell2 = gtk.CellRendererText()

        # add the cell to the tvcolumn and allow it to expand
        self.tvcolumn.pack_start(self.cell, True)
        self.tvcolumn2.pack_start(self.cell2, True)

        # set the cell "text" attribute to column 0 - retrieve text
        # from that column in treestore
        self.tvcolumn.add_attribute(self.cell, 'text', 0)
        self.tvcolumn2.add_attribute(self.cell2, 'text', 0)

        # make it searchable
        self.treeview.set_search_column(0)

        # Allow sorting on the column
        self.tvcolumn.set_sort_column_id(0)

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
