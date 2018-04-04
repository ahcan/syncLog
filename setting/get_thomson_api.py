import json
from xml.dom import minidom
import requests# $ pip install requests
from requests.auth import HTTPDigestAuth
from setting.DateTime import *
from setting import settings
##############################################################################
#                                                                            #
#-------------------------------------FILE-----------------------------------#
#                                                                            #
##############################################################################

class File:
    def __init__(self):
        #self.file_path = '/root/thomson_project/setting/responseXml/'
        self.file_path = 'setting/responseXml/'
        #self.file_path = '/home/huy/django_env/thomson_huynt/setting/responseXml/'

    def read(self, filename):
        #print self.file_path + filename
        f = open(self.file_path + filename , 'r')
        lines=f.read()
        f.close()
        #return data
        return lines

    def append(self, filename, text):
        f = open(self.file_path + filename, 'a')
        f.write(text+"\n")
        f.close()

    def get_response(self, filename):
        response = self.read(filename)
        return response

##############################################################################
#                                                                            #
#------------------------------------THOMSON---------------------------------#
#                                                                            #
##############################################################################

class Thomson:
    def __init__(self, name):
        # name: thomson-name
        self.user = settings.THOMSON_HOST[name]['user']
        self.passwd = settings.THOMSON_HOST[name]['passwd']
        self.url = settings.THOMSON_HOST[name]['url']
        self.name = name
    def get_response(self, headers, body):
        response = requests.post(self.url, data=body, headers=headers, \
            auth=HTTPDigestAuth(self.user, self.passwd), timeout=5)
        #print response.content
        response_xml = response.content[response.content.find('<soapenv:Envelope') :\
         response.content.find('</soapenv:Envelope>') + len('</soapenv:Envelope>')]
        return response_xml

    def get_datetime(self):
        from setting.xmlReq import DateAndTimeReq
        headers = DateAndTimeReq.HEADERS
        body = DateAndTimeReq.BODY
        print body
        #response_xml = self.get_response(headers, body)
        response_xml = File().get_response('GetDateAndTimeRsp.xml')
        print response_xml
        xmldoc = minidom.parseString(response_xml)
        itemlist = xmldoc.getElementsByTagName('GetDateAndTime:RspOkGetDate')
        DateAndTime = itemlist[0].attributes['DateAndTime'].value if \
        "'DateAndTime'" in str(itemlist[0].attributes.items()) else ""
        OlsonTZ = itemlist[0].attributes['OlsonTZ'].value if \
        "'OlsonTZ'" in str(itemlist[0].attributes.items()) else ""
        #Convert response data to Json
        args = []
        args.append({'dateAndTime'  : DateTime().conver_UTC_2_unix_timestamp(DateAndTime) \
            if DateAndTime else 1,
                    'timeZone'      : OlsonTZ if OlsonTZ else "Asia/Ho_Chi_Minh"
            })
        return json.dumps(args)

    def get_mountpoint(self):
        from setting.xmlReq import MountPointReq
        headers = MountPointReq.HEADERS
        body = MountPointReq.BODY
        #response_xml = self.get_response(headers, body)
        response_xml = File().get_response('GetMountPointsRsp.xml')
        xmldoc = minidom.parseString(response_xml)
        itemlist = xmldoc.getElementsByTagName('GetMountPoints:MountPoint')
        args = []
        for s in itemlist:
            Name = s.attributes['Name'].value if "'Name'" in \
            str(s.attributes.items()) else ""
            args.append({'name'             : Name if Name else ""
                })
        return json.dumps(args)

    def get_system_status(self):
        from setting.xmlReq import SystemReq
        headers = SystemReq.HEADERS
        body = SystemReq.BODY
        ##response_xml = self.get_response(headers, body)
        response_xml = File().get_response('SystemGetStatusRsp.xml')
        xmldoc = minidom.parseString(response_xml)
        itemlist = xmldoc.getElementsByTagName('sGetStatus:RspOkSGS')
        Status = itemlist[0].attributes['Status'].value if 'Status' in\
         str(itemlist[0].attributes.items()) else ""
        CPU = itemlist[0].attributes['CPU'].value if "'CPU'" in\
         str(itemlist[0].attributes.items()) else '-1'
        AllocCpu = itemlist[0].attributes['AllocCpu'].value if "'AllocCpu'" in\
         str(itemlist[0].attributes.items()) else '-1'
        Mem = itemlist[0].attributes['Mem'].value if "'Mem'" in\
         str(itemlist[0].attributes.items()) else '-1'
        AllocMem = itemlist[0].attributes['AllocMem'].value if "'AllocMem'" in\
         str(itemlist[0].attributes.items()) else '-1'
        agrs = []
        agrs.append({'status'   : Status,
                     'cpu'      : int(CPU),
                     'alloccpu' : int(AllocCpu),
                     'mem'      : int(Mem),
                     'allocmem' : int(AllocMem)
                    })
        # print self.user
        return json.dumps(agrs)

    def get_job_status(self):
        agrs = []
        agrs.append({
            'total'     :Job(self.name).count_job(),
            'running'   :Job(self.name).count_Running(),
            'completed' :Job(self.name).count_Completed(),
            'waiting'   :Job(self.name).count_Waiting(),
            'paused'    :Job(self.name).count_Paused(),
            'aborted'   :Job(self.name).count_Aborted()
            })
        return json.dumps(agrs)


    def get_license_xml(self):
        from setting.xmlReq.SystemReq import LICENSE_HEADERS, LICENSE_BODY
        headers = LICENSE_HEADERS
        body = LICENSE_BODY
        #response_xml = self.get_response(headers, body)
        response_xml = File().get_response('SystemGetVersionsRsp.xml')
        return response_xml

    def parse_license_xml_object(self, license_obj):
        str_license_obj = str(license_obj.attributes.items())
        Nb = license_obj.attributes['Nb'].value if "'Nb'" in str_license_obj else ''
        Name = license_obj.attributes['Name'].value if "'Name'" in str_license_obj else ''
        NbOfUsedLicenceDec = license_obj.attributes['NbOfUsedLicenceDec'].value if "'NbOfUsedLicenceDec'" in str_license_obj else ''
        NbOfUsedLicence = license_obj.attributes['NbOfUsedLicence'].value if "'NbOfUsedLicence'" in str_license_obj else ''
        Desc = license_obj.attributes['Desc'].value if "'Desc'" in str_license_obj else ''
        return Nb,Name,NbOfUsedLicenceDec,NbOfUsedLicence,Desc

    def parse_license(self, license_xml):
        xmldoc = minidom.parseString(license_xml)
        args=[]
        version_item = xmldoc.getElementsByTagName('sGetVersions:SRItem')
        str_version_obj = str(version_item[0].attributes.items())
        version = version_item[0].attributes['Ver'].value if "'Ver'" in str_version_obj else ''
        args_license=[]
        itemlist = xmldoc.getElementsByTagName('sGetVersions:LicItem')
        for license_obj in itemlist:
            Nb,Name,NbOfUsedLicenceDec,NbOfUsedLicence,Desc = self.parse_license_xml_object(license_obj)
            args_license.append({'license' : Desc,
                        'partnumber'       : Name,
                        'used'             : NbOfUsedLicenceDec,
                        'max'              : int(Nb)
                })
        args.append({
            'version'       : version,
            'license_list'  : args_license
            })
        return args

    def get_license(self):
        license_xml = self.get_license_xml()
        arr_license = self.parse_license(license_xml)
        return json.dumps(arr_license)


