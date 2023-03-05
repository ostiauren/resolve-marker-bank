from PyQt5 import QtWidgets, uic
import sys
import qdarkstyle
from terminal import resolve
import uuid
import os
import ast
from utils import *

import globals
globals.init()

ui_file = 'Qt_main.ui'

def update_database(timelineFolder, markers):
    #Make database folder if we dont have one
    databaseLocation = globals.databaseRoot + "/" + globals.databaseFolder
    if not os.path.exists(databaseLocation):
        os.makedirs(databaseLocation)

    timelineFolder = databaseLocation + "/" + timelineFolder
    if not os.path.exists(timelineFolder):
        os.makedirs((timelineFolder))

    for i in markers:
        if markers[i]['name'] == globals.bank_id_marker_name:
            markerUUID = markers[i]['customData']
            break
    
    # Check if an existing maker set exist and if so,get it different.
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


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi(ui_file, self)
        self.show()

        self.config_callbacks()
        self.set_column_width()

        self.rc = resolve_connection()
        self.project = self.rc.project
        self.timeline = self.rc.project.GetCurrentTimeline()

        self.marker_set = marker_set()
        self.marker_set.input_marker_set(self.rc.get_markers())

        self.timeline_selected()



    def timeline_selected(self):
        self.update_table()
        self.update_combo()

        # Write timeline to database
        selected_timeline_uuid = self.timeline.GetUniqueId()
        update_database(selected_timeline_uuid, self.marker_set.get_marker_set_for_resolve())

    def config_callbacks(self):
        testButton = self.testButton
        testButton.clicked.connect(self.callback_test_button)
        self.timelineCombo = self.timelineCombo
        self.timelineCombo.activated[int].connect(self.callback_timelineCombo)
        self.bankCombo = self.bankCombo
        self.bankCombo.activated[int].connect(self.callback_bankCombo)

    def callback_test_button(self):
        print ("Pushed")

    def callback_timelineCombo(self, selectedIndex,):
        print ("callback_timelineCombo - Selected", selectedIndex)
        self.timeline = self.project.GetTimelineByIndex(selectedIndex+1)
        self.marker_set = marker_set()
        self.marker_set.input_marker_set(self.rc.get_markers(selectedIndex+1))
        self.timeline_selected()

    def callback_bankCombo(self, selectedIndex,):
        print ("callback_bankCombo - Selected", selectedIndex)
        #self.timeline = self.project.GetTimelineByIndex(selectedIndex+1)

    def update_combo(self):
        timelines = self.rc.timelines_list()
        self.timelineCombo.clear()
        options = []

        # Get index of current timeline
        current_timeline_uuid = self.project.GetCurrentTimeline().GetUniqueId()

        # Current_timeline_index is the timline currently open in Resolve, not the currently selected timeline in the combobox
        current_timeline_index = [index for (index, timelines) in enumerate(timelines) if timelines[2]==current_timeline_uuid][0]
        # Update combobox with timelines
        for i in timelines:
            if i[0] == current_timeline_index:
                options.append("%s - Current Timeline" % i[1].GetName())
                selected_index = i[0]
            else:
                options.append("%s" % i[1].GetName())

        self.timelineCombo.addItems(options)
        selected_timeline_uuid = self.timeline.GetUniqueId()

        # Select current timeline in combobox
        selelcted_timeline_index = [index for (index, timelines) in enumerate(timelines) if timelines[2]==selected_timeline_uuid][0]
        self.timelineCombo.setCurrentIndex(selelcted_timeline_index)
        
    def set_column_width(self):
        widths = [100, 100, 150, 200, 80, 300]
        for i in range(len(widths)):
            self.tableWidget.setColumnWidth(i, widths[i])

    def update_table(self):
        # Delete all current rows
        for i in reversed(range(self.tableWidget.rowCount())):
            self.tableWidget.removeRow(i)

        timeline_framerate =  self.timeline.GetSetting('timelineFrameRate')
        markers = self.marker_set.get_markers_as_list()
        self.tableWidget.setRowCount(len(markers))
        for row, i in enumerate(markers):
            self.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(frames_to_tc(i[0], timeline_framerate)))
            self.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(frames_to_tc(i[1], timeline_framerate)))
            self.tableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem(i[2]))
            self.tableWidget.setItem(row, 3, QtWidgets.QTableWidgetItem(i[3]))
            self.tableWidget.setItem(row, 4, QtWidgets.QTableWidgetItem(i[4]))
            self.tableWidget.setItem(row, 5, QtWidgets.QTableWidgetItem(i[5]))
        self.tableWidget.resizeRowsToContents()


app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.setStyleSheet(qdarkstyle.load_stylesheet())
app.exec_()