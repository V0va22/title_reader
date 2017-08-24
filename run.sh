#!/usr/bin/env bash
if [ -n "$1" ]
  then
    mypassword=$1

elif [ -n "$GMPASS" ]
  then
    mypassword=$GMPASS
else
    read -s -p "Enter google Password: " mypassword
fi
while :
do
    python titlereader.py -u vvkohut@gmail.com -p $mypassword -pl 'Radio Roks Ballads' -s http://online-radioroks2.tavrmedia.ua/RadioROKS_Ballads -bp $$
done