##############################################################################
#                                                                            #
#------------------------------------NODES-----------------------------------#
#                                                                            #
##############################################################################

class Node:
    def __init__(self, name):
        from setting.xmlReq import NodeReq
        headers = NodeReq.HEADERS
        body = NodeReq.BODY
        self.headers = headers
        self.body = body
        self.name = name

    def get_nodes_xml(self):
        #response_xml = Thomson(self.name).get_response(self.headers, self.body)
        response_xml = File().get_response('SystemGetNodesStatsRsp.xml')
        return response_xml

    def parse_dom_object(self, dom_object):
        text = str(dom_object.attributes.items())
        NStatus = dom_object.attributes['NStatus'].value if "'NStatus'" in text else ''
        Cpu = dom_object.attributes['Cpu'].value if "'Cpu'" in text else '-1'
        AllocCpu = dom_object.attributes['AllocCpu'].value if "'AllocCpu'" in text else '-1'
        Unreachable = dom_object.attributes['Unreachable'].value if "'Unreachable'" in text else ''
        NId = dom_object.attributes['NId'].value if "'NId'" in text else '-1'
        NState = dom_object.attributes['NState'].value if "'NState'" in text else ''
        Mem =  dom_object.attributes['Mem'].value if "'Mem'" in text else '-1'
        AllocMem = dom_object.attributes['AllocMem'].value if "'AllocMem'" in text else '-1'
        return NStatus,Cpu,AllocCpu,Unreachable,NId,NState,Mem,AllocMem

    def parse_xml(self, xml):
        args = []
        xmldoc = minidom.parseString(xml)
        itemlist = xmldoc.getElementsByTagName('sGetNodesStats:RspSGNSOk')
        for node in itemlist.item(0).childNodes:
            NStatus,Cpu,AllocCpu,Unreachable,NId,NState,Mem,AllocMem = self.parse_dom_object(node)
            JError, JCounter = NodeDetail(NId, self.name).count_job_error()
            args.append({'status'             : NStatus,
                        'cpu'                 : int(Cpu),
                        'alloccpu'            : int(AllocCpu),
                        'uncreahable'         : Unreachable,
                        'nid'                 : int(NId),
                        'state'               : NState,
                        'mem'                 : int(Mem),
                        'allocmem'            : int(AllocMem),
                        'jerror'              : JError,
                        'jcounter'            : JCounter
                })
        return json.dumps(args)

    def get_info(self):
        xml = self.get_nodes_xml()
        return self.parse_xml(xml)

