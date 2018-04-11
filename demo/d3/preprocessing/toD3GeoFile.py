'''
output two Geo location files for citys
'''
import json
import numpy as np

with open('areaInfo.js', 'r') as f:
    areaInfo = json.load(f)
wbc = []
wbc.append({"total": len(areaInfo)})
data1 = []
data2 = []
for key in areaInfo:
    dic1 = {
    "id":"",
    "iso2Code":"",
    "name":"",
    "capitalCity":"",
    "longitude":"",
    "latitude":""
    }
    dic2 = {
    "type":"Feature",
    "properties":{"name": ''},
    "geometry":{
        "type":"Polygon",
        "coordinates":[]
        },
    "id":''
    }
    dic1["id"] = areaInfo[key]['area_code']
    dic1["iso2Code"] = areaInfo[key]['area_code']
    dic1["name"] = areaInfo[key]['area_desc']
    if (key=='沈阳市'):
        dic1["longitude"] = '123.296'
        dic1["latitude"] = '41.805'
    elif(key=='绍兴市'):
        dic1["longitude"] = '120.51'
        dic1["latitude"] = '29.99'
    elif(key=='中山市'):
        dic1["longitude"] = '113.265'
        dic1["latitude"] = '22.51'
    elif(key=='西安市'):
        dic1["longitude"] = '108.82'
        dic1["latitude"] = '34.25'
    elif(key=='成都市'):
        dic1["longitude"] = '103.9354'
        dic1["latitude"] = '30.6587'

    else:
        dic1["longitude"] = areaInfo[key]["lng"]
        dic1["latitude"] = areaInfo[key]['lat']

    print(key)
    print(dic1["longitude"])
    print(dic1["latitude"])
    dic2['properties']['name'] = areaInfo[key]['area_desc']
    r = 1
    theta = np.arange(0, 2*3.14, 2*3.14/10)
    coor = [[float(dic1["longitude"])+ np.cos(t), float(dic1["latitude"]) + np.sin(t)] for t in theta]
    dic2["geometry"]["coordinates"].append(coor)
    dic2["id"] = dic1["id"]
    data1.append(dic1)
    data2.append(dic2)
wbc.append(data1)

world_countries = {
    "type": "FeatureCollection",
    "features":data2
}
with open("wbc2.js", "w") as f:
    json.dump(wbc, f)
with open("world-countries2.js", 'w') as f:
    json.dump(world_countries, f)
