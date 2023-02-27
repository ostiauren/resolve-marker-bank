from terminal.connect import load_fusionscript

def getResolve() -> "PyRemoteResolve":
    print ("main.py getResolve()")
    load_fusionscript()
    import fusionscript as dvr_script
    return dvr_script.scriptapp("Resolve", "10.1.10.1")
    
resolveObject: "PyRemoteResolve" = getResolve()