class NodeDetail:

    def __init__(self, node_id, name):
        self.nid = int(node_id)
        self.name = name

    def get_dom_node(self):
        dom_node = None
        nodes_xml = Node(self.name).get_nodes_xml()
        xmldoc = minidom.parseString(nodes_xml)
        itemlist = xmldoc.getElementsByTagName('sGetNodesStats:RspSGNSOk')
        for node in itemlist.item(0).childNodes:
            text = str(node.attributes.items())
            NId = node.attributes['NId'].value if "'NId'" in text else -1
            if int(NId) == self.nid:
                dom_node = node
        return dom_node

    def get_array_job_id(self):
        array_jid = []
        dom_node = self.get_dom_node()
        for node_status_detail in dom_node.childNodes:
            text = str(node_status_detail.attributes.items())
            jid = node_status_detail.attributes['JId'].value if "'JId'" in text else ''
            if jid:
                array_jid.append(int(jid))
        return array_jid

    def get_list_job(self):
        args = []
        array_jid = self.get_array_job_id()
        dom_node = self.get_dom_node()
        NStatus,Cpu,AllocCpu,Unreachable,NId,NState,Mem,AllocMem = Node(self.name).parse_dom_object(dom_node)
        JError, JCounter = self.count_job_error()
        job_list = Job(self.name).get_job_detail_by_job_id(array_jid)
        args.append({'status'             : NStatus,
                    'cpu'                 : int(Cpu),
                    'alloccpu'            : int(AllocCpu),
                    'uncreahable'         : Unreachable,
                    'nid'                 : int(NId),
                    'state'               : NState,
                    'mem'                 : int(Mem),
                    'allocmem'            : int(AllocMem),
                    'jerror'              : JError,
                    'jcounter'            : JCounter,
                    'job_list'            : job_list
            })
        return json.dumps(args)

    def count_job_error(self):
        array_jid = self.get_array_job_id()
        job_list = Job(self.name).get_job_detail_by_job_id(array_jid)
        error=0
        for job in job_list:
            if job['status'] != 'Ok':
                error += 1
        return error, len(array_jid)
        
