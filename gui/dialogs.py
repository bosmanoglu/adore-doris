#!/usr/bin/env python

#Modified from:
#http://ardoris.wordpress.com/2008/07/05/pygtk-text-entry-dialog/

import gtk

def responseToDialog(entry, dialog, response):
	dialog.response(response)

def error(msg, title='Agooey'):
    dialog = gtk.MessageDialog(
            None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_ERROR,
            gtk.BUTTONS_OK,
            None)
    dialog.set_title(title);
    dialog.set_markup(msg);
    dialog.show_all()
    #go go go
    response=dialog.run()
    dialog.destroy();	  
    return

def parameter(label1String, label2String=None, textString=None, titleString=None):
	#base this on a message dialog
	dialog = gtk.MessageDialog(
		None,
		gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
		gtk.MESSAGE_QUESTION,
		gtk.BUTTONS_OK_CANCEL,
		None)
	dialog.set_markup(label1String)
	#create the text input field
	entry = gtk.Entry()
	if textString is not None:
	  entry.set_text(textString);
	#allow the user to press enter to do ok
	entry.connect("activate", responseToDialog, dialog, gtk.RESPONSE_OK)
	#create a horizontal box to pack the entry and a label
	hbox = gtk.HBox()
	hbox.pack_start(gtk.Label("Parameters:"), False, 5, 5)
	hbox.pack_end(entry)
	#title
	if titleString:
	  dialog.set_title(titleString);
	#some secondary text
	if label2String:
	  dialog.format_secondary_markup(label2String)
	#add it and show it
	dialog.vbox.pack_end(hbox, True, True, 0)
	dialog.show_all()
	#go go go
	response=dialog.run()
	text = entry.get_text()
        dialog.destroy();	  
	return response,text

def dropdown(dropdownList, label1String, label2String=None, label3String='Selection:', titleString=None):
        #http://www.pygtk.org/pygtk2tutorial/examples/comboboxbasic.py
	#base this on a message dialog
	dialog = gtk.MessageDialog(
		None,
		gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
		gtk.MESSAGE_QUESTION,
		gtk.BUTTONS_OK_CANCEL,
		None)
	dialog.set_markup(label1String)
	#create the text input field
	cmb = gtk.combo_box_new_text()	
	for item in dropdownList:
	  cmb.append_text(item)
	cmb.set_active(0)
	#allow the user to press enter to do ok
	#cmb.connect("activate", responseToDialog, dialog, gtk.RESPONSE_OK)
	#create a horizontal box to pack the entry and a label
	hbox = gtk.HBox()
	hbox.pack_start(gtk.Label(label3String), False, 5, 5)
	hbox.pack_end(cmb)
	#title
	if titleString:
	  dialog.set_title(titleString);
	#some secondary text
	if label2String:
	  dialog.format_secondary_markup(label2String)
	#add it and show it
	dialog.vbox.pack_end(hbox, True, True, 0)
	dialog.show_all()
	#go go go
	response=dialog.run()
	text = cmb.get_active_text()
        dialog.destroy();	  
	return response,text


if __name__ == '__main__':
	print "The name was %s" % parameter("Please enter your name:")
	gtk.main()
