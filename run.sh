#!/usr/bin/env bash
if [ -z "$1" ]
  then
    read -s -p "Enter google Password: " mypassword
  else
    mypassword=$1
fi
while :
do
    echo 'PID:'  $$
    python titlereader.py -u vvkohut@gmail.com -p $mypassword -pl 'Radio Roks Ballads' -s http://online-radioroks2.tavrmedia.ua/RadioROKS_Ballads
done