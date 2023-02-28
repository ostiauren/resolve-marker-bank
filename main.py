from PyQt5 import QtWidgets, uic
import sys
import qdarkstyle
from terminal import resolve
import pathlib
import uuid
import os
import json
import ast
PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "markers.ui"

bank_id_marker_name = "BANK_ID_MARKER - DO NOT EDIT"

databaseRoot = "/pool/resolve"
databaseFolder = "marker_banks"


def update_database(timelineFolder, markers):
    #Make database folder if we dont have one
    databaseLocation = databaseRoot + "/" + databaseFolder
    if not os.path.exists(databaseLocation):
        os.makedirs(databaseLocation)

    timelineFolder = databaseLocation + "/" + timelineFolder
    if not os.path.exists(timelineFolder):
        os.makedirs((timelineFolder))

    # Get UUID of marker with ban_id_maker_name string
    marker_index = list(dict_extract('name', markers)).index(bank_id_marker_name)
    markerUUID = markers[marker_index]['customData']

    # Check if an existing maker set exist and if so, is it different.
    filepath = timelineFolder + "/" + markerUUID
    if not os.path.exists(filepath):
        print ("No marker set for this timeline exist. Adding to database.")
        with open(filepath, 'w') as file:
            file.write(str(markers))
    else:
        file_markers = ast.literal_eval(open(filepath).read())
        if file_markers == markers:
            print ("Maker set is the same as in database. No update made.")
        else:
            print ("Marker set is NOT the same as in database. Updating marker set.")
            # Write code to backup and update markers

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

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('Qt_main.ui', self)
        self.show()

        self.config_callbacks()
        self.set_column_width()

        self._connect_to_resolve()
        self._get_current_timeline()
        self.timeline_selected()


    def timeline_selected(self):
        self.timelines = self.get_timelines()        
        self.get_markers()
        self.update_table()
        self.update_combo()

        # Write timeline to database

        selected_timeline_uuid = self.timeline.GetUniqueId()
        update_database(selected_timeline_uuid, self.markers)

    def config_callbacks(self):
        testButton = self.testButton
        testButton.clicked.connect(self.callback_test_button)

        self.timelineCombo = self.timelineCombo
        self.timelineCombo.activated[int].connect(self.callback_timelineCombo)

        self.bankCombo = self.bankCombo
        self.timelineCombo.activated[int].connect(self.callback_bankCombo)

    def callback_test_button(self):
        print ("Pushed")

    def callback_timelineCombo(self, selectedIndex,):
        print ("Selected", selectedIndex)
        self.selectedTimelineIdx = selectedIndex+1

        self.timeline = self.project.GetTimelineByIndex(selectedIndex+1)
        self.timeline_selected()

    def callback_bankCombo(self, selectedIndex,):
        print ("Selected", selectedIndex)
        self.timeline = self.project.GetTimelineByIndex(selectedIndex+1)

    def _connect_to_resolve(self):
        print ("Connecting to Resolve")
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

    def update_combo(self):
        self.timelineCombo.clear()
        options = []

        # Get index of current timeline
        if self.resolve_version == 17:
            current_timeline_index = 1
        else:
            current_timeline_uuid = self.project.GetCurrentTimeline().GetUniqueId()
            # Current_timeline_index is the timline currently open in Resolve, not the currently selected timeline in the combobox
            current_timeline_index = [index for (index, timelines) in enumerate(self.timelines) if timelines[2]==current_timeline_uuid][0]
        # Update combobox with timelines
        for i in self.timelines:
            if i[0] == current_timeline_index:
                options.append("%s - Current Timeline" % i[1].GetName())
                selected_index = i[0]
            else:
                options.append("%s" % i[1].GetName())

        self.timelineCombo.addItems(options)
        selected_timeline_uuid = self.timeline.GetUniqueId()

        # Select current timeline in combobox
        selelcted_timeline_index = [index for (index, self.timelines) in enumerate(self.timelines) if self.timelines[2]==selected_timeline_uuid][0]
        self.timelineCombo.setCurrentIndex(selelcted_timeline_index)

    def add_bank_id_marker(self, index):
        if self.timeline.AddMarker(index, 'Red', bank_id_marker_name, 'VFX', 1, str(uuid.uuid4())):
            print ("A bank ID marker was added")
        else:
            print ("A bank ID could not be added")        


    def get_markers(self):
        #Get markers and update customData if it's empty
        markers = self.timeline.GetMarkers()

        #Add UUID to Custom Data field if empty
        for i in markers:
            if markers[i]['customData'] == '':
                if self.timeline.UpdateMarkerCustomData(i, str(uuid.uuid4())):
                    print ("A custom data field was updated")
                else:
                    print ("Somethin went wrong. A custom data field could not be updated")

        # Add bank_id_marker to the timeline. If timeline does not have any markers add one at index 0, else check for next available index and add one 
        if not bool(markers):
            self.add_bank_id_marker(0)
        else:    
            if bank_id_marker_name not in list(dict_extract('name', markers)):
                for count, i in enumerate(markers):
                    if count < i:
                        self.add_bank_id_marker(count)
                        break

        #Get updated markers and set heading label on GUI
        self.markers = self.timeline.GetMarkers()

    def set_column_width(self):
        widths = [100, 100, 150, 200, 80, 300]
        for i in range(len(widths)):
            self.tableWidget.setColumnWidth(i, widths[i])

    def update_table(self):
        # Delete all current rows
        for i in reversed(range(self.tableWidget.rowCount())):
            self.tableWidget.removeRow(i)
        markers = self.timeline.GetMarkers()

        # Don't count bank_id_marker_name marker if it excists 
        if bank_id_marker_name not in list(dict_extract('name', self.timeline.GetMarkers())):
            self.tableWidget.setRowCount(len(self.markers))
        else:
            self.tableWidget.setRowCount(len(self.markers)-1)

        timeline_framerate =  self.timeline.GetSetting('timelineFrameRate')

        for row, i in enumerate(self.markers):
            if self.markers[i]['name'] != bank_id_marker_name:  
                self.tableWidget.setItem(row-1, 0, QtWidgets.QTableWidgetItem(frames_to_tc(i, timeline_framerate)))
                self.tableWidget.setItem(row-1, 1, QtWidgets.QTableWidgetItem(frames_to_tc(self.markers[i]['duration'], timeline_framerate)))
                self.tableWidget.setItem(row-1, 2, QtWidgets.QTableWidgetItem(self.markers[i]['name']))
                self.tableWidget.setItem(row-1, 3, QtWidgets.QTableWidgetItem(self.markers[i]['note']))
                self.tableWidget.setItem(row-1, 4, QtWidgets.QTableWidgetItem(self.markers[i]['color']))
                self.tableWidget.setItem(row-1, 5, QtWidgets.QTableWidgetItem(self.markers[i]['customData']))
                self.tableWidget.resizeRowsToContents()

            else:
                # Update bank label
                #self.bank_label.configure(text = self.markers[i]['note'])
                pass


app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.setStyleSheet(qdarkstyle.load_stylesheet())
app.exec_()