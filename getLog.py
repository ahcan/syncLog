from setting import settings
from setting.get_thomson_api import *
# import setting
import pika
from RabbitMQ import *
import threading
import json
import logging, logging.config

queLog = RabbitQueue('thomson_log')
queNewest = RabbitQueue('newest_log')
maxlID = 0
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

def set_log_2_que(lstLog, queLog, maxlID):
    args = []
    for item in lstLog:
        if item['lid'] >= maxlID:
            args.append(item)
            print item['lid']
    queLog.push_queue(json.dumps(args))
    return args

def set_log_2_ryslog(args):
    logger = logging.getLogger(__name__)
    for item in args:
        if item['sev'] == 'Info':
            logger.info(json.dumps(item))
        elif item['sev'] == 'Critical':
            logger.critical(json.dumps(item))
        elif item['sev'] == 'Warning':
            logger.warning(json.dumps(item))
        else:
            logger.error(json.dumps(item))

def run(name = None, queNewest = None, queLog = None):
    ## name: thomson-name
    global maxlID
    logs = get_log(name)
    maxlID = get_max_logID(logs, maxlID)
    args = set_log_2_que(logs, queLog, maxlID)
    print len(args)
    set_log_2_ryslog(args)

def main():
    name = 'thomson-hcm'
    run(name = name, queNewest = queNewest, queLog = queLog)
    print "finish"

if __name__ == '__main__':
    main()