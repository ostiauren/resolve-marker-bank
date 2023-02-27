from terminal.getResolve import resolveObject

class Resolve(object):
    def __init__(self): #, headless: Optional[bool] = None, path: Optional[str] = None):
        #self._obj: PyRemoteProjectManager = resolveObject.GetProjectManager()
        print ("class Resolve(object): before")
        self.project_manager = resolveObject.GetProjectManager()
        print ("class Resolve(object): after")
#        return resolveObject

    def projectManager(self):
#        print ("self.Resolve", resolveObject.GetProjectManager())
        #pm = self.Resolve.GetProjectManager()
        #return resolveObject.GetProjectManager()
        return self.projectManager

    def resolve(self):
        print ("def resolve(self)")
        return resolveObject
