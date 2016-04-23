# -*- coding: utf-8 -*-
# Autor: Daniel Garcia (danielgarciabsb@gmail.com)

import scrapy
import re
import MySQLdb

from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from unicodedata import normalize

class CursosSpider(scrapy.Spider):
    name = "cursos_sql"
    allowed_domains = ["matriculaweb.unb.br"]
    start_urls = ('https://matriculaweb.unb.br/matriculaweb/graduacao/curso_rel.aspx?cod=1',
                'https://matriculaweb.unb.br/matriculaweb/graduacao/curso_rel.aspx?cod=2',
                'https://matriculaweb.unb.br/matriculaweb/graduacao/curso_rel.aspx?cod=3',
                'https://matriculaweb.unb.br/matriculaweb/graduacao/curso_rel.aspx?cod=4',)

    def __init__(self):
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider, reason):
        if reason == 'finished':
            print 'Finalizado!'
            print self.cursos
            print 'Tamanho: ' + str(len(self.cursos))
            db = MySQLdb.connect(host="localhost", user="root", passwd="", db="DADOS_ALUNOS_LICMAT")
            cur = db.cursor()

            for curso in self.cursos:
                try:
                    print 'Inserindo curso: ' + curso[1]
                    cur.execute("INSERT INTO CURSO VALUES (%s,%s,%s)", (curso[0], curso[1], curso[2]))
                    db.commit()
                except IOError, e:
                    db.rollback()
                    print 'ERRO!'
                    print >> sys.stderr, e
                    sys.exit()

    def parse(self, response):
        try:
            self.cursos
        except:
            self.cursos = []

        for tablerow in response.xpath("//tr[@class='PadraoMenor']"):
            curso = [
                    int(tablerow.xpath('td[2]/text()').extract()[0]),
                    normalizarNome(tablerow.xpath('td/a/text()').extract()[0]),
                    ]
            if tablerow.xpath('td[4]/text()').extract()[0] == u'Noturno':
                curso.append('N')
            else:
                curso.append('D')
            self.cursos.append(curso)

def normalizarNome(source):
    source = source.rstrip()
    source = source.lstrip()
    source = source.replace('-','_')
    source = source.replace(',','_')
    source = source.replace(' ','_')
    source = source.replace('.','_')
    source = source.replace('___','_')
    source = source.replace('__','_')
    source = source.upper()
    return normalize('NFKD', source).encode('ASCII','ignore')