##############################################################################
#                                                                            #
#------------------------------------LOG-------------------------------------#
#                                                                            #
##############################################################################

class Log:
    def __init__(self, name):
        from setting.xmlReq.LogReq import HEADERS
        self.headers = HEADERS
        self.name  = name

    def parse_xml(self, xml):
        args = []
        xmldoc = minidom.parseString(xml)
        itemlist = xmldoc.getElementsByTagName('lGet:RspOkLog')
        for log in itemlist.item(0).childNodes:
            text = str(log.attributes.items())
            JId = log.attributes['JId'].value if "'JId'" in text else '-1'
            Cat = log.attributes['Cat'].value if "'Cat'" in text else ''
            LId = log.attributes['LId'].value if "'LId'" in text else ''
            try:
                Res = log.attributes['Res'].value if "'Res'" in text else ''
            except Exception as e:
                Res = ''
                #print text
            Res = log.attributes['Res'].value if 'Res' in text else ''
            JName = log.attributes['JName'].value if "'JName'" in text else ''
            NId =  log.attributes['NId'].value if "'NId'" in text else ''
            Sev = log.attributes['Sev'].value if "'Sev'" in text else ''
            Desc = log.attributes['Desc'].value if "'Desc'" in text else ''
            OpDate = log.attributes['OpDate'].value if "'OpDate'" in text else None
            ClDate = log.attributes['ClDate'].value if "'ClDate'" in text else None
            text = ''
            #Convert response data to Json
            args.append({'jid'             : int(JId),
                        'cat'              : Cat,
                        'lid'              : long(LId),
                        'res'              : Res,
                        'jname'            : JName,
                        'nid'              : int(NId),
                        'sev'              : Sev,
                        'desc'             : Desc,
                        'opdate'           : int(OpDate) if OpDate else None,
                        'cldate'           : int(ClDate) if ClDate else None
                })
        return args

    #Getting All Logs
    def get_log(self):
        from setting.xmlReq.LogReq import BODY
        body = BODY
        #response_xml = Thomson(self.name).get_response(self.headers, body)
        response_xml = File().get_response('LogsAllGetRsp.xml')
        return self.parse_xml(response_xml)

    #Getting Open Logs of All Severities
    def get_open(self):
        from setting.xmlReq.LogReq import OPEN
        body = OPEN
        #response_xml = Thomson(self.name).get_response(self.headers, body)
        response_xml = File().get_response('LogsOpenGetRsp.xml')
        #print response_xml
        return self.parse_xml(response_xml)

    #Getting All open log of Specific Jobs
    def get_by_jobID(self, jobID):
        from setting.xmlReq.LogReq import ID
        body = ID
        body = body.replace('JobID', str(jobID))
        response_xml = File().get_response('LogsGetByJobIDRsp.xml')
        #response_xml = Thomson(self.name).get_response(self.headers, body)
        return self.parse_xml(response_xml)

    def get_sys_log(self):
        from setting.xmlReq.LogReq import SYSTEM
        body = SYSTEM
        response_xml = File().get_response('LogsGetSysRsp.xml')
        #response_xml = Thomson(self.name).get_response(self.headers, body)
        return self.parse_xml(response_xml)


##############################################################################
#                                                                            #
#-----------------------------------WORKFLOW---------------------------------#
#                                                                            #
##############################################################################

