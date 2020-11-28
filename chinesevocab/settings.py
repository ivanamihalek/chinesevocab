# Scrapy settings for chinesevocab project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from chinesevocab.pipeline.mongo_words_component import MongoWordsComponent

BOT_NAME = 'chinesevocab'

SPIDER_MODULES = ['chinesevocab.spiders']
NEWSPIDER_MODULE = 'chinesevocab.spiders'

LOG_ENABLED = True
LOG_LEVEL = "ERROR"  # too much noise otherwise

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'chinesevocab (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'chinesevocab.middlewares.ChinesevocabSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'chinesevocab.middlewares.ChinesevocabDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# The integer values you assign to classes in this setting determine the order
# in which they run: items go through from lower valued to higher valued classes.
# It’s customary to define these numbers in the 0-1000 range.
ITEM_PIPELINES = {
   # 'chinesevocab.pipeline.mongo_text_component.MongoTextComponent': 100,
   # 'chinesevocab.pipeline.text_parser_component.TextParserComponent': 200,
   # 'chinesevocab.pipeline.mongo_words_component.MongoWordsComponent': 300,
}
MONGODB_URI = "mongodb://localhost:27017"
# MONGODB_PORT = 27017  # default port for mongoDB;
# http interface accessible at  http://localhost:28017
# http interface  not working some hacking apparently needed in /etc/mongod.conf
# I'm not a fan of these anyway, so move on
MONGODB_DB  = "chinesevocab"
MONGODB_WORDS_COLLECTION = "words"
MONGODB_TEXT_COLLECTION = "text_chunks"

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'