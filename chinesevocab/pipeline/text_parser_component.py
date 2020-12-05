import re

#    Chinesevocab collects several hundred non-generic words related to a specified topic
#
#    Copyright (C) 2020 Ivana Mihalek
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#    Contact: ivana.mihalek@gmail.com


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
