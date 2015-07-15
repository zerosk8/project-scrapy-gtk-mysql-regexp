# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy import signals
from scrapy.contrib.exporter import JsonLinesItemExporter

class WallhavenPipeline(object):
    def __init__(self):
        self.file_name = './resources/query_results.json'
    
    @classmethod
    def from_crawler(cls, crawler):
         pipeline = cls()
         crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
         crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
         return pipeline
    
    def spider_opened(self, spider):
        self.file = open(self.file_name, 'w+b')
        self.exporter = JsonLinesItemExporter(self.file)
        self.exporter.start_exporting()
    
    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        self.file.close()
    
    def process_item(self, item, spider):
        self.exporter.export_item(item)
        
        return item
