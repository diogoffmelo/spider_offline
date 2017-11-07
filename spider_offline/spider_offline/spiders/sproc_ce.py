# -*- coding: utf-8 -*-
import scrapy


URL = ('http://www4.tjce.jus.br/sproc2/paginas/resconprocpartenova.asp?'
       'optNomeParte=2&TXT_NOMEPARTE={}&TXT_NOMEUNIDES=&TXT_CODUNIDES'
       '=&TXT_NOMEORI=&TXT_CODORI=&chk_Arquivados=1&CMB_NUMMOV=99').format

XPATH_LINKS = './table/tr[@class="l1" or @class="l0"]/td[1]/a/@href'


BASE_LINK = 'http://www4.tjce.jus.br/sproc2/paginas/'


XPATH_LINK_PROCESSO = ('.//tr[@class="linha-superior alinhamento-esquerdo"]'
                       '/td[1]/a/@href')

class SprocCeSpider(scrapy.Spider):
    name = 'sproc_ce'
    allowed_domains = ['http://www4.tjce.jus.br']


    def __init__(self, nome='', *args, **kwargs):
        if not nome:
            raise Exception('Argumento invalido')

        super(SprocCeSpider, self).__init__(*args, **kwargs)
        self.start_urls = [URL(nome.strip().replace(' ', '+'))]


    def parse(self, response):
        pagina_off_line = {
            'tipo': 'pesquisa_inicial',
            'links_gerados': [],
            'link_originario': response.url,
            'argumentos': '',
            'conteudo': response.xpath('./body').extract_first(),
            'metodo': 'GET',
        }

        base = response.xpath('./body/center')[0]
        for link in base.xpath(XPATH_LINKS).extract():
            url = BASE_LINK + link
            pagina_off_line['links_gerados'].append(url)
            yield scrapy.Request(
                    url=url,
                    dont_filter=True,
                    callback=self.parse_nomes)

        yield pagina_off_line


    def parse_nomes(self, response):
        pagina_off_line = {
            'tipo': 'paginacao_nome',
            'links_gerados': [],
            'link_originario': response.url,
            'argumentos': '',
            'metodo': 'GET',
            'conteudo': response.xpath('./body').extract_first(),
        }

        links = response.xpath(XPATH_LINK_PROCESSO).extract()

        if links:
            for link in links:
                url = BASE_LINK + link
                pagina_off_line['links_gerados'].append(url)
                yield scrapy.Request(
                        url=url,
                        dont_filter=True,
                        callback=self.parse_processo)
            
            yield pagina_off_line
        
        else:
            for r in self.parse_processo(response):
                yield r

    def parse_processo(self, response):
        pagina_off_line = {
            'tipo': 'pagina_processo',
            'links_gerados': [],
            'link_originario': response.url,
            'argumentos': '',
            'metodo': 'GET',
            'conteudo': response.xpath('./body').extract_first(),
        }

        yield pagina_off_line
