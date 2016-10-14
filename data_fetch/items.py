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
