# -*- coding: latin-1 -*-

from wrap import *
import math

_metafor = None 
def getMetafor(_parameters={}):
	global _metafor
	if _metafor == None :
		from sphere import getMetafor
		parameters = {'R1':50}
		_metafor = getMetafor(parameters)
	return _metafor