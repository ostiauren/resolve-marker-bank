import pathlib
def init():
    global bank_id_marker_name
    global databaseRoot
    global databaseFolder
    global bank_marker_color
    global default_new_marker_set_name
    global databaseSetExtention
    bank_id_marker_name = "BANK_ID_MARKER - DO NOT EDIT"
    bank_marker_color = "Red"
    databaseRoot = "/pool/resolve"
    databaseFolder = "marker_banks"
    databaseSetExtention = 'set'
    default_new_marker_set_name = "Untitled marker set"