# -*- coding: utf-8 -*-

from unicodedata import normalize

# Dado um objeto de uma lista em Unicode
# retorna a forma normalizada
def normalizarNome(source):
	source = source.rstrip()
	source = source.replace('-','')
	source = source.replace(',','')
	source = source.lstrip()
	source = source.upper()
	#print '[' + source + ']'
	return normalize('NFKD', source).encode('ASCII','ignore')