# -*- coding: utf-8 -*-
# Autor: Daniel Garcia (danielgarciabsb@gmail.com)

import scrapy
import re
import MySQLdb

from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from unicodedata import normalize

def getHabs():
    cursos = [1228,1643,1627,1619,1635,1601,1104,1295,1694,1121,1287,1091,1244,1236,1252,1571,1279,1261,19,701,86,27,1422,728,680,1309,671,1023,191,1538,370,710,1333,94,736,507,809,35,213,906,205,1473,698,43,817,612,795,329,1589,442,1457,582,1341,1376,892,591,396,604,949,1562,353,876,1449,221,1503,124,744,1384,264,132,1511,1350,1431,230,1392,51,779,825,914,639,1414,345,1465,141,752,1686,159,884,1368,175,281,1406,451,647,60,787,523,183,167,761,1481,400,272,1490,1554,1520,1112,1546,1155,1082,1325,1163,1317,1147,1139,1180,299,1171]
    url = 'https://matriculaweb.unb.br/matriculaweb/graduacao/curso_dados.aspx?cod='
    tupla = ()
    for hab in cursos:
        tupla += (url + str(hab),)
    return tupla

class HabilitacoesSpider(scrapy.Spider):
    name = "habilitacoes_sql"
    allowed_domains = ["matriculaweb.unb.br"]
    start_urls = getHabs()

    def __init__(self):
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider, reason):
        if reason == 'finished':
            print 'Finalizado!'
            print self.habilitacoes
            print 'Tamanho: ' + str(len(self.habilitacoes))
            db = MySQLdb.connect(host="localhost", user="root", passwd="", db="DADOS_ALUNOS_LICMAT")
            cur = db.cursor()

            for habilitacao in self.habilitacoes:
                try:
                    print 'Inserindo habilitacao: ' + habilitacao[1]
                    print habilitacao
                    cur.execute("INSERT INTO HABILITACAO VALUES (%s,%s,%s)", (habilitacao[0], habilitacao[1], habilitacao[2]))
                    db.commit()
                except IOError, e:
                    db.rollback()
                    print 'ERRO!'
                    print >> sys.stderr, e
                    sys.exit()

    def parse(self, response):
        try:
            self.habilitacoes
        except:
            self.habilitacoes = []

        for tablerow in response.xpath("//tr[@class='PadraoBranco']/td/b"):
            codigo = int(re.findall('\d+',tablerow.xpath('text()').extract()[0])[0])
            nome = re.sub(r'^[0-9 ]+','',tablerow.xpath('text()').extract()[0])
            nome = normalizarNome(nome)
            curso = int(response.url[72:])

            self.habilitacoes.append([codigo,nome,curso])

def normalizarNome(source):
    source = source.rstrip()
    source = source.lstrip()
    source = source.replace('-','_')
    source = source.replace(',','_')
    source = source.replace(' ','_')
    source = source.replace('.','_')
    source = source.replace('___','_')
    source = source.replace('__','_')
    source = source.lstrip('_')
    source = source.upper()
    return normalize('NFKD', source).encode('ASCII','ignore')
