from lxml import etree #AH
from lxml import objectify #AH
import json
import uuid
import codecs
# import lxml #GVM

from pymei.Components import MeiAttribute, MeiElement, MeiDocument
from pymei.Components import Modules as mod

import types
import logging

lg = logging.getLogger('pymei')

def jsontomei(meifile):
    """ Takes an incoming JSON stream and returns a MeiDocument object.
        
        Requires that you pass it a name.
    """
    f = codecs.open(meifile, 'r', encoding='utf-8')
    js = f.read()
    f.close()
    jsn = json.loads(js) # convert the JSON to python dicts/arrays.
    doc = MeiDocument.MeiDocument('jsonstream')
    j = _json_to_mei(jsn)
    doc.root = j
    return doc

def jsonstringtomei(string):
    jsn = json.loads(string)
    doc = MeiDocument.MeiDocument('jsonstream')
    j = _json_to_mei(jsn)
    doc.root = j
    return doc

def _json_to_mei(el):
    """ Takes a JSON-structured MEI file and converts it to a set of nested Python
        MEI objects.
        
        See test/meijson.py for an example of how JSON-structured MEI looks.
    """
    # Strings are interpreted as values.
    if isinstance(el, types.StringType) or isinstance(el, types.UnicodeType):
        return el
    
    # attributes have a special attribute dictionary key.
    if isinstance(el, types.DictType) and "@a" in el.keys():
        return el
    
    if isinstance(el, types.DictType) and "@t" in el.keys():
        return el
    
    if isinstance(el, types.DictType) and "@v" in el.keys():
        return el
        
    # don't pop from an empty dict!
    if len(el.keys()) < 1:
        return
    
    # convert the dict key name to an MEI object name.
    tagname = el.keys().pop()
    objname = "{0}_".format(tagname)
    obj = getattr(mod, objname)()
    
    # map this on to the object
    if isinstance(el[tagname], types.ListType):
        
        # loopdy-loopdy!
        m = map(_json_to_mei, el[tagname])
        # our map operation will return a number of things. Depending on what 
        # is in our map result, we put that it the MeiElement object accordingly.
        for d in m:                
            if isinstance(d, types.DictType) and "@a" in d.keys():
                if u"xml:id" not in d['@a'].keys():
                    d['@a'][u'xml:id'] = generate_mei_id()
                obj.attributes = d['@a']
            
            elif isinstance(d, types.DictType) and "@t" in d.keys():
                obj.tail = d['@t']
            
            elif isinstance(d, types.DictType) and "@v" in d.keys():
                obj.value = d['@v']
                
            else:
                obj.add_child(d)
    return obj