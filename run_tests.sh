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





