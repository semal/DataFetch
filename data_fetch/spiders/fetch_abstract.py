# coding=utf-8
# 抓取给定 pmid 的文献摘要

import scrapy
from scrapy.loader import ItemLoader
from data_fetch.items import PaperItem, OMIMTable

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/45.0.2454.85 Safari/537.36'
}


class FetchPubMedAbstract(scrapy.Spider):
    name = 'fetch_pubmed_abstract'
    domain = 'https://www.ncbi.nlm.nih.gov/pubmed'

    def __init__(self, pmids):
        self.pmid_list = pmids.split(',')
        self.count = 0
        self.current_pmid = None

    def start_requests(self):
        for pmid in self.pmid_list:
            self.current_pmid = pmid
            yield scrapy.Request('%s/%s' % (self.domain, pmid), self.parse)

    def parse(self, response):
        self.count += 1
        loader = ItemLoader(item=PaperItem(), response=response)
        # pmid = response.xpath('//dl[@class="rprtid"]/dd/a/text()').extract_first()
        loader.add_xpath('title', '//div[@class="rprt abstract"]/h1/text()')
        loader.add_xpath('abstract', '//abstracttext/text()')
        loader.add_xpath('pmid', '//dl[@class="rprtid"]/dd/text()')
        loader.add_value('id', '%d' % self.count)
        yield loader.load_item()


class FetchOMIMTable(scrapy.Spider):
    name = 'fetch_omim_table'
    domain = 'https://omim.org/search/?index=geneMap&search='
    cookies = {
        'donation-popup': 'true',
    }

    def __init__(self, gene_list):
        self.gene_list = gene_list.split(',')

    def start_requests(self):
        for gene in self.gene_list:
            request = scrapy.Request(
                '%s%s' % (self.domain, gene), callback=self.parse,
                headers=headers, cookies=self.cookies,
            )
            yield request

    def parse(self, response):
        print response
        loader = ItemLoader(item=OMIMTable(), response=response)
        print response.xpath(
            '//div[@id="content"]'
            '/div/div[@id="results"]'
            '/table[@class="wrapper-table"]'
            '/tr/td/table[@class="wrapper-table"]'
        ).extract()[0]
        loader.add_xpath(
            'table',
            '//div[@id="content"]'
            '/div/div[@id="results"]'
            '/table[@class="wrapper-table"]'
            # '/tbody'
            '/tr/td'
            '/table[@class="wrapper-table"]/tbody'
        )
        # print response.xpath('//td[@class="value text-font lookup"]/text()').extract()
        # loader.add_xpath(
        #     'table',
        #     '//td[contains(@class, "value text-font")]'
        # )
        yield loader.load_item()
