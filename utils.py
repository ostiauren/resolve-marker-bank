#bank_id_marker_name = "BANK_ID_MARKER - DO NOT EDIT"

import globals
import sys
from terminal import resolve
import uuid
from pathlib import Path
import os
import ast
import shutil
import time



def update_database(timelineFolder, marker_set):
    databaseLocation = globals.databaseRoot + "/" + globals.databaseFolder
    marker_set_UUID = marker_set['uuid']

    #Make timeline folder (all parent folders will be made if they don't exist)
    timelineFolder = databaseLocation + "/" + marker_set['project_uuid'] + "/" + timelineFolder
    
    try:
        Path(timelineFolder).mkdir(parents=True, exist_ok=True)
        print("folder '{}' created ".format(timelineFolder))
    except FileExistsError:
        print("folder {} already exists".format(timelineFolder))
    

    fileName = marker_set_UUID + "." + globals.databaseSetExtention
    filePath = timelineFolder + "/" + fileName
    backups_folder = timelineFolder + '/backups'
    if not os.path.isfile(filePath):
        print ("No marker set for this timeline exist. Adding to database.")
        print (marker_set)
        try:
            with open(filePath, 'w') as file:
                file.write(str(marker_set))
        except FileNotFoundError:
            print("No such {} file or directory.".format(timelineFolder))
            sys.exit()
    else:
        file_markers = ast.literal_eval(open(filePath).read())
        
        if file_markers == marker_set:
            print ("Maker set is the same as in database. No update made.")
        else:
            print ("Marker set is NOT the same as in database. Updating marker set.")
            # Make backup folder if it does not exsist.
            
            try:
                Path(backups_folder).mkdir(parents=True, exist_ok=True)
                print("Folder '{}' for backups created or allready exsisted".format(backups_folder))
            except:
                print("Folder '{}' for backups could not be created ".format(backups_folder))
                sys.exit()
            shutil.move(filePath, backups_folder + "/" +  str(time.time()) + "-" + fileName)
            try:
                with open(filePath, 'w') as file:
                    file.write(str(marker_set))
            except FileNotFoundError:
                print("No such {} file or directory.".format(timelineFolder))
                sys.exit()
            # Write code to backup and update markers
            


def get_database_marker_sets(projectUUID, timelineUUID):
    databaseLocation = globals.databaseRoot + "/" + globals.databaseFolder
    timelineFolder = databaseLocation + "/" + projectUUID + "/" + timelineUUID
    marker_sets = []
    
    for filename in os.listdir(timelineFolder):
        if filename.endswith("." + globals.databaseSetExtention):
            try:
                with open(timelineFolder + "/" + filename) as file:
                    file_content = ast.literal_eval(file.read())
                    marker_sets.append((file_content['uuid'] ,file_content['name']))
            except FileNotFoundError:
                print("No such {} file or directory.".format(timelineFolder + "/" + filename))
                sys.exit()
    return marker_sets

def get_database_marker_set(projectUUID, timelineUUID, markerSetUUID):
    databaseLocation = globals.databaseRoot + "/" + globals.databaseFolder
    markerSetPath = databaseLocation + "/" + projectUUID + "/" + timelineUUID + "/" + markerSetUUID + "." + globals.databaseSetExtention
    try:
        with open(markerSetPath) as file:
            file_content = ast.literal_eval(file.read())
    except FileNotFoundError:
        print("No such {} file or directory.".format(markerSetPath))
        sys.exit()
    return file_content



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

        if globals.bank_id_marker_name not in list(dict_extract('name', markers)):
            return None
        else:
            return self.timeline.GetMarkers()

    def add_bank_id(self):
        markers = self.timeline.GetMarkers()
        # Add bank_id_marker to the timeline. If timeline does not have any markers add one the first available frame 
        if globals.bank_id_marker_name not in list(dict_extract('name', markers)):
            # Check if there are makers. If there are, check for and make bank_id_make. If there are no markers, just make a mank ID marker at index 0.
            if markers:
                for count, i in enumerate(markers):
                    if count < i:
                        if self.timeline.AddMarker(count, 'Red', globals.bank_id_marker_name, globals.default_new_marker_set_name, 1, str(uuid.uuid4())):
                            print ("A bank ID marker was added")
                        else:
                            print ("A bank ID could not be added") 
                        break
            else:
                if self.timeline.AddMarker(0, 'Red', globals.bank_id_marker_name, globals.default_new_marker_set_name, 1, str(uuid.uuid4())):
                    print ("A bank ID marker was added")
                else:
                    print ("A bank ID could not be added")      

        #Get updated markers and set heading label on GUI
        return self.timeline.GetMarkers()

    def commit_changes(self, marker_set):
        new_name = marker_set.marker_set_info.get('new_name')
        print ("new_name", new_name)
        if new_name:

            if new_name == marker_set.marker_set_info['name']:
                print ("The new marker set name ('%s') is the same as the old. No change made." % new_name)
                return
            else:
                print ("Renameing the marker set from '%s' to '%s'." % (marker_set.marker_set_info['name'], new_name))
                set_marker = self.timeline.GetMarkerByCustomData(marker_set.marker_set_info['uuid'])
                set_marker['note'] = new_name
                if self.timeline.DeleteMarkerByCustomData(marker_set.marker_set_info['uuid']):
                    print ("Marker deleted")
                if self.timeline.AddMarker(marker_set.marker_set_info['position'], set_marker['color'], set_marker['name'], set_marker['note'], set_marker['duration'], set_marker['customData']):
                    print ("Marker added")
                return True    

