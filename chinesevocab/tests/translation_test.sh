#!/bin/bash
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

## contract test
echo; echo "##############################"
echo running contract test for translation
scrapy check translation

## test the translation stored
echo; echo "##############################"
echo checking the translation stored
sed 's/MONGODB_DB/#MONGODB_DB/' ../settings.py -i
echo 'MONGODB_DB  = "cvkb_mockup"' >> ../settings.py
# drop the mockup db
mongo --eval "db.dropDatabase()" cvkb_mockup   > /dev/null 2>&1
# run the spider
scrapy crawl translation -a topic=genome > /dev/null 2>&1
# check the translation stored
translation_stored=`mongo --eval "db.translation.find({english: 'genome'}, {chinese: 1, _id:0})" cvkb_mockup | grep 基因组`
if [[ $translation_stored > 0 ]]
then
  echo "translation stored: $translation_stored (OK)"
else
  echo "Warning: the expected translation for 'genome' (基因组) not found."
fi

## failure test
## if we cannot find the word we should raise an exception
echo; echo "##############################"
echo translation failure test
errmsg="Chinese translation for the topic 'web scraping' not found."
ret=`scrapy crawl translation -a topic="web_scraping" | tail -n1`
if [[ $errmsg == $ret ]]
then
  echo "translation not found handled gracefully (OK)"
else
  echo "Warning: unexpected behavior on translation  not found."
fi


# cleanup after ourselves
echo; echo "##############################"
echo cleanup
mongo --eval "db.dropDatabase()" cvkb_mockup   > /dev/null 2>&1
cp ../bkps/settings.py ../settings.py
echo copied ../bkps/settings.py back to ../settings.py

echo