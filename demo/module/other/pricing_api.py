# -*- coding: utf-8 -*-


from flask import Flask, request, session, g, redirect, url_for, abort, \
render_template, flash, jsonify
from flask_restful import Api
from flask import Response

from src.data_handle.prepare_data import *
from src.data_handle.feature_extract import *
from src.model.model import *

from pricing_model import *
from model_params_config import *

import pandas as pd
import json
import os
import re

import pickle

app = Flask(__name__)
api = Api(app)

# 缺失值填充模型位置
imp_path = "model/feature_engineer/imputer_1.pkl"

# 数据归一化模型位置
scaler_path = "model/feature_engineer/scaler_1.pkl"

# xgboost模型位置
model_path = "model/gbdt/gbdt_full.bin"

# 数据特征映射字典位置
path_to_dict = "data/feature_dict/mapping_dict.pkl"

# 测试数据位置
path_test = "data/rawdata/final_tender_contest_test.csv"
#测试数据temp位置
path_test_temp = "data/rawdata/tt_combine_testTry.csv"

# 读取测试数据， 对于API接口，需要自行拼凑出相同字段的字典。 包含以下字段
"""
contestNo
lineId
tenderDepteCode
vehicleClassify
lineRunningCode
vehicleTon
totalKilogram
totalDistance
isStops
quoteStartDate
quoteEndDate
effectiveDate
expiryDate
runCycle
runPattern
runNum
transportLevel
carriageMode
originDeptCode
destinationDeptCode
isNeedImportedcar
isNeedLoadingserve
lineSource
lineDepteCode
forWorkingDays
bizType
contestUnit
combinationCode
resultPrice
tradeType
total_route_prices
total_route_price_with_one_ways
tolls_sum,route_price
vehicle_fix
vehicel_flex
person_fix
person_flex
"""

