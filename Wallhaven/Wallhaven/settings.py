# -*- coding: utf-8 -*-

# Scrapy settings for Wallhaven project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'Wallhaven'

SPIDER_MODULES = ['Wallhaven.spiders']
NEWSPIDER_MODULE = 'Wallhaven.spiders'

ITEM_PIPELINES = {
    'Wallhaven.pipelines.WallhavenPipeline': 0,
}

FEED_FORMAT = 'json'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'Wallhaven (+http://www.yourdomain.com)'
