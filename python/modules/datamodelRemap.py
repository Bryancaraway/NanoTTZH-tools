from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object

class ObjectRemapped(Object):
    def __init__(self, event, prefix, index=None, replaceMap=None):
        Object.__init__(self, event, prefix, index)
        self.replaceMap = replaceMap

    def __getattr__(self, attr):
        if self.replaceMap and attr in self.replaceMap:
            return Object.__getattr__(self, self.replaceMap[attr])
        else:
            return Object.__getattr__(self, attr)


class CollectionRemapped(Collection):
    def __init__(self, event, prefix, lenVar=None, replaceMap=None):
        Collection.__init__(self, event, prefix, lenVar)
        self.replaceMap = replaceMap

    def __getitem__(self, index):
        if not self.replaceMap:
            return Collection.__getitem__(self, index)

        if type(index) == int and index in self._cache: return self._cache[index]
        if index >= self._len: raise IndexError, "Invalid index %r (len is %r) at %s" % (index,self._len,self._prefix)
        ret = ObjectRemapped(self._event,self._prefix,index=index,replaceMap=self.replaceMap)
        if type(index) == int: self._cache[index] = ret
        return ret

        
