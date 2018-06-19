import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk,Gdk
import os
import glob
import time
#import definitions
#import utils.gui
#import utils.helpers
#from engine.engine import Engine as app_engine
from datetime import datetime, timedelta

# gui to choose analysistime frame window
# once timeframe is selected extract network data from pcap files
# send extracted data to ecel-model module

class DssGUI(Gtk.Window): 
	def __init__(self):
		super(DssGUI, self).__init__()
		
		#self.main_gui = parent
		
		#self.collectors = collectors
		self.set_title("DSS")
		self.set_modal(True)
		#self.set_transient_for(self.main_gui)
		self.set_position(Gtk.WindowPosition.CENTER)#_ON_PARENT)
		self.set_size_request(275,250)
		self.set_resizable(False)
		
		# create combobox with timeframe options
		self.time_options = Gtk.ListStore(str)
		self.options_list = ["Select a timeframe", "5 minutes", "30 minutes", "1 hour", "All"]
		for i in xrange(len(self.options_list)):
			self.time_options.append([self.options_list[i]])
			
		self.timeframe_combobox = Gtk.ComboBox.new_with_model_and_entry(self.time_options)
		
		#TODO: Figure out why combobox isn't showing the first option
		#	   I think it's the following line
		self.timeframe_combobox.set_entry_text_column(0) 
		
		cell = Gtk.CellRendererText()
		self.timeframe_combobox.pack_start(cell, True)
		self.timeframe_combobox.add_attribute(cell, "text", 0)
		
		# create buttons
		button_analyze = Gtk.Button("Analyze")
		button_analyze.connect("clicked", self.close_dialog) #TODO: Change to self.analyze
		button_cancel = Gtk.Button("Cancel")
		button_cancel.connect("clicked", self.close_dialog)
		
		# create labels for title and error
		title = Gtk.Label("Select Timeframe to Analyze:")
		self.errormsg = Gtk.Label()
		
		# pack layout
		vbox = Gtk.VBox()
		vbox.pack_start(title, True, True, 0)
		vbox.pack_start(self.errormsg, True, True, 0)
		vbox.pack_start(self.timeframe_combobox, True, True, 0)
		
		hbox_okcancel = Gtk.HBox()
		hbox_okcancel.pack_start(button_cancel, True, True, 5)
		hbox_okcancel.pack_start(button_analyze, True, True, 5)
		vbox.pack_start(hbox_okcancel, False, False, 10)
		
		self.add(vbox)
		self.show_all()
		
	def close_dialog(self, event):
		self.hide_all()
		
	#def analyze(self, event):
		# Put code here
		

DssGUI()
Gtk.main()	
		
		
		
		
		
		
