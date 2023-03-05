#bank_id_marker_name = "BANK_ID_MARKER - DO NOT EDIT"

import globals
import sys
from terminal import resolve
import uuid

def frames_to_tc(frames, tc_base):
    hours = int(frames / (3600 * tc_base))
    minutes = int(frames / (60 * tc_base) % 60)
    seconds = int(frames / tc_base % 60)
    frames = int(frames % tc_base)
    return "%02d:%02d:%02d:%02d" % (hours, minutes, seconds, frames)


def dict_extract(key, var):
    if hasattr(var, 'items'):
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


class resolve_connection():
    def __init__(self):
        self._connect_to_resolve()

    def _connect_to_resolve(self):
        print ("Connecting to Resolve")
        self.resolveApp = resolve.resolveObject
        print ("Resolve version:", self.resolveApp.GetVersion())

        resolve_version = self.resolveApp.GetVersion()

        # Get Resolve verson (17.4 and higher or 18 and higher)
        if resolve_version[0] == 17:
            if resolve_version[1] >= 4:
                resolve_version =17
        elif resolve_version[0] >= 18:
            resolve_version = 18

        self.pm = self.resolveApp.GetProjectManager()
        self.project = self.pm.GetCurrentProject()
        print ("Current project:", self.project.GetName())
        self.timeline = self.project.GetCurrentTimeline()

    def timelines_list(self):
        timelines = []
        timeline_count = self.project.GetTimelineCount()
        for i in range(timeline_count):
            timeline = self.project.GetTimelineByIndex(i+1)
            timelines.append((i, timeline, timeline.GetUniqueId()))
        return timelines

    def get_markers(self, idx = None):
        #Get markers and update customData if it's empty
        if idx != None:
            self.timeline = self.project.GetTimelineByIndex(idx)
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
            if self.timeline.AddMarker(0, 'Red', globals.bank_id_marker_name, 'VFX', 1, str(uuid.uuid4())):
                print ("A bank ID marker was added")
            else:
                print ("A bank ID could not be added") 
        else:    
            if globals.bank_id_marker_name not in list(dict_extract('name', markers)):
                for count, i in enumerate(markers):
                    if count < i:
                        if self.timeline.AddMarker(count, 'Red', globals.bank_id_marker_name, 'VFX', 1, str(uuid.uuid4())):
                            print ("A bank ID marker was added")
                        else:
                            print ("A bank ID could not be added") 
                        break

        #Get updated markers and set heading label on GUI
        return self.timeline.GetMarkers()

def get_current_timeline(self):
    self.timeline = self.project.GetCurrentTimeline()
    if not self.timeline:
        print ("The current project does not have any open timelines")
        sys.exit()
    print ("The current timeline is:", self.timeline.GetName())

class marker_set:
    def __init__(self):
        pass

    def input_marker_set(self, marker_set):
        self.input_marker_set =  marker_set
        self.extract_marker_set(self.input_marker_set)

    def extract_marker_set(self, input_marker_set):
        # Check if the passed marker set is just a normal Resolve marker set or a marker set read from file.
        # A marker set from file has the set info separated while the Resolve marker set has the set info as a marker
        if input_marker_set.get('set') is not None:
            # Marker set is from file. Separate marker set info and marker set
            print("Markers from file")
            self.marker_set_info = [value for key, value in input_marker_set.items() if key not in 'set']
            self.markers = input_marker_set['set']
            
        else:
            print("Markers from Resolve")
            info_marker_key = list(dict_extract(
                'name', input_marker_set)).index(globals.bank_id_marker_name)
            self.marker_set_info = {
                'position': info_marker_key,
                'name': input_marker_set[info_marker_key]['note'],
                'uuid': input_marker_set[info_marker_key]['customData']
                }
            self.markers = input_marker_set
            del self.markers[info_marker_key]

    def get_marker_set_for_resolve(self):
        bank_marker = {
            'color': globals.bank_marker_color,
            'duration': 1,
            'note': self.marker_set_info['name'],
            'name': globals.bank_id_marker_name,
            'customData': self.marker_set_info['uuid']
            }
        self.markers[self.marker_set_info['position']] = bank_marker
        return self.markers
    
    def get_marker_set_for_database(self):
        pass

    def get_markers_as_list(self):
        marker_set_list = []
        for row, i in enumerate(self.markers):
            marker_set_list.append ((
                i,
                self.markers[i]['duration'],
                self.markers[i]['name'],
                self.markers[i]['note'],
                self.markers[i]['color'],
                self.markers[i]['customData']))
        return marker_set_list

    def get_set_info(self):
        return self.marker_set_info

    def update_name(self, frame, name):
        self.markers[frame].update({'name': name})

    def get_marker(self, frame):
        return self.markers[frame]




my_markers_resolve={0: {'color': 'Red', 'duration': 1, 'note': 'VFX', 'name': 'BANK_ID_MARKER - DO NOT EDIT', 'customData': '342f870e-3e4e-47b5-805f-e5c0852b5b9d'}, 5197: {'color': 'Blue', 'duration': 1, 'note': '', 'name': 'Marker 2', 'customData': '4072054c-67b9-4923-bd2b-80f69daf7804'},
    6407: {'color': 'Blue', 'duration': 1, 'note': '', 'name': 'Marker 3', 'customData': '3de75f15-a6e3-41d9-a6de-c198d974f85a'}, 7417: {'color': 'Blue', 'duration': 1, 'note': '', 'name': 'Marker 4', 'customData': 'efa3101f-ee54-490c-9aa1-1ae32854c2b9'}}
my_markers_tmp={5197: {'color': 'Blue', 'duration': 1, 'note': '', 'name': 'Marker 2', 'customData': '4072054c-67b9-4923-bd2b-80f69daf7804'}, 6407: {'color': 'Blue', 'duration': 1, 'note': '',
    'name': 'Marker 3', 'customData': '3de75f15-a6e3-41d9-a6de-c198d974f85a'}, 7417: {'color': 'Blue', 'duration': 1, 'note': '', 'name': 'Marker 4', 'customData': 'efa3101f-ee54-490c-9aa1-1ae32854c2b9'}}
my_markers_file={'position': 0, 'name': 'VFX', 'uuid': '3de75f15-a6e3-41d9-a6de-c198d974f85a', 'set': my_markers_tmp}

#globals.init()
#marker_set = marker_set()
#marker_set.read_marker_set(my_markers_resolve)
#marker_set = marker_set(my_markers_resolve)
#marker_set=marker_set(my_markers_file)

#print("+++++", marker_set.get_set())
#print("+++++", marker_set.get_list())
#print ("+++++", marker_set.get_set_info())

# marker_set.update_name(5197, 'This is the end')
# print ("=======", marker_set.get_set())

# print ("===", marker_set.get_marker(5197))
# print ("+++++", marker_set.get_marker(5197))
# a = marker_set._marker
# print (a)
