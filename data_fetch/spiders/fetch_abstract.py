# coding=utf-8
# 抓取给定 pmid 的文献摘要

import scrapy
from scrapy.loader import ItemLoader
from utils import search_pubmed
from data_fetch.items import PaperItem


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
