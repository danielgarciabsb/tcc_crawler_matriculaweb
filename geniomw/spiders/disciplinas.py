# -*- coding: utf-8 -*-
# Autor: Daniel Garcia (danielgarciabsb@gmail.com)

import scrapy
import re

from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals

from normalizarTexto import normalizarNome
from salvarArquivo import salvarArquivo

class DisciplinasSpider(scrapy.Spider):
    name = "disciplinas"
    allowed_domains = ["matriculaweb.unb.br"]
    start_urls = ('https://matriculaweb.unb.br/matriculaweb/graduacao/oferta_dep.aspx?cod=1',
                'https://matriculaweb.unb.br/matriculaweb/graduacao/oferta_dep.aspx?cod=2',
                'https://matriculaweb.unb.br/matriculaweb/graduacao/oferta_dep.aspx?cod=3',
                'https://matriculaweb.unb.br/matriculaweb/graduacao/oferta_dep.aspx?cod=4')

    def __init__(self):
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider, reason):
        if reason == 'finished':
            salvarArquivo(self.departamentos, 'disciplinas.json')

    def parse(self, response):
    	try:
            self.departamentos
        except:
            self.departamentos = []

        for tablerow in response.xpath("//tr[@class='PadraoMenor']"):
            departamento = {
                'codigoDep'  : int(tablerow.xpath('td[1]/text()').extract()[0]),
                'siglaDep'   : tablerow.xpath('td[2]/text()').extract()[0],
                'departamento'    : normalizarNome(tablerow.xpath('td/a/text()').extract()[0]),
                }
            self.departamentos.append(departamento)

        for departamento in self.departamentos:
            request = scrapy.Request('https://matriculaweb.unb.br/matriculaweb/graduacao/oferta_dis.aspx?cod='+str(departamento.get('codigoDep')), callback=self.parseDisciplinas)
            request.meta['codigo'] = int(departamento.get('codigoDep'))
            print "DEPARTAMENTO: " + str(departamento.get('codigoDep'))
            yield request

    def parseDisciplinas(self, response):
        disciplinas = []

        for tablerow in response.xpath("//tr[@class='PadraoMenor']"):
                disciplina = {
                    'codigo' : int(tablerow.xpath('td/b/text()').extract()[0]),
                    'nome'   : normalizarNome(tablerow.xpath('td/a/text()').extract()[0]),
                    }
                disciplinas.append(disciplina)

        for i in range(len(self.departamentos)):
            if self.departamentos[i].get('codigoDep') == response.meta['codigo']:
                self.departamentos[i].update({'disciplinas':disciplinas})
                break
