"""Utilities for working with JSON and json-like structures - deeply nested Python dicts and lists

This lets us iterate over child nodes and access elements with a dot-notation.
"""
import sys
isPy3 = sys.version_info[0]==3
if isPy3:
    def __alt_str__(v,enc='utf8'):
        return v if isinstance(v,bytes) else v.encode(enc)
    __strTypes__ = (str,bytes)
else:
    __alt_str__ = unicode
    __strTypes__ = (str,unicode)

class MyLocals(object):
    pass
mylocals = MyLocals()

def setErrorCollect(collect):
    mylocals.error_collect = collect

setErrorCollect(False)

def errorValue(x):
    if isinstance(x,__strTypes__):
         return repr(x) if ' ' in x else x
    return 'None' if x is None else str(x)
def condJSON(v,__name__=''):
    return JSONDict(v,__name__=__name__) if isinstance(v,dict) else JSONList(v,__name__=__name__) if isinstance(v,list) else v

def condJSONSafe(v,__name__=''):
    return JSONDictSafe(v,__name__=__name__) if isinstance(v,dict) else JSONListSafe(v,__name__=__name__) if isinstance(v,list) else v

class JSONListIter(object):
    def __init__(self, lst, conv):
        self.lst = lst
        self.i = -1
        self.conv = conv

    def __iter__(self):
        return self

    def next(self):
        if self.i<len(self.lst)-1:
            self.i += 1         
            return self.conv(self.lst[self.i])
        else:
            raise StopIteration

    if isPy3:
        __next__ = next
        del next

class JSONList(list):
    def __init__(self,v,__name__=''):
        list.__init__(self,v)
        self.__name__ = __name__
    def __getitem__(self,x):
        return condJSON(list.__getitem__(self,x),__name__='%s\t%s'%(self.__name__,errorValue(x)))
    def __iter__(self):
        return JSONListIter(self,condJSON)

class JSONListSafe(JSONList):
    def __getitem__(self,x):
        __name__='%s\t%s'%(self.__name__,errorValue(x))
        try:
            return condJSONSafe(list.__getitem__(self,x),__name__=__name__)
        except:
            if mylocals.error_collect:
                mylocals.error_collect(__name__)
            return JSONStrSafe('')
    def __iter__(self):
        return JSONListIter(self,condJSONSafe)

class JSONStrSafe(str):
    def __getattr__(self, attr):
        return self
    __getitem__ = __getattr__


class JSONDict(dict):
    "Allows dotted access"
    def __new__(cls,*args,**kwds):
        __name__ = kwds.pop('__name__')
        self = dict.__new__(cls,*args,**kwds)
        self.__name__ = __name__
        return self

    def __init__(self,*args,**kwds):
        kwds.pop('__name__','')
        dict.__init__(self,*args,**kwds)

    def __getattr__(self, attr, default=None):
        if attr in self:
            return condJSON(self[attr],__name__='%s\t%s'%(self.__name__,errorValue(attr)))
        elif __alt_str__(attr) in self:
            return condJSON(self[__alt_str__(attr)],__name__='%s\t%s'%(self.__name__,errorValue(attr)))
        elif attr=='__safe__':
            return JSONDictSafe(self,__name__=self.__name__)
        else:
            raise AttributeError("No attribute or key named '%s'" % attr)

    def sorted_items(self,accept=None, reject=lambda i: i[0]=='__name__'):
        if accept or reject:
            if not accept:
                f = lambda i: not reject(i)
            elif not reject:
                f = accept
            else: #both
                f = lambda i: accept(i) and not reject(i)
            return sorted(((k,condJSON(v,__name__==k)) for k,v in self.iteritems() if f((k,v))))
        else:
            return sorted(((k,condJSON(v,__name__==k)) for k,v in self.iteritems()))

    def sorted_keys(self):
        return sorted(self.keys())

class JSONDictSafe(JSONDict):
    "Allows dotted access"
    def __getattr__(self, attr, default=None):
        if attr in self:
            return condJSONSafe(self[attr],__name__='%s\t%s'%(self.__name__,errorValue(attr)))
        elif __alt_str__(attr) in self:
            return condJSONSafe(self[__alt_str__(attr)],__name__='%s\t%s'%(self.__name__,errorValue(attr)))
        elif attr=='__safe__':
            return self
        else:
            return JSONStrSafe('')

    def __getitem__(self,x):
        __name__='%s\t%s'%(self.__name__,errorValue(x))
        try:
            return condJSONSafe(dict.__getitem__(self,x),__name__=__name__)
        except KeyError:
            if mylocals.error_collect:
                mylocals.error_collect(__name__)
            return JSONStrSafe('')

    def sorted_items(self,accept=None, reject=lambda i: i[0]=='__name__'):
        if accept or reject:
            if not accept:
                f = lambda i: not reject(i)
            elif not reject:
                f = accept
            else: #both
                f = lambda i: accept(i) and not reject(i)
            return sorted(((k,condJSONSafe(v,__name__==k)) for k,v in self.iteritems() if f((k,v))))
        else:
            return sorted(((k,condJSONSafe(v,__name__==k)) for k,v in self.iteritems()))
