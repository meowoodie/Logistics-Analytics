#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import pandas as pd
import math
import os
import numpy as np
reload(sys)
sys.setdefaultencoding('utf-8')
from impala.dbapi import connect
import pandas as pd
import datetime
import time


hive_config = {}
#生产环境
hive_config['nrps'] = {
    'host': 'dbsit.sfdc.com.cn', # IP address
    'db': 'nrps-m', # database name
    'port': 3306, #port
    'user' : 'nrps', ### user
    'passwd' : '9mniswYpgo'  ### password`
}

hive_config['dm_oia'] = {
    'host': '10.202.77.200', # IP address
    'db': 'dm_oia', # database name
    'port': 10000, #port
    'user' : 'facility_location', ### user
    'passwd' : 'FL561042'  ### password`
}

def get_hive_cursor(conf):
    conn = connect(host=conf['host'], port=conf['port'], database=conf['db'],user = conf['user'],password=conf['passwd'], auth_mechanism='PLAIN')
    return conn.cursor()


hive = hive_config['dm_oia']
cursor = get_hive_cursor(hive)
sql = "select * from dm_oia.result_status"
cursor.execute(sql)
objs = cursor.fetchall()
cursor.close()
r_objs = pd.DataFrame(objs)
print r_objs
