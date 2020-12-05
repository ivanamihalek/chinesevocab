#!/bin/bash
##########################
## run all tests that we have so far
cd chinesevocab/tests
echo moved to `pwd`

tput setaf 4  # font color blue
echo
echo "################################"
echo "testing generic vocab collection"
tput sgr0
./generic_vocab_test.sh


tput setaf 4
echo
echo "###################################"
echo "testing translation"
tput sgr0
./translation_test.sh


tput setaf 4
echo
echo "##################################"
echo "testing topic vocab collection"
tput sgr0
./topic_vocab_test.sh


tput setaf 4
echo
echo "##################################"
echo "testing extended vocab collection"
tput sgr0
./extended_topic_vocab_test.sh





