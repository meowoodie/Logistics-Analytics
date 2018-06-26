#!usr/bin/env python 2.7
# -*- coding:utf-8 -*-

import sys
import math
import os
import numpy as np
from flask import Flask, request, session, g, redirect, url_for, abort, \
render_template, flash, jsonify
#from flask_restful import Api
from flask_restful import Api
import uuid

reload(sys)
sys.setdefaultencoding('utf-8')
from impala.dbapi import connect
import pandas as pd
import datetime
import time
from tasks import *
import ast


# initial api enviroment
app = Flask(__name__)
api = Api(app)
#api = restful.Api(app)

@app.route('/api/defaultPlan', methods=['GET', 'POST'])
def defaultPlan():
    if request.method == 'POST':
        # get parameters
        poststr = request.get_json()
        # print poststr, /////////////////////split the city code
        #citycode = poststr['cityCode']
        #cityname = poststr['cityName']
        #taskType = poststr['type']
        #predictedTm = poststr['predictedTime']
        #guId = poststr['guid']
        #empCode = poststr['empCode']
        #schemeName = poststr['schemeName']


        #poststr = request.get_json()
        #print poststr
        # run model
        #json_temp = {"cityCode": "020,755", "numOpen": "null", "time_ratio":"null", "unavailableAreaId" : "['12055','11955','12001']",
        #"unitCost35":"5.37", "unitCost70":"5.27", "unitCost140":"5.07", "unitCost200":"4.97", "unitCost300":"4.77", "classifierCost":"1000",
        #"classifierCostRange":"10", "unitBuildingCost":"3500", "buildingCostRange":"20", "humanCost":"8", "humanClassifyEfficiency":"550", "minParcelCnt":"50", "maxParcelCnt":"100", "areaEfficiency":"1", "timeEfficiency":"null", "billPackageRatio":"20", "predictYear":"2020"}
        #poststr = json.dumps(json_temp)
        #poststr = json.loads(poststr)


        citycode = poststr['cityCode']
        numOpen = poststr['numOpen']
        guId = uuid.uuid1()
        predictedTm = poststr['predictYear']
        time_ratio = poststr['time_ratio']
        unavailableAreaId = poststr['unavailableAreaId'].replace("[","")
        unavailableAreaId = unavailableAreaId.replace("]", "")
        unavailableAreaId = unavailableAreaId.replace("'", "")
        #unavailableAreaId = unavailableAreaId.replace("'", "")
        print unavailableAreaId.split(",")
        parameters = {'unitCost35':poststr['unitCost35'], 'unitCost70':poststr['unitCost70'], 'unitCost140':poststr['unitCost140'], 'unitCost200':poststr['unitCost200'], 'unitCost300':poststr['unitCost300'],
                      'classifierCost':poststr['classifierCost'], 'classifierCostRange': poststr['classifierCostRange'], 'unitBuildingCost':poststr['unitBuildingCost'], 'buildingCostRange':poststr['buildingCostRange'], 'humanCost':poststr['humanCost'], 'humanClassifyEfficiency':poststr['humanClassifyEfficiency'],
                      'minParcelCnt':poststr['minParcelCnt'], 'maxParcelCnt':poststr['maxParcelCnt'],'areaEfficiency':poststr['areaEfficiency'], 'timeEfficiency':poststr['timeEfficiency'], 'billPackageRatio':poststr['billPackageRatio']}

        lpNumTask(citycode.replace(',', '|'), numOpen, guId, predictedTm, unavailableAreaId, parameters, time_ratio)

        return jsonify({"modelTaskId": guId, "taskState": 'started', "cityCode": citycode})
    else:
        return 'Please use POST method!'


#defaultPlan()

