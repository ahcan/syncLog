from setting import settings
from setting.get_thomson_api import *
import setting
import pika
from RabbitMQ import *
import threading
import json
import logging, logging.config
import time

queLog = RabbitQueue('thomson_log')
queNewest = RabbitQueue('newest_log')
timeEnd = 0
timeStart = int(round(time.time()*1000))
def get_log(name = None):
    # name: thomson-name
    # return araay-dict
    return Log(name).get_log()

def get_max_logID(lstLog, maxlID):
    for item in lstLog:
        if not maxlID:
            maxlID = item['lid']
            print maxlID
        maxlID = item['lid'] if maxlID < item['lid'] else maxlID
    return maxlID

def set_log_2_que(lstLog, queLog, timeEnd, timeStart):
    args = []
    for item in lstLog:
        if (item['opdate'] > timeStart and  item['opdate'] <= timeEnd) or (item['cldate'] > timeStart and item['cldate'] <= timeEnd):
            args.append(item)
        print("opdate: %s cldate: %s---start: %s end: %s"%(item['opdate'], item['cldate'], timeStart, timeEnd))
    if len(args):
        queLog.push_queue(json.dumps(args))
        set_log_2_ryslog(args)
    return args

def set_log_2_ryslog(args):
    logger = logging.getLogger(__name__)
    try:
        for item in args:
            if item['sev'] == 'Critical':
                print("Critical")
                logger.critical(json.dumps(item))
            elif item['sev'] == 'Warning' or item['sev']=='Info':
                print("Warning")
                logger.warning(json.dumps(item))
            else:
                logger.error(json.dumps(item))
    except:
         print("No log")

def run(name = None, queNewest = None, queLog = None):
    ## name: thomson-name
    global timeStart, timeEnd
    logs = get_log(name)
    timeEnd =int(round(time.time()*1000))
    args = set_log_2_que(logs, queLog, timeEnd, timeStart)
    print("lenght log is added:%d"%(len(args)))
    print("lenght log is:%d"%(len(logs)))
    print("%s---%s"%(timeStart, timeEnd))
    # set_log_2_ryslog(args)
    timeStart = timeEnd
    time.sleep(5)

def main():
    name = 'thomson-hni'
    i =0
    while 1:
       run(name = name, queNewest = queNewest, queLog = queLog)
       print "finish"
       i +=1
       print i

if __name__ == '__main__':
    main()