@app.route('/api/guiding_price', methods=['GET', 'POST'])
def pricing2():
    try:
        #Get path
        folderpath = os.path.abspath(os.path.dirname(os.getcwd()))

        #get support data file
        # map_ = folderpath + '/gbdt_deploy/data/city_oil_price.csv'
        # f = open(dat_oil_price_file, encoding='gbk')
        # dat_oil_price = pd.read_csv(f)

        dat_oil_price_file = folderpath + '/gbdt_deploy/data/city_oil_price.csv'
        f = open(dat_oil_price_file, encoding='gbk')
        dat_oil_price = pd.read_csv(f)

        dat_fuel_agg_merge_summary_file = folderpath + '/gbdt_deploy/data/dat_fuel_agg_merge_summary.csv'
        f = open(dat_fuel_agg_merge_summary_file, encoding='gbk')
        dat_fuel_agg_merge_summary = pd.read_csv(f)

        dat_organization_city_file = folderpath + '/gbdt_deploy/data/dat_organization_city.csv'
        f = open(dat_organization_city_file, encoding='gbk')
        dat_organization_city = pd.read_csv(f)

        dat_city_code_file = folderpath + '/gbdt_deploy/data/dat_city_code.csv'
        f = open(dat_city_code_file, encoding='gbk')
        dat_city_code = pd.read_csv(f)

        oil_price_average = sum(dat_oil_price['oil_price'].tolist()) / len(dat_oil_price['oil_price'].tolist())

        folderpath = os.path.abspath(os.path.dirname(os.getcwd()))

        #read json data from api and run predict model
        if request.method == 'POST':
            # get parameters
            poststr = request.get_json()

            # 检查lineRunningCode是否有中文字符
            test_lineRC_string = str(poststr["lineRunningCode"])
            zhPattern = re.compile(u'[\u4e00-\u9fa5]+')
            match = zhPattern.search(test_lineRC_string)
            # 将中文字符的项设为None
            if match:
                # print(u'有中文：%s' % (match.group(0),))
                poststr["lineRunningCode"] = None

            #save parameters to be local variable
            lineId = poststr['lineId']  #
            # reqId = poststr['reqId']
            tenderDepteCode = poststr['tenderDepteCode']  #

            vehicleClassify = poststr['vehicleClassify']  #
            combinationCode = poststr['combinationCode']
            lineRunningCode = poststr['lineRunningCode']
            # vehicleTon = poststr['vehicleTon'].replace("T","")
            vehicleTon = poststr['vehicleTon']
            totalKilogram = poststr['totalKilogram']  #
            totalDistance = poststr['totalDistance']
            isStops = poststr['isStops']  #
            effectiveDate = poststr['effectiveDate']  #
            expiryDate = poststr['expiryDate']  #
            runCycle = poststr['runCycle']  #
            runPattern = poststr['runPattern']
            runNum = poststr['runNum']  #

            try:
                transportLevel = poststr['transportLevel']
            except:
                transportLevel = poststr['线路等级']

            if transportLevel == '一级运输':
                transportLevel = 1
            if transportLevel == '二级运输':
                transportLevel = 2
            if transportLevel == '三级运输':
                transportLevel = 3


            carriageMode = poststr['carriageMode']  #
            originDeptCode = poststr['originDeptCode']
            destinationDeptCode = poststr['destinationDeptCode']

            isNeedImportedcar = poststr['isNeedImportedcar']  #
            isNeedLoadingserve = poststr['isNeedLoadingserve']  #

            lineSource = poststr['lineSource']  #
            lineDepteCode = poststr['lineDepteCode']  #

            forWorkingDays = poststr['forWorkingDays']  #
            bizType = poststr['bizType']  #

            startDeptLongitude = poststr['startDeptLongitude']
            startDeptLatitude = poststr['startDeptLatitude']
            #if startDeptLongitude==None:


            destDeptLongitude = poststr['destDeptLongitude']
            destDeptLatitude = poststr['destDeptLatitude']

            # 解决输出时间格式问题
            planStartNearTime = poststr['planStartNearTime']
            planStartNearTime = planStartNearTime.replace("/", "-")
            planStartTime = poststr['planStartTime']
            planStartTime = planStartTime.replace("/", "-")
            planDestEndTime = poststr['planDestEndTime']
            planDestEndTime = planDestEndTime.replace("/", "-")
            acrossDayNum = poststr['acrossDayNum']

            reqId = poststr['reqId']
            # linePackageType = poststr['linePackageType']
            contestUnit = poststr['contestUnit']

            quoteStartDate = poststr['quoteStartDate']
            quoteEndDate = poststr['quoteEndDate']

            tradeType = poststr['tradeType']

            # stoppingPoints = poststr['stoppintPoints']

            # 求平均油耗
            mean_oil_consume = dat_fuel_agg_merge_summary['oil_consume.x'].mean()
            oil_consume_row = dat_fuel_agg_merge_summary[dat_fuel_agg_merge_summary['ton'] == float(vehicleTon)]
            # 如果对应ton在列表上找不到就用平均油耗
            try:
                oil_consume = oil_consume_row['oil_consume.x'].tolist()[0] * 100
            except:
                oil_consume = mean_oil_consume

            # dist_code = re.findall('([0-9]*)[A-Z]*', originDeptCode)[0]
            dist_code = re.findall('[PM]*([0-9]*)[A-Z]*', originDeptCode)[0]
            if int(dist_code) not in dat_organization_city['city'].tolist():
                dist_code = re.findall('([0-9]*)', tenderDepteCode)[0]

            try:
                ##find the province
                prov_row = dat_city_code[dat_city_code['V1'] == int(dist_code)]
                prov_temp = prov_row['prov'].tolist()[0]

                oil_price_row = dat_oil_price[dat_oil_price['city'] == prov_temp]
                oil_price = oil_price_row['oil_price'].tolist()[0]
            except:
                oil_price = oil_price_average

            #prepare parameter for pricing model to get part dat_history
            route_info_row = {"originDeptCode": originDeptCode, "destinationDeptCode": destinationDeptCode,
                              "startDeptLongitude": startDeptLongitude,
                              "startDeptLatitude": startDeptLatitude, "destDeptLongitude": destDeptLongitude,
                              "destDeptLatitude": destDeptLatitude, "vehicleTon": vehicleTon,
                              "totalDistance": totalDistance,
                              "lineDepteCode": lineDepteCode, "runPattern": runPattern, "transportLevel": transportLevel,
                              "planStartNearTime": planStartNearTime + ':00', "planStartTime": planStartTime + ':00',
                              "planDestEndTime": planDestEndTime + ':00',
                              "acrossDayNum": acrossDayNum}

            #get new feature from pricing model
            total_route_price, total_route_price_with_one_way, toll_sum, route_price, vehicle_fix, vehicle_flex, person_fix, person_flex = pricing(route_info_row)
            #print('total_route_price, total_route_price_with_one_way ,toll_sum, route_price, vehicle_fix, vehicle_flex, person_fix, person_flex')
            #print(total_route_price, total_route_price_with_one_way, toll_sum, route_price, vehicle_fix, vehicle_flex,person_fix, person_flex)
            #'hh_line_package_code': [combinationCode], 'cx_line_package_code': [combinationCode]
            #'approved_oil_price': [str(oil_price)],
            #'approved_oil_wear': [str(oil_consume)],
            #'win_bid_price': ['4'],
            #'quote_unit': ['2'], 'appoint_price': ['2'], 'appoint_unit': ['7']

            #create tt_combine_testTry
            ####contestNo unknown; ResultPrice unknown;
            tt_combine_testTry = {'contestNo': ['2'], 'lineId': [lineId], 'tenderDepteCode': [tenderDepteCode],
                                  'vehicleClassify': [vehicleClassify],'lineRunningCode': [lineRunningCode],
                                  'vehicleTon': [vehicleTon],'totalKilogram': [totalKilogram], 'totalDistance': totalDistance,
                                  'isStops': [isStops],'quoteStartDate':[quoteStartDate],'quoteEndDate':[quoteEndDate],
                                  'effectiveDate': [effectiveDate], 'expiryDate': [expiryDate],
                                  'runCycle': [runCycle], 'runPattern': [runPattern], 'runNum': [runNum],
                                  'transportLevel': [transportLevel], 'carriageMode': [carriageMode],
                                  'originDeptCode': [originDeptCode], 'destinationDeptCode': [destinationDeptCode],
                                  'isNeedImportedcar': [isNeedImportedcar],
                                  'isNeedLoadingserve': [isNeedLoadingserve], 'lineSource': [lineSource],
                                  'lineDepteCode': [lineDepteCode], 'forWorkingDays': [forWorkingDays], 'bizType': [bizType],
                                  'contestUnit':[contestUnit],'combinationCode':[combinationCode],'resultPrice':['0'],
                                  'tradeType':[tradeType],'total_route_prices':[total_route_price],
                                  'total_route_price_with_one_ways':[total_route_price_with_one_way],'tolls_sum':[toll_sum],
                                  'route_price':[route_price],'vehicle_fix':[vehicle_fix],'vehicel_flex':[vehicle_flex],
                                  'person_fix':[person_fix],'person_flex':[person_flex]}

            tt_combine_testTrytemp = pd.DataFrame(data=tt_combine_testTry)
            #print('tt_combine_testTrytemp.shape 1',tt_combine_testTrytemp.shape)
            #tt_combine_testTry=pd.concat([tt_combine_testTrytemp, tt_combine_testTrytemp])
            #print('tt_combine_testTrytemp.shape 2', tt_combine_testTrytemp.shape)
            #tt_combine_testTry.drop(columns=0)
            tt_combine_testTrytemp.to_csv(folderpath + "/gbdt_deploy/data/rawdata/tt_combine_testTry.csv",index=None)

            #####replace this!!!
            #tt_combine_test = pd.read_csv(path_test, low_memory=False).head()
            tt_combine_testTry_final = pd.read_csv(path_test_temp, low_memory=False).head()
            #print('tt_combine_testTry_final.shape', tt_combine_testTry_final.shape)
            #print(tt_combine_testTry_final)
            #tt_combine_testTry_final = pd.read_csv(path_test, low_memory=False).head()

            # 载入模型和字典， API服务启动后需要先把模型读入内存。
            bst, imp, scaler, map_dict = model_init(model_path=model_path,
                                                    imputer_path=imp_path,
                                                    scaler_path=scaler_path,
                                                    map_dict_path=path_to_dict,
                                                    params=PARAMS)

            #print('scaler',scaler)
            # 特征映射
            tt_combine, tt_combine_onehot = prepare_test_data(tt_combine_testTry_final, map_dict)

            # 缺失值填充和数据标准化
            data = feature_engineer_predict(data_clean_onehot=tt_combine_onehot,
                                            data_clean=tt_combine,
                                            imputer=imp,
                                            scaler=scaler)

            # 预测
            x_test = data['features']
            meta = data['meta']
            #data_test_full = predict(bst, x_test, meta, tt_combine)
            predict_price = predict(bst, x_test, tt_combine)['predict_price'].tolist()[0]
            print([lineId, predict_price])
            return jsonify({"success": "Y", "resultPrice": predict_price, "errorMessage": "N", "reqId": reqId})

        else:
            return 'Please use POST method!'
    except:
        poststr = request.get_json()
        reqId = poststr['reqId']
        return jsonify({"success": "N", "resultPrice": 'null', "errorMessage": "Y", "reqId": reqId})


@app.route('/healthCheck', methods=['GET', 'POST'])
def healthCheck():
    response = {"code": 0, "message": "service start"}
    resp = Response(json.dumps(response))
    resp.headers['Content-Type'] = 'application/json;charset=UTF-8'
    return resp


#@app.route('/api/guiding_price', methods=['GET', 'POST'])
if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 8080, debug=True)