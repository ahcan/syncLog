#!/bin/sh
while true
do
    /web/env/soap_thomson/bin/python /web/source/syncLog/getLog.py
    sleep 1s
done
