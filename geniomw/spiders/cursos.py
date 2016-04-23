# -*- coding: utf-8 -*-
# Autor: Daniel Garcia (danielgarciabsb@gmail.com)

import scrapy
import re

from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals

from normalizarTexto import normalizarNome
from salvarArquivo import salvarArquivo

class CursosSpider(scrapy.Spider):
    name = "cursos"
    allowed_domains = ["matriculaweb.unb.br"]
    start_urls = ('https://matriculaweb.unb.br/matriculaweb/graduacao/curso_rel.aspx?cod=1',
                'https://matriculaweb.unb.br/matriculaweb/graduacao/curso_rel.aspx?cod=2',
                'https://matriculaweb.unb.br/matriculaweb/graduacao/curso_rel.aspx?cod=3',
                'https://matriculaweb.unb.br/matriculaweb/graduacao/curso_rel.aspx?cod=4',)

    def __init__(self):
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider, reason):
        if reason == 'finished':
            salvarArquivo(self.cursos, 'cursos.json')
            salvarArquivo(self.fluxos, 'fluxos.json')
            salvarArquivo(self.habilitacoes, 'habilitacoes.json')

    def parse(self, response):
        try:
            self.cursos
        except:
            self.cursos = []

        for tablerow in response.xpath("//tr[@class='PadraoMenor']"):
            curso = {
                'codigo' : int(tablerow.xpath('td[2]/text()').extract()[0]),
                'nome'   : normalizarNome(tablerow.xpath('td/a/text()').extract()[0]),
                'turno'  : tablerow.xpath('td[4]/text()').extract()[0],
                }
            self.cursos.append(curso)
        
        for curso in self.cursos:
            request = scrapy.Request('https://matriculaweb.unb.br/matriculaweb/graduacao/curso_dados.aspx?cod='+str(curso.get('codigo')),
                callback=self.parseHabilitacoes)
            request.meta['codigo'] = curso.get('codigo')
            yield request

    def parseHabilitacoes(self, response):
        try:
            self.habilitacoes
        except:
            self.habilitacoes = []

        habilitacoes = []

        for tablerow in response.xpath("//tr[@class='PadraoBranco']/td/b"):
            codigo = int(re.findall('\d+',tablerow.xpath('text()').extract()[0])[0])
            habilitacoes.append(codigo)
            self.habilitacoes.append({
                    'codigo' : codigo,
                    'nome'   : re.sub(r'^[0-9 ]+','',normalizarNome(tablerow.xpath('text()').extract()[0])),
                    })

        for i in range(len(self.cursos)):
            if self.cursos[i].get('codigo') == response.meta['codigo']:
                self.cursos[i].update({'habilitacoes':habilitacoes})
                break

        for habilitacao in habilitacoes:
            request = scrapy.Request('https://matriculaweb.unb.br/matriculaweb/graduacao/fluxo.aspx?cod='+str(habilitacao),
                callback=self.parseFluxo)
            request.meta['habilitacao'] = habilitacao
            yield request

    def parseFluxo(self, response):
        fluxo = []

        for tabela in response.xpath("//table[@class='FrameCinza' and @cellpadding='5']"):
            periodo = []

            for tablerow in tabela.xpath("tr[@class='padraomenor']"):
                periodo.append(int(tablerow.xpath('td[3]/a/text()').extract()[0]))
            fluxo.append(periodo)

        try:
            self.fluxos
        except:
            self.fluxos = []

        self.fluxos.append({'habilitacao':response.meta['habilitacao'],'fluxo':fluxo})