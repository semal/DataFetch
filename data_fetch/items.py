# coding=utf-8
# DataFetch items definition file
import scrapy
from scrapy.loader.processors import Join, MapCompose, TakeFirst
from w3lib.html import remove_tags


class PaperItem(scrapy.Item):
    id = scrapy.Field(output_processor=TakeFirst())
    pmid = scrapy.Field(output_processor=TakeFirst())
    title = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=Join(),
    )
    abstract = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=Join(),
    )


def strip(string):
    return string.strip()


class OMIMTable(scrapy.Item):
    table = scrapy.Field(output_processor=Join())


def clean_novel_content(content):
    content = content.replace('<dd id="contents">', '').replace('</dd>', '')
    paragraphs = [e.replace(u'顶点小说 ２３ＵＳ．ＣＯＭ更新最快', '') for e in content.split('<br><br>')]
    return paragraphs


class TakeFirstAndClen(object):
    def __call__(self, values):
        for value in values:
            if value is not None and value != '':
                return clean_novel_content(value)


class ChapterItem(scrapy.Item):
    book_title = scrapy.Field(output_processor=TakeFirst())
    chapter_name = scrapy.Field(output_processor=TakeFirst())
    chapter_order = scrapy.Field(output_processor=TakeFirst())
    chapter_content = scrapy.Field(output_processor=TakeFirstAndClen())
    source = scrapy.Field(output_processor=TakeFirst())
