#!/usr/bin/env python

# example basictreeview.py

import pygtk
pygtk.require('2.0')
import gtk
import xml.etree.cElementTree as etree
from lxml import etree

class xmlEditor:
    def xmlLoad(self, filename, treestore):
        intree=etree.parse(filename)
        sectionId=None
        parentSectionId={}
        k=0;
        for e in intree.iter():
            if e.getparent() is None:
                sectionId=None
            else: 
                sectionId=parentSectionId[e.getparent().tag]
            t=self.treestore.append(sectionId, (e.tag, e.text))
            parentSectionId[e.tag]=t;
        del parentSectionId, sectionId, intree

    def xmlWrite(self, filename, treestore):
        #fid=open(filename, 'w')
        sections=[];
        for section in treestore:
            sections.append(section)
            for row in treestore[(section.path[0])].iterchildren():
                self.getChild(row,sections)

    def getChild(self,row,sections):
        if row is None:
            print('</%s>' % sections.pop())
        else:
            #print('<%s>' % row[0]);
            for child in row.iterchildren():
                print('<%s>%s</%s>' % (child[0],child[1],child[0]))
                self.getChild(child)
                 
    def advancedChkBtnToggled(self, widget, treestore):
        #widget.get_active()
        treestore.clear()
        self.displayOptions(self.xmlFile, treestore);

    def displayOptions(self, xmlFile, treestore):
        self.set.read(xmlFile)
        # we'll add some data now - 4 rows with 3 child rows each
        for section in self.set.sections():
            sectionId = self.treestore.append(None, (False,section, ''))
            for option,value in self.set.items(section):
                if "_rel_" in option and not self.advancedChkBtn.get_active():
                    continue;
                self.treestore.append(sectionId, (False,option,value))
                        
    def chkbx_toggled_cb(self, cell, path, treestore):
        treestore[path][0]=not treestore[path][0]
        return

    # Handle edited value
    def edited_cb(self, cell, path, new_text, treestore):
        #print path
        #print new_text
        #print treestore
        treestore[path][1] = new_text
        #treestore[path][0] = True
        return
        
    # close the window and quit
    def delete_event(self, widget, event, data=None):
        gtk.main_quit()
        #del self.treestore
        #self.window.destroy()
        #return False

    def applyButtonClicked(self, widget, treestore):
        settxt="settings apply -r "
        self.runcmd(settxt);
        #Let's see if this will stop the constant crashing
        #self.window.destroy();  

    def refreshButtonClicked(self, widget, treestore):
        treestore.clear()
        self.displayOptions(self.xmlFile, treestore);

    def m_about(self, w):
        about = gtk.AboutDialog()
        about.set_program_name("ADORE XML Editor")
        about.set_version('0.1')
        about.set_copyright("(c) Batuhan Osmanoglu 2009-2013")
        about.set_license(open("../license.txt", 'r').read())    
        about.set_comments("Automated Doris Environment")
        about.set_website("http://code.google.com/p/adore-doris/")
        about.set_logo(gtk.gdk.pixbuf_new_from_file("./adore-doris-gui-icon-256px.png"))
        about.run()
        about.destroy()
        return

    def m_open(self, w):
        pass
    def m_save(self, w):
        self.xmlWrite(self.xmlFile, self.treestore)
    def m_saveas(self, w):    
        pass
        
    def __init__(self):
        #Load settings 
        self.xmlFile='/home/bosmanoglu/projectLocker/giant/GIAnT/examples/data.xml'
        #Make settings case sensitive
        #
        # Create a new window
             
        self.window = gtk.Window()#hadjustment=None, vadjustment=None)
        self.swindow = gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
        self.swindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        self.window.set_title("AGOOEY XML Editor")

        self.window.set_size_request(400, 600)

        self.window.connect("delete_event", self.delete_event)
        self.vbox = gtk.VBox(homogeneous=False, spacing=0);
        self.hbox = gtk.HBox(homogeneous=False, spacing=0);

        # create a TreeStore with one string column to use as the model
        self.treestore = gtk.TreeStore(str, str)

        ######################
        ## MENU
        ######################
        # create action group
        self.actiongroup = gtk.ActionGroup('MyActionGroup')
        self.actiongroup.add_actions([
        ('File', None, '_File'),
        ('Open', None, '_Open', '<ALT>o', 'Open an XML file.', lambda w: self.m_open(w)),
        ('Save', None, '_Save', '<ALT>s', 'Save an XML file.', lambda w: self.m_save(w)),
        ('SaveAs', None, 'S_aveAs', '<ALT>a', 'Save as an XML file.', lambda w: self.m_saveas(w)),
        ('Help', None, '_Help'),
        ('About', gtk.STOCK_ABOUT, '_About', None, 'Show about information', lambda w: self.m_about(w))])
        # the uimanager
        self.uimanager = gtk.UIManager()
        accelgroup = self.uimanager.get_accel_group()
        self.window.add_accel_group( accelgroup)

        self.uimanager.insert_action_group( self.actiongroup, 0)
        self.uimanager.add_ui_from_string("""
        <ui>
        <menubar name="xmlMenu">
          <menu action="File">
            <menuitem action="Open"/>
            <menuitem action="Save"/>
            <menuitem action="SaveAs" />
            <separator/>
          </menu>
          <menu action="Help">
            <menuitem action="About"/>
          </menu>
        </menubar>
        </ui>
        """)
        #self.uimanager.add_ui_from_file(ADOREFOLDER + '/gui/agooey.ui')
        # menu bar
        self.menu_bar = self.uimanager.get_widget( "/xmlMenu")
        self.vbox.pack_start( self.menu_bar, expand=False, fill=False)
        self.menu_bar.show()

        ##### SET THE VBOX #####

