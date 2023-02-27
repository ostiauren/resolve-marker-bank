from terminal.connect import load_fusionscript

def getResolve() -> "PyRemoteResolve":
    print ("main.py getResolve()")
    load_fusionscript()
    import fusionscript as dvr_script

    return dvr_script.scriptapp("Resolve")
    
resolveObject: "PyRemoteResolve" = getResolve()

