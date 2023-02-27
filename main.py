from PyQt5 import QtWidgets, uic
import sys
import qdarkstyle
from terminal import resolve
import pathlib

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

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        #uic.loadUi('basic.ui', self)
        uic.loadUi('tabletutorial3.ui', self)
        self.show()

        self._connect_to_resolve()
        self._get_current_timeline()
        self._get_markers()

        self.set_column_width()
        self.update_table()


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

        #Get updated markers and set heading label on GUI
        self.markers = self.timeline.GetMarkers()
        #self.timeline_label.configure(text = self.timeline.GetName())

    def set_column_width(self):
        widths = [100, 100, 150, 200, 80, 300]
        for i in range(len(widths)):
            self.tableWidget.setColumnWidth(i, widths[i])

    def update_table(self):

        # Delete all current rows
        for i in reversed(range(self.tableWidget.rowCount())):
            self.tableWidget.removeRow(i)
        #print (self.markers)
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