#        adj = gtk.Adjustment(0.0, 0.0, 100.0, 1.0, 10.0, 0.0)
#        scrollbar = gtk.HScale(adj)
#        self.vbox.pack_start(scrollbar, False, False, 0)

        
        #Add some data now
#        self.displayOptions(self.xmlFile, self.treestore);
        self.xmlLoad(self.xmlFile, self.treestore);
        # create the TreeView using treestore
        self.treeview = gtk.TreeView(self.treestore)

        # create a CellRendererText to render the data
        #self.chkbx= gtk.CellRendererToggle();
        self.cell = gtk.CellRendererText()
        self.cell2 = gtk.CellRendererText()        
        #Make chkbox col activatable
        #self.chkbx.set_property('activatable', True)
        #Make col1 editable
        self.cell2.set_property('editable', True)
        # connect the edit handling function
        self.cell2.connect('edited', self.edited_cb, self.treestore)
        #self.chkbx.connect('toggled', self.chkbx_toggled_cb, self.treestore)

        # create the TreeViewColumn to display the data
        #self.tvcolumn0 = gtk.TreeViewColumn('Apply', self.chkbx)
        self.tvcolumn1 = gtk.TreeViewColumn('Tags', self.cell, text=0)
        self.tvcolumn2 = gtk.TreeViewColumn('Values', self.cell2, text=1)

        # add tvcolumn to treeview
        #self.treeview.append_column(self.tvcolumn0)
        self.treeview.append_column(self.tvcolumn1)
        self.treeview.append_column(self.tvcolumn2)

        # add the cell to the tvcolumn and allow it to expand
        #self.tvcolumn.pack_start(self.cell, True)
        #self.tvcolumn2.pack_start(self.cell2, True)

        # set the cell "text" attribute to column 0 - retrieve text
        # from that column in treestore
        #self.tvcolumn0.add_attribute(self.chkbx, 'active', 0)
        self.tvcolumn1.add_attribute(self.cell, 'text', 0)
        self.tvcolumn2.add_attribute(self.cell2, 'text', 1)

        # make it searchable
        self.treeview.set_search_column(1)

        # Allow sorting on the column
        self.tvcolumn1.set_sort_column_id(1)

        # Allow drag and drop reordering of rows
        self.treeview.set_reorderable(True)
        self.treeview.show()

        #self.vbox.pack_start(self.hbox);
        self.vbox.pack_end(self.treeview);
        #self.window.set_default(self.applyButton);
        
        self.swindow.add_with_viewport(self.vbox)
        self.window.add(self.swindow)
        #self.vbox.show()
        self.window.show_all();

def main():
    gtk.main()
    return 0

if __name__ == "__main__":
    se = xmlEditor()
    main()
