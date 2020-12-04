#!/bin/bash
##########################
## extended vocab spider test

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
echo running contract test for extended
scrapy check extended

## failure test
echo; echo "##############################"
echo failure test for extended spider
# what happens if we don't have the translation
sed 's/MONGODB_DB/#MONGODB_DB/' ../settings.py -i
echo 'MONGODB_DB  = "cvkb_mockup"' >> ../settings.py
## drop the mockup db - make sure we don't have the translation
mongo --eval "db.dropDatabase()" cvkb_mockup   > /dev/null 2>&1

echo "testing the case of no translation found"
ret=`scrapy crawl extended -a topic="web_crawling" | tail -n1 | grep -i "No extended translation"`
echo $ret
if [[ $ret > 0 ]]
then
  tput setaf 4; echo "translation not found, closed gracefully (OK)"; tput sgr0
else
  tput setaf 1; echo "Warning: unexpected behavior on translation  not found."; tput sgr0
fi

# any other failure cases I could think of?

# cleanup after ourselves
echo; echo "##############################"
echo cleanup
mongo --eval "db.dropDatabase()" cvkb_mockup   > /dev/null 2>&1
cp ../bkps/settings.py ../settings.py
echo copied ../bkps/settings.py back to ../settings.py

echo