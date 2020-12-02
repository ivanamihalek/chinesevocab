#!/bin/bash
##########################
## generic vocab spider test

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
echo running contract test for generic
scrapy check generic

## test the collection produced
echo; echo "##############################"
echo checking the size of the produced collection of generic words
sed 's/MONGODB_DB/#MONGODB_DB/' ../settings.py -i
echo 'MONGODB_DB  = "cvkb_mockup"' >> ../settings.py
# drop the mockup db
mongo --eval "db.dropDatabase()" cvkb_mockup   > /dev/null 2>&1
# run the spider
scrapy crawl generic > /dev/null 2>&1
# count words stored
words_stored=`mongo --eval "db.words_generic.count()" cvkb_mockup | tail -n1`
echo "words stored: $words_stored"
if [[ $words_stored -gt 1000 ]]  # -gt compares integers, > compares strings (duh)
then
  echo OK
else
  echo "Warning: the number of stored generic words smaller than expected."
fi

# cleanup after ourselves
echo; echo "##############################"
echo cleanup
mongo --eval "db.dropDatabase()" cvkb_mockup   > /dev/null 2>&1
cp ../bkps/settings.py ../settings.py
echo copied ../bkps/settings.py back to ../settings.py

echo