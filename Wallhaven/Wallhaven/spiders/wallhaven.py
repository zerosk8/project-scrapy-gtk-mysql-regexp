# -*- coding: utf-8 -*-
import scrapy
import re
from Wallhaven.items import WallhavenItem


class WallhavenSpider(scrapy.Spider):
    name = 'wallhaven'
    allowed_domains = ["alpha.wallhaven.cc"]
    
    base_url = 'http://alpha.wallhaven.cc/search?q='
    start_urls = []
    
    def __init__(self, query):
        self.start_urls.append(self.base_url + query)
        self.query = query
    
    def parse(self, response):
        for url in response.xpath('//a[@class="preview"]/@href').extract():
            yield scrapy.Request(url, callback = self.parse_item)
    
    def parse_item(self, response):
        item = WallhavenItem()
        
        url = response.xpath('//img[@id="wallpaper"]/@src').extract().pop(0)
        file_name = url.split('/')[-1]
        
        item['url'] = 'http://' + re.sub('^\W+', '', url)
        item['name'] = file_name.split('.')[0]
        item['format'] = file_name.split('.')[1]
        item['width'] = response.xpath('//img[@id="wallpaper"]/@data-wallpaper-width').extract().pop(0)
        item['height'] = response.xpath('//img[@id="wallpaper"]/@data-wallpaper-height').extract().pop(0)
        item['query'] = self.query
        
        return item
