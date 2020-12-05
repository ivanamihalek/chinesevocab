#!/bin/bash

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


##########################
## translation spider test

# check we are in the test dir
echo "##############################"
if [[ `basename $PWD` != "tests"  ]]
then
  echo "please run from tests dir"
  echo
  exit
fi
echo "in test dir"

# do we have the settings file?
if [[ ! -f  ../settings.py ]]
then
  echo "oddly enough, ../settings.py not found"
fi
# copy settings to bkps
if [[ ! -d   ../bkps ]]  # make bkps dir if it does not exists
then
  mkdir ../bkps
fi
if [[ -f  ../bkps/settings.py ]]
then
  echo ../bkps/settings.py exists
else
  cp ../settings.py ../bkps/settings.py
  echo copied ../settings.py to ../bkps/settings.py
fi

##################################################
# hack the settings.py to the values that we need
sed 's/MONGODB_DB/#MONGODB_DB/' ../settings.py -i
echo 'MONGODB_DB  = "cvkb_mockup"' >> ../settings.py
sed 's/LOG_LEVEL/#LOG_LEVEL/' ../settings.py -i
echo 'LOG_LEVEL = "ERROR"' >> ../settings.py
# drop the mockup db if it exists
mongo --eval "db.dropDatabase()" cvkb_mockup   > /dev/null 2>&1

## contract test
echo; echo "##############################"
echo running contract test for translation
scrapy check translation

## test the translation stored
echo; echo "##############################"
echo checking the translation stored

# run the spider
scrapy crawl translation -a topic=genome > /dev/null 2>&1
# check the translation stored
translation_stored=`mongo --eval "db.translation.find({english: 'genome'}, {chinese: 1, _id:0})" cvkb_mockup | grep 基因组`
if [[ $translation_stored > 0 ]]
then
  tput setaf 4; echo "translation stored: $translation_stored (OK)";  tput sgr0
else
  tput setaf 1; echo "Warning: the expected translation for 'genome' (基因组) not found.";  tput sgr0
fi

## failure test
## if we cannot find the word we should raise an exception
echo; echo "##############################"
echo translation failure test
## the full error message will be something like "CloseSpider exception: Chinese translation for the topic 'web scraping' not found."
ret=`scrapy crawl translation -a topic="web_scraping" 2>&1 | grep "ERROR: CloseSpider exception: Chinese translation"`
if [[ $ret > 0 ]]
then
  tput setaf 4; echo "translation not found handled gracefully (OK)";  tput sgr0
else
  tput setaf 1; echo "Warning: unexpected behavior when translation not found.";  tput sgr0
fi


# cleanup after ourselves
echo; echo "##############################"
echo cleanup
mongo --eval "db.dropDatabase()" cvkb_mockup   > /dev/null 2>&1
cp ../bkps/settings.py ../settings.py
echo copied ../bkps/settings.py back to ../settings.py

echo