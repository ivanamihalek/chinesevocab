import re
import jieba
from chinesevocab.items import TokenSetItem


class TextParserComponent:

    def __init__(self):
        pass

    def _tokenize(self, item):
        # get rid of non-chinese characters
        matches = re.findall(r"[\u4e00-\u9FFF]", item['text'])
        chstr = "".join(matches)
        # cut_all=False does not further divide chunks it recognizes as words
        return jieba.cut(chstr, cut_all=False)

    def process_item(self, item, spider):
        print("In process_item in TextParserComponent.")
        processedItem = TokenSetItem()
        processedItem['tokens'] = self._tokenize(item)
        processedItem['collection'] = item['collection']
        return processedItem
