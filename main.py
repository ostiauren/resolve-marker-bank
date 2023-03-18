from PyQt5 import QtWidgets, uic
import sys
import qdarkstyle
from utils import *
import globals
globals.init()

main_widow_ui = 'Qt_main.ui'
dialog_input = 'Qt_dialog_input.ui'

class dialog_text_input(QtWidgets.QDialog): 
    def __init__(self, main, marker_uuid = None):
        self.main = main
        self.marker_uuid = marker_uuid
        QtWidgets.QDialog.__init__(self) #(self, parent)
        uic.loadUi(dialog_input, self)
        button_1 = self.button_1
        button_1.clicked.connect(self.button_1_callback)
        button_2 = self.button_2
        button_2.clicked.connect(self.button_2_callback)

    def button_1_callback(self):
        if self.main.rc.rename_bank_id(self.lineEdit.text(), self.main.marker_set.get_set_info()):
            # Get updated markers and update the interface
            self.main.get_markers_wrapper()
            self.main.timeline_selected()
        self.close()

    def button_2_callback(self):
        self.close()


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi(main_widow_ui, self)
        self.show()
        self.setWindowTitle("Resolve Marker Bank")
        
        self.config_callbacks()
        self.qt_overrides()

        self.rc = resolve_connection()

        self.project_changed()

        self.timeline = self.rc.project.GetCurrentTimeline()
        self.get_markers_wrapper()
        
        self.timeline_selected()


    def project_changed(self):
        self.project = self.rc.project
        self.project_uuid = self.rc.project.GetUniqueId() 
        self.project_name = self.rc.project.GetName() 
        self.project_name_label.setText(self.project_name)
        self.project_uuid_label.setText(self.project_uuid)

    def timeline_selected(self):
        self.update_table()
        self.update_combo()

        # Write timeline to database
        selected_timeline_uuid = self.timeline.GetUniqueId()
        update_database(selected_timeline_uuid, self.marker_set.get_marker_set_for_database())

    def config_callbacks(self):
        renameMarkerSetButton = self.renameMarkerSetButton
        renameMarkerSetButton.clicked.connect(self.callback_test_button)
        self.timelineCombo = self.timelineCombo
        self.timelineCombo.activated[int].connect(self.callback_timelineCombo)
        self.bankCombo = self.bankCombo
        self.bankCombo.activated[int].connect(self.callback_bankCombo)

  
    def popup_dialog(self, dialog_name, label, button_text_1, button_text_2):
        dialog = dialog_text_input(self)
        dialog.text_label.setText(label)
        dialog.button_1.setText(button_text_1)
        dialog.button_2.setText(button_text_2)
        dialog.lineEdit.setText(self.marker_set.get_set_name())
        dialog.lineEdit.selectAll()
        dialog.lineEdit.setFocus()
        dialog.exec_()
        dialog.deleteLater()
 
    def callback_test_button(self):
        print ("Pushed")
        self.popup_dialog("Name Marker Set", "This timeline has a unnamed marker set.\nPlease give it a name.", 'OK', 'Cancel')

    def get_markers_wrapper(self, selectedIndex=None):
        self.marker_set = marker_set()
        if selectedIndex == None:
            timeline_markers = self.rc.get_markers()
        else:
            timeline_markers = self.rc.get_markers(selectedIndex)
        if timeline_markers == None: #If the selected timeline does not have a marker_bank_id
            self.rc.add_bank_id() # Make bank_marker
        if selectedIndex == None:
            timeline_markers = self.rc.get_markers()
        else:
            timeline_markers = self.rc.get_markers(selectedIndex)
        self.marker_set.input_marker_set(timeline_markers, self.project_uuid)        

    def callback_timelineCombo(self, selectedIndex,):
        selectedIndex += 1  # Plus one on selectedIndex because Resolves timeline index starts on 1 not 0
        self.timeline = self.project.GetTimelineByIndex(selectedIndex)
        self.get_markers_wrapper(selectedIndex)
        self.timeline_selected()

    def callback_bankCombo(self, selectedIndex,):
        selectedIndex += 1  # Plus one on selectedIndex because Resolves timeline index starts on 1 not 0
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
                options.append("%s *" % i[1].GetName())
                selected_index = i[0]
            else:
                options.append("%s" % i[1].GetName())

        self.timelineCombo.addItems(options)
        selected_timeline_uuid = self.timeline.GetUniqueId()

        # Select current timeline in combobox
        selelcted_timeline_index = [index for (index, timelines) in enumerate(timelines) if timelines[2]==selected_timeline_uuid][0]
        self.timelineCombo.setCurrentIndex(selelcted_timeline_index)
        
        self.timeline_uuid_label.setText(selected_timeline_uuid)
        

    def qt_overrides(self):
        widths = [100, 100, 150, 200, 80, 300]
        for i in range(len(widths)):
            self.tableWidget.setColumnWidth(i, widths[i])
        
        self.timeline_uuid_label.setStyleSheet("QLabel {color: rgb(84, 104, 122);}")
        self.marker_set_uuid_label.setStyleSheet("QLabel {color: rgb(84, 104, 122);}")
        self.project_uuid_label.setStyleSheet("QLabel {color: rgb(84, 104, 122);}")
        self.marker_set_name_label.setStyleSheet("QLabel {color: rgb(84, 104, 122);}")

    def update_table(self):
        # Delete all current rows
        for i in reversed(range(self.tableWidget.rowCount())):
            self.tableWidget.removeRow(i)

        # Update marker name label
        self.marker_set_name_label.setText(self.marker_set.get_set_name()) 

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