def get_current_timeline(self):
    self.timeline = self.project.GetCurrentTimeline()
    if not self.timeline:
        print ("The current project does not have any open timelines")
        sys.exit()
    print ("The current timeline is:", self.timeline.GetName())

class marker_set:
    def __init__(self):
        pass

    def input_marker_set(self, marker_set, project_uuid):
        self.input_marker_set =  marker_set
        self.project_uuid = project_uuid
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
                'uuid': input_marker_set[info_marker_key]['customData'],
                'project_uuid': self.project_uuid
                }
            self.markers = input_marker_set
            del self.markers[info_marker_key]

    def get_marker_set_as_resolve_dict(self):
        bank_marker = {
            'color': globals.bank_marker_color,
            'duration': 1,
            'note': self.marker_set_info['name'],
            'name': globals.bank_id_marker_name,
            'customData': self.marker_set_info['uuid']
            }
        self.markers[self.marker_set_info['position']] = bank_marker
        return self.markers

    def get_marker_set_for_resolve(self):
        info_marker = (
            self.marker_set_info[0],
            globals.bank_marker_color,
            globals.bank_id_marker_name,
            self.marker_set_info[1],
            1,
            self.marker_set_info[2],
        )
        marker_set_list = [(info_marker)]
        for row, i in enumerate(self.markers):
            marker_set_list.append ((
                i,
                self.markers[i]['color'],
                self.markers[i]['name'],
                self.markers[i]['note'],
                self.markers[i]['duration'],
                self.markers[i]['customData']))
        return marker_set_list

    def get_marker_set_for_database(self):
        database_set = dict(self.marker_set_info)
        database_set['set'] = self.markers
        return database_set

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

    def get_set_name(self):
        return self.marker_set_info['name']

    def update_name(self, frame, name):
        self.markers[frame].update({'name': name})

    def rename_set(self, new_name):
        print ("rename_set 1")
        self.marker_set_info['new_name'] = new_name
        return True

    def get_marker(self, frame):
        return self.markers[frame]




my_markers_resolve={0: {'color': 'Red', 'duration': 1, 'note': 'VFX', 'name': 'BANK_ID_MARKER - DO NOT EDIT', 'customData': '342f870e-3e4e-47b5-805f-e5c0852b5b9d'}, 5197: {'color': 'Blue', 'duration': 1, 'note': '', 'name': 'Marker 2', 'customData': '4072054c-67b9-4923-bd2b-80f69daf7804'},
    6407: {'color': 'Blue', 'duration': 1, 'note': '', 'name': 'Marker 3', 'customData': '3de75f15-a6e3-41d9-a6de-c198d974f85a'}, 7417: {'color': 'Blue', 'duration': 1, 'note': '', 'name': 'Marker 4', 'customData': 'efa3101f-ee54-490c-9aa1-1ae32854c2b9'}}
my_markers_tmp={5197: {'color': 'Blue', 'duration': 1, 'note': '', 'name': 'Marker 2', 'customData': '4072054c-67b9-4923-bd2b-80f69daf7804'}, 6407: {'color': 'Blue', 'duration': 1, 'note': '',
    'name': 'Marker 3', 'customData': '3de75f15-a6e3-41d9-a6de-c198d974f85a'}, 7417: {'color': 'Blue', 'duration': 1, 'note': '', 'name': 'Marker 4', 'customData': 'efa3101f-ee54-490c-9aa1-1ae32854c2b9'}}
my_markers_file={'position': 0, 'name': 'VFX', 'uuid': '3de75f15-a6e3-41d9-a6de-c198d974f85a', 'project_uuid': '4ab11e24-a6e3-41d9-a6de-d218d953f65b', 'set': my_markers_tmp}

#globals.init()
#project_Uuid = "4d577f17-a6e3-41d9-a6de-c198d973f84b"

#marker_set = marker_set()
#marker_set.input_marker_set(my_markers_resolve)
#marker_set = marker_set(my_markers_resolve)

#my_marker_set = marker_set()
#my_marker_set = my_marker_set.input_marker_set(my_markers_file, project_Uuid)

#print("+++++", marker_set.get_marker_set_for_database())
#print("+++++", marker_set.get_list())
#print ("+++++", marker_set.get_set_info())

# marker_set.update_name(5197, 'This is the end')
# print ("=======", marker_set.get_set())

# print ("===", marker_set.get_marker(5197))
# print ("+++++", marker_set.get_marker(5197))
# a = marker_set._marker
# print (a)
