import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk,Gdk
from utils.css_provider import CssProvider
from utils.collector_action import Action
import engine.collector
import definitions
import os

#TODO: Select multiple collectors

class CollectorListBox(Gtk.TreeView):

    def __init__(self, engine, main_gui):
        super(CollectorListBox,self).__init__()

        self.engine = engine
        self.numCollectors = self.engine.get_collector_length()
        self.get_selection().set_mode(Gtk.SelectionMode.SINGLE)
        self.attached_gui = main_gui
        self.css = CssProvider("widget_styles.css")

        self.collectorStatus = {}

        self.set_activate_on_single_click(True)
        #self.connect("row-selected",self.update_row_colors)
        self.connect("row-activated",self.row_activated_handler)

        # Enable multiple collector selection when CTRL + left click occurs (selection mode == MULTIPLE)
        self.connect("button-press-event",self.enable_multiple)
        # List box updates collector rows on up/down arrow/tab key presses.
        self.connect("key-release-event",self.key_release_handler)

        self.create_collector_list()
        # for i, collector in enumerate(self.engine.collectors):
        #     self.add(self.create_collector_row(collector))
        #     self.collectorStatus[collector.name] = False

    # Collector List Box enables mutliple selection on CTRL + left click
    def enable_multiple(self, lBox, event):
        modifiers = Gtk.accelerator_get_default_mod_mask()
        print "Entering Enable multiple"

        print "Event state and modifiers", event.state & modifiers
        ###Was not working for control###
        '''if(event.button == Gdk.BUTTON_PRIMARY and  ((event.state & modifiers) == Gdk.ModifierType.CONTROL_MASK)):
            print "CTRL was pressed"
            self.set_selection_mode(Gtk.SelectionMode.MULTIPLE)'''

        if(event.button == Gdk.BUTTON_PRIMARY and ((event.state & modifiers) == Gdk.ModifierType.SHIFT_MASK)):
        	print "Shift was pressed"
        	self.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
        elif(event.button == Gdk.BUTTON_SECONDARY): # right click
            path_info = self.get_path_at_pos(event.x, event.y)
            if path_info != None:
                path, col, cellx, celly = path_info
                self.grab_focus()
                self.set_cursor(path,col,0)

            selection = self.get_selection()
            model, treeiter = selection.get_selected()
            collectorName = model[treeiter][0]
            collector = self.engine.get_collector(collectorName)
            
            self.show_collector_popup_menu(event,collector)

    # Left pane responds to up/down arrow and tab key presses
    def key_release_handler(self, listBox, event):
        modifiers = Gtk.accelerator_get_default_mod_mask()
        reactivate_single = (event.state & modifiers) != Gdk.ModifierType.SHIFT_MASK if os.name == "nt" else (event.state & modifiers) == Gdk.ModifierType.SHIFT_MASK
       	print "event state:", event.state
       	print "modifiers:", modifiers

        print "Reactivate single:", reactivate_single

        # if (event.keyval == Gdk.KEY_Up or event.keyval == Gdk.KEY_Down or Gdk.KEY_Tab):
        #     collector = self.engine.get_collector(self.get_selected_row().get_name())
        #     if(self.get_selection_mode() == Gtk.SelectionMode.SINGLE):
        #         self.attached_gui.create_config_window(event,collector)
        if (event.keyval == Gdk.KEY_Up or event.keyval == Gdk.KEY_Down or Gdk.KEY_Tab):
            model, treeiter = self.get_selection().get_selected()
            collector = self.engine.get_collector(model[treeiter][0])

            self.attached_gui.create_config_window(event,collector)

        if(reactivate_single):
            # The next click will renable single selection
            print "activating single!!!!"
            self.connect("button-press-event",self.re_enable_single)

    # When CTRL is released, the next left click resets the list box to single selection mode.
    def re_enable_single(self, lBox, event):
        if(event.button == Gdk.BUTTON_PRIMARY):
        	self.disconnect_by_func(self.re_enable_single)
        	self.unselect_all()
        	self.set_selection_mode(Gtk.SelectionMode.SINGLE)

    # Create Gtk.TreeView() with collector information
    def create_collector_list(self):

        collector_liststore = Gtk.ListStore(str)

        for i, service in enumerate(self.engine.collectors):
            collector_liststore.append([service.name])
            self.collectorStatus[service.name] = False

        #treeview = Gtk.TreeView(collector_liststore)
        self.set_model(collector_liststore)

        cellRenderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Collectors", cellRenderer, text=0)
        self.append_column(column)

        self.set_activate_on_single_click(True)

        # This block not necessary
        select = self.get_selection()
        select.connect("changed", self.tree_selection_change_handler)

    # I think this is not necessary 
    def tree_selection_change_handler(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            print model[treeiter][0]
            #self.collector_listbox_handler(model[treeiter][0])


    # Show options over collector row on right click, select collector and create config window on left click
    def collector_listbox_handler(self, eventBox, event, collectorName):
        collector = self.engine.get_collector(collectorName)
        if(event.button == Gdk.BUTTON_SECONDARY): # right click
            self.show_collector_popup_menu(event,collector)

    # Toggle the clicked row if the selection mode is multiple
    def toggle_clicked_row(self, row):
        activate = not self.collectorStatus[row.get_name()]

        if(activate == True):
            self.select_row(row)
        if(activate == False):
            self.unselect_row(row)

        self.collectorStatus[row.get_name()] = activate
        self.update_row_colors(Gdk.Event(), row)

    # Return the Gtk.ListBoxRow() based on the its name (string)
    def get_row(self, name):
        row = filter(lambda r: r.get_name() == name, self.get_children())
        return row.pop()

    # Show the popup menu on right click
    def show_collector_popup_menu(self, event, collector):
        menu = Gtk.Menu()

        runItem = Gtk.MenuItem("Run " + collector.name)
        runItem.connect("activate", self.attached_gui.startIndividualCollector, collector)

        stopItem = Gtk.MenuItem("Stop " + collector.name)
        stopItem.connect("activate", self.attached_gui.stopIndividualCollector, collector)

        parseItem = Gtk.MenuItem("Parse " + collector.name + " data")
        parseItem.connect("activate", self.attached_gui.parser, collector)

        # manual collector should only be run by icon
        if (isinstance(collector, engine.collector.AutomaticCollector)):
            menu.append(runItem)
            menu.append(stopItem)

        menu.append(parseItem)

        menu.show_all()
        menu.popup(None, None, None, None, event.button, event.time)

        return True

    # Update background colors of collector rows based on isSelected()
    def update_row_colors(self, event, lBoxRow):
        self.foreach(self.update_row_color)

    # Helper for update_row_colors
    def update_row_color(self, row):
        if (row.is_selected()):
            row.get_style_context().add_class("active-color")
            row.get_style_context().remove_class("inactive-color")
        else:
            row.get_style_context().remove_class("active-color")
            row.get_style_context().add_class("inactive-color")

    # Runs when a Gtk.ListBoxRow() is activated
    # def row_activated_handler(self,lBox,lBoxRow):
    #     collector = self.engine.get_collector(lBoxRow.get_name())
    #     if(self.get_selection_mode() == Gtk.SelectionMode.SINGLE):
    #         self.select_row(lBoxRow)
    #         self.attached_gui.create_config_window(Gdk.Event(),collector)
    #     if(self.get_selection_mode() == Gtk.SelectionMode.MULTIPLE):
    #         if(lBoxRow.get_name() != self.attached_gui.get_current_config_window_name()):
    #             self.toggle_clicked_row(lBoxRow)
    #         if(not self.attached_gui.is_config_window_active()):
    #             self.attached_gui.create_config_window(Gdk.Event(), collector)
    #     self.update_row_colors(Gdk.Event(),lBoxRow)

    # Runs when a Gtk.TreeView row is activated
    def row_activated_handler(self, treeview, treepath, column):
        
        i = treepath.get_indices()[0]
        model = treeview.get_model()
        collector_name = model[i][0]

        print collector_name

        collector = self.engine.get_collector(collector_name)

        if(self.get_selection().get_mode() == Gtk.SelectionMode.SINGLE):
        #   self.select_row(lBoxRow)
            self.attached_gui.create_config_window(Gdk.Event(),collector)
        if(self.get_selection().get_mode() == Gtk.SelectionMode.MULTIPLE):
        #     if(collector_name() != self.attached_gui.get_current_config_window_name()):
        #         self.toggle_clicked_row(lBoxRow) #You need this function
            if(not self.attached_gui.is_config_window_active()):
                self.attached_gui.create_config_window(Gdk.Event(), collector)
        # self.update_row_colors(Gdk.Event(),lBoxRow)

    # Called by the start/stop all collector menu option in the staus icon menu. Updates the status of the collector rows when they are pressed.
    def update_collector_status(self, action, collectorName):
        row = filter(lambda r: r.get_name() == collectorName, self.get_children())
        if (row.__len__() > 0):
            collectorRow = row.pop()
            if (action == Action.RUN):
                self.select_row(collectorRow)
            if (action == Action.STOP):
                self.unselect_row(collectorRow)
            self.update_row_color(collectorRow)
