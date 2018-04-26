from setting import settings
from setting.get_thomson_api import *
import setting
import pika
from RabbitMQ import *
import threading
import json
import logging, logging.config
import time

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
        #args.append(item)
        # print("opdate: %s cldate: %s---start: %s end: %s"%(item['opdate'], item['cldate'], timeStart, timeEnd))
    if len(args):
        queLog.push_queue(json.dumps(args))
    return args

def set_log_2_ryslog(args, name):
    ## name handler : thomsn-name
    logger = logging.getLogger(name)
    if len(args):
        try:
            for item in args:
                if item['sev'] == 'Critical':
                    #print("Critical")
                    logger.critical(json.dumps(item))
                elif item['sev'] == 'Warning' or item['sev']=='Info':
                    #print("Warning")
                    logger.warning(json.dumps(item))
                else:
                    logger.error(json.dumps(item))
        except Exception as e:
            print e
        return "Add log"
    else:
        return "No log"

def run(name = None, queNewest = None, queLog = None, timeStart = 0, timeEnd = 0):
    ## name: thomson-name
    queLog = RabbitQueue('thomson_log')
    queNewest = RabbitQueue('newest_log')
    logs = get_log(name)
    # timeEnd =int(round(time.time()*1000))
    args = set_log_2_que(logs, queLog, timeEnd, timeStart)
    print ("host: %s"%(name))
    print("lenght log is added:%d"%(len(args)))
    print("lenght log is:%d"%(len(logs)))
    # print("%s---%s"%(timeStart, timeEnd))
    set_log_2_ryslog(args, name)
    # timeStart = timeEnd
    # time.sleep(5)
    print("%s finish!!"%(name))
    return timeEnd

def work_thread(hostname = None, queLog = None, queNewest = None, timeStart = 0):
    # while True:
    timeStart =  run(name = hostname, queNewest=queNewest, queLog=queLog, timeStart = timeStart)
        #timeStart = timeTMP
    # print("%s finsh!!"%(hostname))
queTimeStart = RabbitQueue('time_log_start')
queTimeEnd = RabbitQueue('time_log_end')
if __name__ == '__main__':
    threads = []
    #try:
    #    print(queTimeStart.get_queue(no_ack=False)[0][2])
    #except:
    #    print('no')
    if queTimeStart.get_queue(no_ack=False):
        timeStart = int(queTimeStart.get_queue(no_ack=True)[0][2])
    else:
        timeStart = int(time.time()*1000)
    time.sleep(2)
    timeEnd = int(time.time()*1000)
    queTimeStart.push_queue(str(timeEnd))
    for item in settings.THOMSON_HOST:
        threads.append(threading.Thread(target=run, kwargs={'name': item, 'timeStart': timeStart, 'timeEnd': timeEnd}))
    for thread in threads:
        thread.daemon = True
        thread.start()
        thread.join()
    print('start: %s - end:%s'%(timeStart, timeEnd))