class Workflow:
    def __init__(self, name):
        from setting.xmlReq.WorkflowReq import HEADERS
        self.headers = HEADERS
        self.name = name

    def parse_xml(self, xml):
        xmldoc = minidom.parseString(xml)
        itemlist = xmldoc.getElementsByTagName('wGetList:WItem')
        args=[]
        for s in itemlist:
            str_tmp = str(s.attributes.items())
            Name = s.attributes['Name'].value if "'Name'" in str_tmp else ''
            WId = s.attributes['WId'].value if "'WId'" in str_tmp else ''
            PubVer = s.attributes['PubVer'].value if "'PubVer'" in str_tmp else ''
            PriVer = s.attributes['PriVer'].value if "'PriVer'" in str_tmp else ''
            #Convert response data to Json
            args.append({'name'             : Name,
                        'wid'               : WId,
                        'pubver'            : int(PubVer),
                        'priver'            : int(PriVer)
                })
        return json.dumps(args)   

    def get_workflow(self):
        from setting.xmlReq.WorkflowReq import BODY
        body = BODY
        #response_xml = Thomson(self.name).get_response(self.headers, body)
        response_xml = File().get_response('WorklowGetListRsp.xml')
        return self.parse_xml(response_xml)

class WorkflowDetail:
    def __init__(self, wfid, name):
        from setting.xmlReq.WorkflowDetailReq import HEADERS, BODY
        self.headers = HEADERS
        self.body = BODY
        self.body = self.body.replace('WorkflowID', wfid)
        self.wfid = wfid
        self.name = name

    def parse_xml(self, xml):
        xmldoc = minidom.parseString(xml)
        wflist = xmldoc.getElementsByTagName('wd:Workflow')
        wf = wflist[0]
        wfname = wf.attributes['name'].value if "'name'" in \
        str(wf.attributes.items()) else ''
        wfid = wf.attributes['id'].value if "'id'" in \
        str(wf.attributes.items()) else ''
        wfpriority = wf.attributes['priority'].value if "'priority'" in \
        str(wf.attributes.items()) else ''
        wfcategory = wf.attributes['category'].value if "'category'" in \
        str(wf.attributes.items()) else ''
        wfcolor = wf.attributes['color'].value if "'color'" in \
        str(wf.attributes.items()) else ''
        args_param = []
        paramlist = xmldoc.getElementsByTagName('wd:Param')
        for param in paramlist:
            name = param.attributes['name'].value if "'name'" in \
            str(param.attributes.items()) else ''
            value = param.attributes['value'].value if "'value'" in \
            str(param.attributes.items()) else ''
            args_param.append({'name'              : name,
                               'value'             : value
                        })
        args = []
        args.append({'id'                      : wfid,
                     'name'                    : wfname,
                     'priority'                : wfpriority,
                     'category'                : wfcategory,
                     'color'                   : wfcolor,
                     'params'                  : args_param
                     })
        return json.dumps(args)

    def get_param(self):
        #response_xml = Thomson(self.name).get_response(self.headers, self.body)
        response_xml = File().get_response('WorkflowGetParamsRsp.xml')
        #print response_xml
        return self.parse_xml(response_xml)

##############################################################################
#                                                                            #
#------------------------------------JOB---------------*---------------------#
#                                                                            #
##############################################################################

