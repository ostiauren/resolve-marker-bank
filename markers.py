#!/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk
import pathlib
import pygubu
from pygubu.widgets.editabletreeview import InplaceEditor
#from timecode import Timecode
from terminal import resolve
import uuid
import sys

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "markers.ui"

bank_id_marker_name = "BANK_ID_MARKER - DO NOT EDIT"

def frames_to_tc (frames, tc_base):
    hours = int(frames / (3600 * tc_base))
    minutes = int(frames / (60 * tc_base) % 60)
    seconds = int(frames / tc_base % 60)
    frames = int(frames % tc_base)
    return "%02d:%02d:%02d:%02d" % (hours, minutes, seconds, frames)




def dict_extract(key, var):
    if hasattr(var,'items'):
        for k, v in var.items():
            if k == key:
                yield v
            if isinstance(v, dict):
                for result in dict_extract(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in dict_extract(key, d):
                        yield result






class EditableTreeviewDemoApp:
    def __init__(self, master=None):
        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(PROJECT_PATH)
        builder.add_from_file(PROJECT_UI)
        self.mainwindow = builder.get_object("toplevel1", master)
        self.pycombo = builder.get_object('combobox1')
        self.timeline_label = builder.get_object('timeline_label')
        self.bank_label = builder.get_object('bank_label')
        self.etv = builder.get_object("etv")

        # Set the "Allow Edit" check box to off
        self.allow_edit = None
        builder.import_variables(self, ["allow_edit"])
        self.allow_edit.set(False)

        builder.connect_callbacks(self)

        self.count = 0

        self._connect_to_resolve()
        self._get_current_timeline()
        self._get_markers()

        self._update_combo()
        self._update_treewidget()


    def get_timelines(self):
        timelines = []
        timeline_count = self.project.GetTimelineCount()
        for i in range(timeline_count):
            timeline = self.project.GetTimelineByIndex(i+1)
            if self.resolve_version == 17:
                timelines.append((i, timeline, 1234))
            else:
                timelines.append((i, timeline, timeline.GetUniqueId()))
        return timelines


    def _update_combo(self):
        options = []
        timelines = self.get_timelines()

        # Get index of current timeline
        if self.resolve_version == 17:
            current_timeline_index = 1
        else:
            current_timeline_uuid = self.project.GetCurrentTimeline().GetUniqueId()
            current_timeline_index = [index for (index, timelines) in enumerate(timelines) if timelines[2]==current_timeline_uuid][0]

        # Update combobox with timelines
        for i in timelines:
            if i[0] == current_timeline_index:
                options.append((i[0], "%s - Current Timeline" % i[1].GetName()))
            else:
                options.append((i[0], "%s" % i[1].GetName()))

        self.pycombo.configure(values=options)

        # Select current timeline in combobox
        self.pycombo.set(current_timeline_index)

    def _connect_to_resolve(self):
        self.resolveApp = resolve.resolveObject
        print ("Resolve version:", self.resolveApp.GetVersion())

        self.resolve_version = self.resolveApp.GetVersion()

        # Get Resolve verson (17.4 and higher or 18 and higher)
        if self.resolve_version[0] == 17:
            if self.resolve_version[1] >= 4:
                self.resolve_version =17
        elif self.resolve_version[0] >= 18:
            self.resolve_version = 18

        self.pm = self.resolveApp.GetProjectManager()
        self.project = self.pm.GetCurrentProject()
        print ("Current project:", self.project.GetName())

    def _get_current_timeline(self):
        self.timeline = self.project.GetCurrentTimeline()
        if not self.timeline:
            print ("The current project does not have any open timelines")
            sys.exit()
        
        print ("The current timeline is:", self.timeline.GetName())

    def _get_markers(self):
        #self.markers = self.timeline.GetMarkers()
        #for i in self.markers:
        #    self.timeline.sUpdateMarkerCustomData(i, '')

        #Get markers and update customData if it's empty

        markers = self.timeline.GetMarkers()
        #Add UUID to Custom Data field
        '''
        for i in markers:
            if markers[i]['customData'] == '':
                if self.timeline.UpdateMarkerCustomData(i, str(uuid.uuid4())):
                    print ("A custom data field was updated")
                else:
                    print ("Somethin went wrong. A custom data field could not be updated")

        # Add BANK_MARKER if the Timeline does not have one. Try insert on first available frame < 11.
        
        '''
        # Check if there is a bank_id_marker in the timeline, and if not make one on  the first available position in the timeline.
        if bank_id_marker_name not in list(dict_extract('name', markers)):
            for count, i in enumerate(markers):
                if count < i:
                    if self.timeline.AddMarker(count, 'Red', bank_id_marker_name, 'VFX', 1, str(uuid.uuid4())):
                        print ("A bank ID marker was added")
                    else:
                        print ("A bank ID could not be added")
                    break

    

 

        #Get updated markers and heading label on GUI
        self.markers = self.timeline.GetMarkers()
        self.timeline_label.configure(text = self.timeline.GetName())

    def _update_treewidget(self):
        # Delete entries from old timeline
        for i in self.etv.get_children():
            self.etv.delete(i)

        # Add entires from current timeline
        timeline_framerate =  self.timeline.GetSetting('timelineFrameRate')
        count = 0
        for i in self.markers:
            if self.markers[i]['name'] != bank_id_marker_name:           
                self.etv.insert("", tk.END, text = count+1, values = (
                frames_to_tc(i, timeline_framerate),
                frames_to_tc(self.markers[i]['duration'], timeline_framerate),
                self.markers[i]['name'],
                self.markers[i]['note'],
                self.markers[i]['color'],
                self.markers[i]['customData']
                ))
                count += 1
            else:
                #self.bank_label = self.markers[i]['name']
                self.bank_label.configure(text = self.markers[i]['note'])
                
                pass
    def run(self):
        self.mainwindow.mainloop()

    def combo_selected(self, event=None):
        timelineIndex = self.pycombo.get()
        print ("Timeline %s selected." % (timelineIndex+1))
        self.timeline = self.project.GetTimelineByIndex(timelineIndex+1)
        self._get_markers()
        self._update_treewidget()

    def on_cell_edited(self, event=None):
        # This method is connected with the <<TreeviewCellEdited>>
        # virtual event of the Editabletreeview
        col, item = self.etv.get_event_info()
        msg = f"Column {col} of item {item} was changed"
        print(msg)
        data = self.etv.item(item, "values")
        print("New values:", data)

        # Test get_value method
        print(f"Column '{col}' value: ", self.etv.get_value(col, item))

    def on_inplace_edit(self, event=None):
        # This method is connected with the <<TreeviewInplaceEdit>>
        # virtual event of the Editabletreeview
        #
        # Get the column id and item id of the cell
        # that is going to be edited
        col, item = self.etv.get_event_info()
        # Allow edition only if allow_edit variable is checked
        if self.allow_edit.get():
            # Define the widget editor to be used to edit the column value
            if col in ("col_name",):
                self.etv.inplace_entry(col, item)
            if col in ("col_note",):
                self.etv.inplace_entry(col, item)

    def on_row_selected(self, event=None):

        # This method is connected with the <<TreeviewSelect>> event
        # The Editabletreeview also uses this event so, Do not forget to
        # mark Add=True in the binding definition

        sel = self.etv.selection()
        if sel:
            item = sel[0]
            print(f"Row item {item} was selected.")

    def on_editors_unfocused(self, event=None):
        # user clicked in treeview area with no rows
        # the editors where hidden.
        print("Editors hidden")

if __name__ == "__main__":
    app = EditableTreeviewDemoApp()
    app.run()