@app.route('/api/adjustingPlan', methods=['GET', 'POST'])
def adjustingPlan():
    if request.method == 'POST':
        # get parameters
        poststr = request.get_json()
    #json_temp = {"cityCode": "020,755", "unitCost35": "5.37", "unitCost70": "5.27", "unitCost140": "5.07", "unitCost200": "4.97",
    #             "unitCost300": "4.77", "classifierCost": "1000",
    #             "classifierCostRange": "10", "unitBuildingCost": "3500", "buildingCostRange": "20", "humanCost": "8",
    #             "humanClassifyEfficiency": "550", "minParcelCnt": "50", "maxParcelCnt": "100", "areaEfficiency": "1",
    #             "timeEfficiency": "null", "billPackageRatio": "20", "predictYear": "2020",
    #             "candidatePoint":'''{"11968": ["755AP", "020LF", "755AG", "755AS", "755FP", "755DM", "755DQ", "755S", "755BG", "755BK"], "12000": ["020FE", "020JI", "020JD", "020JC", "020NK", "020PS", "020PV", "020NL", "020CB", "020CM", "020AG", "020EB", "020EC", "020EK", "020KB", "755D", "020C", "020N", "020K"], "11971": ["020PG", "020FA", "020NA", "020NC", "020NB", "020NR", "020NT", "020LW", "020V", "755CP", "020PT", "020PF", "755AK", "020NE", "020VB", "020S", "020CH", "020AD", "020AT", "020AQ", "020GA", "020GF", "020EA", "020ED", "020EE", "020EL", "020EM", "020EN", "755FD", "020MM", "020SE", "755BT", "020EG", "020E", "020A"], "12004": ["755AV", "755EV", "755EK", "755CF", "755AH", "755DK", "755FM", "755K", "755H", "755E", "755P", "755BD", "755BS", "755BP"], "12044": ["020BA", "020BM", "020BL", "020BI", "020BH", "020BK", "020BP", "020HB", "020HE", "020HD", "020LK", "020PC", "020TC", "020TB", "020CC", "020CK", "020AL", "020AJ", "020AK", "020AF", "020AC", "020AP", "020LH", "020KC", "020KA", "020MA", "020MC", "020M", "020H", "020T"], "11980": ["755AT", "755DG", "755DL", "755FG", "755G", "755T"], "11952": ["020BD", "020BG", "020BC", "020BB", "020FD", "020BQ", "020CF", "020DG", "020DF", "020DE", "020DA", "020JB", "020LN", "020LE", "020PH", "020TE", "020TA", "020AI", "020AA", "020LJ", "020LG", "020EF", "020KG", "020MB", "020B", "020L", "020J"], "11987": ["755EP", "755CA", "755CB", "755CK", "755CL", "755CQ", "755AM", "755AF", "755AR", "755AQ", "755DA", "755FK", "755FH", "755FB", "755DH", "755CN", "755M", "755A", "755BF", "755BJ", "020APAL"], "11957": ["755EB", "755CH", "755CM", "020AM", "755C", "755BH", "020D"], "11958": ["755EA", "755AJ", "755AE", "755AD", "755AB", "755EU", "755FU", "755FQ", "755FC", "755DF", "755B", "755BN", "755BL"], "12051": ["020FL", "020FG", "020FF", "020JK", "020JG", "020ND", "020NH", "020NN", "020Q", "020PB", "020PE", "020PD", "020PL", "020NF", "020NV", "020CD", "020CE", "020CA", "020CJ", "020AN", "020AB", "020EH", "020QG", "020QC", "020F", "020G"], "11993": ["020JL", "020JN", "020JH", "020HC", "755DJ", "755BC", "020QE"], "11963": ["755AN", "755AL", "755AC", "755AA", "755F", "755BA", "755BE"], "12032": ["755CE", "755CD", "755J", "755N", "755Q", "755U"]}'''}

    #poststr = json.dumps(json_temp)
    #poststr = json.loads(poststr)

        citycode = poststr['cityCode']
        guId = uuid.uuid1()
        predictedTm = poststr['predictYear']
        relation = ast.literal_eval(poststr['candidatePoint'])
        parameters = {'unitCost35': poststr['unitCost35'], 'unitCost70': poststr['unitCost70'],
                      'unitCost140': poststr['unitCost140'], 'unitCost200': poststr['unitCost200'],
                      'unitCost300': poststr['unitCost300'],
                      'classifierCost': poststr['classifierCost'], 'classifierCostRange': poststr['classifierCostRange'],
                      'unitBuildingCost': poststr['unitBuildingCost'], 'buildingCostRange': poststr['buildingCostRange'],
                      'humanCost': poststr['humanCost'], 'humanClassifyEfficiency': poststr['humanClassifyEfficiency'],
                      'minParcelCnt': poststr['minParcelCnt'], 'maxParcelCnt': poststr['maxParcelCnt'],
                      'areaEfficiency': poststr['areaEfficiency'], 'timeEfficiency': poststr['timeEfficiency'],
                      'billPackageRatio': poststr['billPackageRatio']}

        print relation.keys()
        lpAdjustTask(citycode.replace(',', '|'), guId, predictedTm, parameters, relation)

        return jsonify({"modelTaskId": guId, "taskState": 'started', "cityCode": citycode})
    else:
        return 'Please use POST method!'


#adjustingPlan()
## app config
if __name__ == '__main__':

    from werkzeug.contrib.fixers import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.config['JSON_SORT_KEYS'] = False
    app.run(host='0.0.0.0',port=5000)
