import scrapy
from scrapy.loader import ItemLoader
from scrapy.http import HtmlResponse
from scrapy.selector import Selector
from data_fetch.items import ChapterItem
from urllib2 import urlopen


class FetchNovel(scrapy.Spider):
    name = 'fetch_novel'
    domain = 'http://www.23us.com'

    def __init__(self, c1, c2):
        self.c1 = c1
        self.c2 = c2
        self.book_name = ''
        self.chapter_list = []

    def start_requests(self):
        book_entrance = '%s/html/%s/%s' % (self.domain, self.c1, self.c2)
        response = urlopen(book_entrance)
        self.parse_chapters(HtmlResponse(book_entrance, body=response.read()))
        for i, chapter in enumerate(self.chapter_list):
            url = '%s/%s' % (book_entrance, chapter)
            print url
            yield scrapy.Request(url, self.parse, dont_filter=True, meta=[('index', i + 1)])

    def parse_chapters(self, response):
        sel = Selector(response)
        items = sel.xpath('//td[@class="L"]/a/@href').extract()
        self.book_name = ' '.join(sel.xpath('//dd/h1/text()').extract()[0].split()[:-1])
        return self.chapter_list.extend(items)

    def parse(self, response):
        loader = ItemLoader(item=ChapterItem(), response=response)
        loader.add_value('book_title', self.book_name)
        loader.add_xpath('chapter_name', '//dd/h1/text()')
        loader.add_value('chapter_order', str(response.meta['index']))
        loader.add_xpath('chapter_content', '//dd[@id="contents"]')
        loader.add_value('source', response.url)
        item = loader.load_item()
        yield item
