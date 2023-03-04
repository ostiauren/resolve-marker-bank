#bank_id_marker_name = "BANK_ID_MARKER - DO NOT EDIT"

import globals


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


class marker_set():
    def __init__(self, input_marker_set):

        self.extract_marker_set(input_marker_set)
        # self._marker2 = self._marker(self)

    def extract_marker_set(self, input_marker_set):
        # Check if the passed marker set is just a normal Resolve marker set or a marker set read from file.
        # A marker set from file has the set info separated while the Resolve marker set has the set info as a marker
        if input_marker_set.get('set') is not None:
            # Marker set is from file. Separate marker set info and marker set
            print("Markers from Resolve")
            self.marker_set_info = [
                value for key, value in input_marker_set.items() if key not in 'set']
            self.marker_set = input_marker_set['set']

        else:
            print("Markers from file")
            info_marker_key = list(dict_extract(
                'name', input_marker_set)).index(globals.bank_id_marker_name)

            self.marker_set_info = input_marker_set[info_marker_key]
            self.marker_set = input_marker_set
            del self.marker_set[info_marker_key]

        # print ("self.marker_set_info", self.marker_set_info)
        # print ("self.marker_set", self.marker_set)

    def marker_info_dict():
        mydict = {
            'marker_start': 0,
            #'marker_color': 'Red',
            #'marker_duration': 1,
            'marker_set_name': 'VFX',
            #'name': 'BANK_ID_MARKER - DO NOT EDIT',
            'marker_set_uuid': '342f870e-3e4e-47b5-805f-e5c0852b5b9d',
            'timebase': '24',
            }

    def get_set(self):
        return self.marker_set

    def get_list(self):
        marker_set_list = []
        for row, i in enumerate(self.marker_set):
            marker_set_list.append ((
                i,
                self.marker_set[i]['duration'],
                self.marker_set[i]['name'],
                self.marker_set[i]['note'],
                self.marker_set[i]['color'],
                self.marker_set[i]['customData']))
        return marker_set_list

    def get_set_info(self):
        return self.marker_set_info

    def update_name(self, frame, name):
        self.marker_set[frame].update({'name': name})

    def get_marker(self, frame):

        class mrkr():
            def __init__(self, outer_instance):
                self.outer_instance=outer_instance
                self.marker_set=self.outer_instance.marker_set


        # def test(self):
         #   print ("?????????????????????????????????????")
        return self.marker_set[frame]








    def get_marker_list(self):
        # a = index(self.marker_set)
        # marker_list = []
        for count, i in enumerate(self.marker_set):
            a=i
        print("===-----------------------------", a)




    class _marker():
        def __init__(self, outer_instance):
            self.outer_instance=outer_instance
            self.marker_set=self.outer_instance.marker_set
            print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++jere")

        def p_marker(self, key):
            print("=====", self.marker_set[key])

my_markers_resolve={0: {'color': 'Red', 'duration': 1, 'note': 'VFX', 'name': 'BANK_ID_MARKER - DO NOT EDIT', 'customData': '342f870e-3e4e-47b5-805f-e5c0852b5b9d'}, 5197: {'color': 'Blue', 'duration': 1, 'note': '', 'name': 'Marker 2', 'customData': '4072054c-67b9-4923-bd2b-80f69daf7804'},
    6407: {'color': 'Blue', 'duration': 1, 'note': '', 'name': 'Marker 3', 'customData': '3de75f15-a6e3-41d9-a6de-c198d974f85a'}, 7417: {'color': 'Blue', 'duration': 1, 'note': '', 'name': 'Marker 4', 'customData': 'efa3101f-ee54-490c-9aa1-1ae32854c2b9'}}
my_markers_tmp={5197: {'color': 'Blue', 'duration': 1, 'note': '', 'name': 'Marker 2', 'customData': '4072054c-67b9-4923-bd2b-80f69daf7804'}, 6407: {'color': 'Blue', 'duration': 1, 'note': '',
    'name': 'Marker 3', 'customData': '3de75f15-a6e3-41d9-a6de-c198d974f85a'}, 7417: {'color': 'Blue', 'duration': 1, 'note': '', 'name': 'Marker 4', 'customData': 'efa3101f-ee54-490c-9aa1-1ae32854c2b9'}}
my_markers_file={'name': 'VFX', 'idx': 0, 'set': my_markers_tmp}

#globals.init()
#marker_set = marker_set(my_markers_resolve)
#marker_set=marker_set(my_markers_file)

#print("+++++", marker_set.get_set())
#print("+++++", marker_set.get_list())
#print ("+++++", marker_set.get_set_info())
# print ("+++++", marker_set.get_marker_list())
# marker_set.update_name(5197, 'This is the end')
# print ("=======", marker_set.get_set())

# print ("===", marker_set.get_marker(5197))
# print ("+++++", marker_set.get_marker(5197))
# a = marker_set._marker
# print (a)
