from terminal.getResolve import resolveObject

class Resolve(object):
    def __init__(self): #, headless: Optional[bool] = None, path: Optional[str] = None):
        #self._obj: PyRemoteProjectManager = resolveObject.GetProjectManager()
        self.project_manager = resolveObject.GetProjectManager()
#        return resolveObject

    def projectManager(self):
#        print ("self.Resolve", resolveObject.GetProjectManager())
        #pm = self.Resolve.GetProjectManager()
        #return resolveObject.GetProjectManager()
        return self.projectManager

    def resolve(self):
        return resolveObject
