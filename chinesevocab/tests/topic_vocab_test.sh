#!/bin/bash
##########################
## topic vocab spider test

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

## contract test
echo; echo "##############################"
echo running contract test for topic
scrapy check topic

## failure test
echo; echo "##############################"
echo failure test for topic spider
# what happens if we don't have the translation
sed 's/MONGODB_DB/#MONGODB_DB/' ../settings.py -i
echo 'MONGODB_DB  = "cvkb_mockup"' >> ../settings.py
## drop the mockup db - make sure we don't have the translation
mongo --eval "db.dropDatabase()" cvkb_mockup   > /dev/null 2>&1

echo "1) testing the case of no translation found"
ret=`scrapy crawl topic -a topic="web_crawling" | tail -n1 | grep -i "No topic translation"`
echo $ret
if [[ $ret > 0 ]]
then
  tput setaf 4; echo "translation not found, closed gracefully (OK)"; tput sgr0
else
  tput setaf 1; echo "Warning: unexpected behavior on translation  not found."; tput sgr0
fi

echo "2) testing the case of no wiki page found"
# first we need to make sure that we have the translation
# for the topic for which there is no wikipedia page
# insert our test word
mongo --eval "db.translation.insertOne({'chinese' : '网络搜寻', 'english' : 'web crawling'})" cvkb_mockup   > /dev/null 2>&1
## run the spider
## if we cannot find the topic on the wikipedia we should raise an exception
## (the Crawler runner will ignore it by desing - it is not essential)
## the full error message will be something like "Chinese translation for the topic 'web crawling' not found."
ret=`scrapy crawl topic -a topic="web_crawling" | tail -n1 | grep -i "CloseSpider exception: Wiki page for the topic"`
echo $ret
if [[  $ret > 0  ]]
then
  tput setaf 4; echo "wiki page not found handled gracefully (OK)"; tput sgr0
else
  tput setaf 1; echo "Warning: unexpected behavior on wiki page  not found."; tput sgr0
fi

# cleanup after ourselves
echo; echo "##############################"
echo cleanup
mongo --eval "db.dropDatabase()" cvkb_mockup   > /dev/null 2>&1
cp ../bkps/settings.py ../settings.py
echo copied ../bkps/settings.py back to ../settings.py

echo