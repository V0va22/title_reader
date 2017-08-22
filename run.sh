#!/usr/bin/env bash

read -s -p "Enter google Password: " mypassword
while :
do
    echo 'PID:'  $$
    python titlereader.py -u vvkohut@gmail.com -p $mypassword -pl 'Radio Roks Ballads' -s http://online-radioroks2.tavrmedia.ua/RadioROKS_Ballads
done