class Job:
    def __init__(self, name):
        from setting.xmlReq.JobReq import HEADERS
        self.headers = HEADERS
        self.name = name

    def parse_dom_object(self, dom_object, workflow_list_json):
        str_tmp = str(dom_object.attributes.items())
        State = dom_object.attributes['State'].value if "'State'" in str_tmp else ''
        Status = dom_object.attributes['Status'].value if "'Status'" in str_tmp else ''
        JId = dom_object.attributes['JId'].value if "'JId'" in str_tmp else ''
        Prog = dom_object.attributes['Prog'].value if "'Prog'" in str_tmp else ''
        StartDate =  dom_object.attributes['StartDate'].value \
        if "'StartDate'" in str_tmp else ''
        Ver = dom_object.attributes['Ver'].value if "'Ver'" in str_tmp else ''
        EndDate = dom_object.attributes['EndDate'].value if "'EndDate'" in str_tmp else ''
        jobname, workflowIdRef = JobDetail(str(JId), self.name).get_job_name() if JId else ''
        '''Get workflow name'''
        workflow_name = ''
        workflow_list_json = json.loads(workflow_list_json)
        for workflow in workflow_list_json:
            if workflow['wid'] == workflowIdRef:
                workflow_name = workflow['name']
                break
        return State,Status,JId,Prog,StartDate,EndDate,Ver,jobname,workflowIdRef,workflow_name

    def parse_xml(self, xml):
        xmldoc = minidom.parseString(xml)
        itemlist = xmldoc.getElementsByTagName('jGetList:JItem')
        args=[]
        workflow_list_json = Workflow().get_workflow()
        for s in itemlist:
            State,Status,JId,Prog,StartDate,EndDate,Ver,jobname,workflowIdRef,workflow_name = self.parse_dom_object(s, workflow_list_json)
            args.append({'jname'    : jobname,
                        'wid'       : workflowIdRef,
                        'wname'     : workflow_name,
                        'state'     : State,
                        'status'    : Status,
                        'jid'       : int(JId),
                        # 'prog'      : int(Prog),
                        'startdate' : StartDate \
                        if StartDate else None,
                        # 'ver'       : int(Ver),
                        'enddate'   : EndDate \
                        if EndDate else None
                })
        return json.dumps(args)

    # return json theo name id job
    def parse_xml_name(self, xml):
        xmldoc = minidom.parseString(xml)
        itemlist = xmldoc.getElementsByTagName('jGetList:JItem')
        args=[]
        workflow_list_json = Workflow().get_workflow()
        for s in itemlist:
            State,Status,JId,Prog,StartDate,EndDate,Ver,jobname,workflowIdRef,workflow_name = self.parse_dom_object(s, workflow_list_json)
            args.append({'jname'    : jobname,
                        'jid'       : int(JId),
                })
        return json.dumps(args)

    def count_object(self, xml):
        xmldoc = minidom.parseString(xml)
        itemlist = xmldoc.getElementsByTagName('jGetList:JItem')
        return len(itemlist)


    def get_job_xml(self):
        from setting.xmlReq.JobReq import BODY
        body = BODY
        #response_xml = Thomson(self.name).get_response(self.headers, body)
        response_xml = File().get_response('JobGetListRsp.xml')
        return response_xml

    def get_jobid_list(self):
        response_xml = self.get_job_xml()
        xmldoc = minidom.parseString(response_xml)
        itemlist = xmldoc.getElementsByTagName('jGetList:JItem')
        args=[]
        for s in itemlist:
            str_tmp = str(s.attributes.items())
            JId = s.attributes['JId'].value if "'JId'" in str_tmp else ''
            args.append(int(JId))
        return args

    def get_job(self):
        #response_xml = self.get_job_xml()
        return self.parse_xml(response_xml)

    def get_job_name(self): # get name id job
        #response_xml = self.get_job_xml()
        return self.parse_xml_name(response_xml)

    def count_job(self):
        #response_xml = self.get_job_xml()
        return self.count_object(response_xml)

    def get_Waiting_xml(self):
        from setting.xmlReq.JobReq import WAITTING
        body = WAITTING
        #response_xml = Thomson(self.name).get_response(self.headers, body)
        response_xml = File().get_response('JobGetListRsp.xml')
        return response_xml

    def get_Waiting(self):
        #response_xml = self.get_Waiting_xml()
        return self.parse_xml(response_xml)

    def count_Waiting(self):
        #response_xml = self.get_Waiting_xml()
        return self.count_object(response_xml)

    def get_Running_xml(self):
        from setting.xmlReq.JobReq import RUNNING
        body = RUNNING
        #response_xml = Thomson(self.name).get_response(self.headers, body)
        response_xml = File().get_response('JobGetListRsp.xml')
        return response_xml

    def get_Running(self):
        xml = self.get_Running_xml()
        return self.parse_xml(xml)

    def count_Running(self):
        #response_xml = self.get_Running_xml()
        return self.count_object(response_xml)

    def get_Paused_xml(self):
        from setting.xmlReq.JobReq import PAUSED
        body = PAUSED
        #response_xml = Thomson(self.name).get_response(self.headers, body)
        response_xml = File().get_response('JobGetListRsp.xml')
        return response_xml

    def get_Paused(self):
        #response_xml = self.get_Paused_xml()
        return self.parse_xml(response_xml)

    def count_Paused(self):
        #response_xml = self.get_Paused_xml()
        return self.count_object(response_xml)

    def get_Completed_xml(self):
        from setting.xmlReq.JobReq import COMPLETED
        body = COMPLETED
        #response_xml = Thomson(self.name).get_response(self.headers, body)
        response_xml = File().get_response('JobGetListRsp.xml')
        return response_xml

    def get_Completed(self):
        #response_xml = self.get_Completed_xml()
        return self.parse_xml(response_xml)

    def count_Completed(self):
        #response_xml = self.get_Completed_xml()
        return self.count_object(response_xml)

    def get_Aborted_xml(self):
        from setting.xmlReq.JobReq import ABORTED
        body = ABORTED
        #response_xml = Thomson(self.name).get_response(self.headers, body)
        response_xml = File().get_response('JobGetListRsp.xml')
        return response_xml

    def get_Aborted(self):
        #response_xml = self.get_Aborted_xml()
        return self.parse_xml(response_xml)

    def count_Aborted(self):
        #response_xml = self.get_Aborted_xml()
        return self.count_object(response_xml)

    def get_job_detail_by_job_id(self, arr_job_id):
        #print arr_job_id
        job_xml = self.get_job_xml()
        xmldoc = minidom.parseString(job_xml)
        itemlist = xmldoc.getElementsByTagName('jGetList:JItem')
        args=[]
        workflow_list_json = Workflow(self.name).get_workflow()
        for job in itemlist:
            str_tmp = str(job.attributes.items())
            JId = job.attributes['JId'].value if "'JId'" in str_tmp else '-1'
            if int(JId) in arr_job_id:
                State,Status,JId,Prog,StartDate,EndDate,Ver,jobname,workflowIdRef,workflow_name = self.parse_dom_object(job, workflow_list_json)
                args.append({'jname'    : jobname,
                            'wid'       : workflowIdRef,
                            'wname'     : workflow_name,
                            'state'     : State,
                            'status'    : Status,
                            'jid'       : JId,
                            'prog'      : Prog,
                            'startdate' : DateTime().conver_UTC_2_unix_timestamp(StartDate) \
                            if StartDate else '',
                            'ver'       : Ver,
                            'enddate'   : DateTime().conver_UTC_2_unix_timestamp(EndDate) \
                            if EndDate else ''
                    })
        return args

