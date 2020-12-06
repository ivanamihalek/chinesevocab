# ChineseVocab - a Scrapy exercise

Chinesevocab collects (Mandarin) Chinese words related to a specified topic.

## Dependencies
[Scrapy](https://scrapy.org/), an open source framework for extracting the website data.

[Jieba](https://pypi.org/project/jieba/), a Chinese text segmentation tool.

[PyMongo](https://pymongo.readthedocs.io/en/stable/), tools for working with MongoDB
*  for MongoDB docs see https://docs.mongodb.com/manual/installation/
*  make sure mongo is running: `sudo systemctl start mongod`
*  check running: `sudo systemctl status mongod`

## Running
Run with

   ```./run.py <topic>```

The topic can be something like "genome" or "fashion." If the topic consistsq of two or three words 
you can link them with underscore,
for example "The_Internet", or "elementary_particle," but keep in mind that this
compound term should be discoverable in a dictionary for the pipeline to run as planned.
   
The project consist of four spiders, and ./run.py runs all of them in the order in
 which they are supposed to be run:
 1. [generic_vocab_spider.py](./chinesevocab/spiders/generic_vocab_spider.py) 
    fills the database collection of generic words (to be able to eliminate them later)
    This will be run only once - if the collection exists, the step is skipped.
 2. [translation_spider.py](./chinesevocab/spiders/translation_spider.py) 
    translates the topic from English to Chinese - if the translation already
    exists in the translation collection, the step is skipped.
 3. [topic_vocab_spider.py](./chinesevocab/spiders/topic_vocab_spider.py) 
    starts the collection of the words on the specified topic by scraping
    the Chinese Wikipedia page.
 4. [extended_topic_vocab_spider.py](./chinesevocab/spiders/extended_topic_vocab_spider.py ) 
    looks for some more words and the word usage frequency by following the first
    couple of tens of links from a search engine.

Each spider can be run by itself:
```
scrapy crawl generic
scrapy crawl translation -a topic=genome
scrapy crawl topic -a topic=genome
scrapy crawl extended -a topic=genome
```
The word genome here is used as an example - put your topic of interest in its place.

## Output
The output is the list of words (currently output to a file called `topic`.tsv) that appear more than 20 times in the search. 
The cutoff of 20 is arbitrary. You can change it in the run.py script.

To be self contained, the pipeline does not check how meaningful the list of words is.
If you would like to branch in that direction, the suggestion is to install and use
[cedict](https://www.mdbg.net/chinese/dictionary?page=cedict) (in that case
you may also wish to use the [cedict parser](https://www.mdbg.net/chinese/dictionary?page=cedict)).

Alternatively, 
[Google Sheets](https://www.mamababymandarin.com/automatically-translate-english-to-chinese-with-google-sheets/)
provides a cute trick to translate a shortish list like the oneproduced here.

## Testing
Use `./run_tests.sh` from the top directory to run all tests at once. Alternatively cd to chinesevocab/tests
and run tests for each spider one by one.
