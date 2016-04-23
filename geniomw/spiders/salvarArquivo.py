import json

def salvarArquivo(source, arquivo):
	f = open(arquivo, 'w')
	json.dump(source, f)
	f.close()