class JobDetail:
    def __init__(self, jid, name):
        self.jid = jid
        self.name = name
    def parse_xml(self, xml):
        xmldoc = minidom.parseString(xml)
        joblist = xmldoc.getElementsByTagName('wd:Job')
        job = joblist[0]
        jobname = job.attributes['name'].value if "'name'" in \
        str(job.attributes.items()) else ''
        workflowIdRef = job.attributes['workflowIdRef'].value if \
        "'workflowIdRef'" in str(job.attributes.items()) else ''
        args_param = []
        paramlist = xmldoc.getElementsByTagName('wd:ParamDesc')
        for param in paramlist:
            name = param.attributes['name'].value if "'name'" in \
            str(param.attributes.items()) else ''
            value = param.attributes['value'].value if "'value'" in \
            str(param.attributes.items()) else ''
            args_param.append({'name'              : name,
                               'value'             : value
                        })
        args = []
        args.append({'jobname'                      : jobname,
                     'workflowIdRef'                : workflowIdRef,
                     'params'                       : args_param
                     })
        return json.dumps(args)

    def get_param_xml(self):
        from setting.xmlReq.JobDetailReq import HEADERS, BODY
        headers = HEADERS
        body = BODY
        body = body.replace('JobID', str(self.jid))
        #response_xml = Thomson(self.name).get_response(headers, body)
        response_xml = File().get_response('JobGetParamsRsp.xml')
        return response_xml

    def get_param(self):
        response_xml = self.get_param_xml()
        return self.parse_xml(response_xml)


    def get_job_name(self):
        #response_xml = self.get_param_xml()
        response_xml = File().get_response('JobGetParamsRsp.xml')
        xmldoc = minidom.parseString(response_xml)
        joblist = xmldoc.getElementsByTagName('wd:Job')
        job = joblist[0]
        jobname = job.attributes['name'].value if "'name'" in \
        str(job.attributes.items()) else ''
        workflowIdRef = job.attributes['workflowIdRef'].value if \
        "'workflowIdRef'" in str(job.attributes.items()) else ''
        return jobname, workflowIdRef
        
    def parse_status(self, xml):
        result = 'NotOK'
        try:
            xmldoc = minidom.parseString(xml)
            if xmldoc.getElementsByTagName('mg:RspNotOK'):
                message = xmldoc.getElementsByTagName('mg:RspNotOK')
                result = message[0].attributes['Desc'].value \
                 if "'Desc'" in str(message[0].attributes.items()) else result
            elif xmldoc.getElementsByTagName('mg:RspDone'):
                result = 'OK'
        except Exception as e:
            print e
            result = 'Unknow'
        return result

    def start(self, user):
        from setting.xmlReq.JobDetailReq import START_HEADERS, START_BODY
        headers = START_HEADERS
        body = START_BODY
        body = body.replace('JobID', str(self.jid))
        # response_xml = Thomson(self.name).get_response(headers, body)
        History().create_log(thomson_name=self.name, user=user, action='start', jid=self.jid, datetime=DateTime().get_now())
        time.sleep(0.5)
        try:
            node_ID = dbNodeDetail(self.name).get_node_by_job(self.jid)        
        except Exception as e:
            node_ID = 0
        # node_ID = dbNodeDetail(self.name).get_node_by_job(self.jid)        
        # status = self.parse_status(response_xml)
        return {'status': 'OK','nid': node_ID}

    def restart(self, user):
        if self.abort(user) == 'OK':
            time.sleep(1)
            # print self.start(user)['nid']
            return self.start(user)
        else :
            message = 'can not stop job'
            return message
        # return "Oke"+self.name
    def abort(self, user):
        from setting.xmlReq.JobDetailReq import ABORT_HEADERS, ABORT_BODY
        headers = ABORT_HEADERS
        body = ABORT_BODY
        body = body.replace('JobID', str(self.jid))
        # #response_xml = Thomson(self.name).get_response(headers, body)
        History().create_log(thomson_name=self.name, user=user, action='abort', jid=self.jid, datetime=DateTime().get_now())
        # return self.parse_status(response_xml)
        return "OK"

    def delete(self):
        from setting.xmlReq.JobDetailReq import DELETE_HEADERS, DELETE_BODY
        headers = DELETE_HEADERS
        body = DELETE_BODY
        body = body.replace('JobID', str(self.jid))
        #response_xml = Thomson(self.name).get_response(headers, body)
        return self.parse_status(response_xml)

##############################################################################
#                                                                            #
#------------------------------------MAIN------------------------------------#
#                                                                            #
##############################################################################
#
#if __name__ == "__main__":
    #print Thomson(self.name).get_nodes_status()
    #print Thomson(self.name).get_datetime()
    #print Thomson(self.name).get_mountpoint()
    #print Thomson(self.name).get_system_status()
    #print Log().get_log()
    #print Log().get_open()
    #print Job().get_Running()
    #Log().get_log()
    #print Log().get_by_jobID(530)
    #print Workflow().get_workflow()
    #Job().get_Running()
    #print WorkflowDetail('dsg').get_param()
    #print Thomson(self.name).get_system_status()
    #print Thomson(self.name).get_job_status()
    #print Node().get_info()
    #print Log().get_sys_log()
    #print Workflow().get_workflow()
    #print WorkflowDetail('AACEncoder').get_param()
    #print Job().get_job()

