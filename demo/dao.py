#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script contains an abstract interface for connecting various kinds of database via standard
restful API and the data models that web service needs. Generally speaking, the data models that 
you implement in web service inherit from interface 'DBConnecter' for getting access to the 
database. 
"""

import arrow
import json
import requests

#BASE_DOMAIN = "139.162.173.91"
BASE_DOMAIN = "127.0.0.1"
#CONN_PORT   = "3000"
CONN_PORT   = "3000"

class DBConnecter():
	"""
	A simple interface (abstract class) for connecting database via secured and standard 
	restful API. The data accessing API was provided by Loopback Database Wrapper, A simple
	loopback server. You can define your own result parser by overriding static method 
	"parse". 

	Parameters:
	- url:   Database restful API base url
	- token: Access token (required by the wrapper of database for safty)
	"""

	def __init__(self, url, token):
		if token == None:
			# TODO: If token was not set, it would request a new token from the server.
			# self.get_access_token()
			return 
		self.url     = url
		self.token   = token
		self.headers = { "Accept": "application/json", "Content-Type": "application/json" }

	def __getitem__(self, id):
		"""
		Rewrite built-in function __getitem__

		Retrieve one data item by its primary key, and return a python dict. The DAO (Data 
		Access Operation) was done by secured and standard Restful API which are provided 
		by Loopback Database Wrapper. 
		"""

		r = requests.get(url="%s/%s" % (self.url, id), headers=self.headers, 
			params={ "access_token": self.token }, verify=False)
		# Return result if success (status == 2XX)
		if r.status_code / 10 == 20:
			return self.parse(r.json())
		# Invalid request
		else:
			return r.json()

	def get(self, key, vals):
		"""
		Get Multiple Items

		Retrieve multiple data items by indicated key and its values. key is supposed to be
		a string, and vals is a list of values. Basically, this method is implemented by 
		sending a restful request with a filter parameter which contains a where filter. It
		would be a better way to fetch multiple data items rather than requesting by id for 
		many times. Noted that the response would return a list of intact data item, and 
		"parse" function would be applied here for each of the item by default. 
		"""

		key_vals = [ {key: val} for val in vals ]
		filter   = { "where": { "or": key_vals } }
		params   = { "access_token": self.token, "filter": json.dumps(filter) }
		r = requests.get(url=self.url, headers=self.headers, params=params, verify=False)

		# Return result if success (status == 2XX)
		if r.status_code / 10 == 20:
			return [ self.parse(item) for item in r.json() ]
		# Invalid request
		else:
			return r.json()

	@staticmethod
	def parse(result):
		"""
		Parse

		The static method would be invoked everytimes when __getitem__ was excuted (getting
		resource by id). it would help to parse the response and return to caller if this 
		method was overrided. In the abstract class DBConnecter, this method would do nothing
		but return response directly. 
		"""

		return result



class BasicInfo(DBConnecter):
	"""
	Basic Info 

	This class is a data model for the table "basic_info" of database "APD_Data" in local MySQL.
	Basically, this class persists a unique url (/api/basic_infos) for acquiring information
	from table "basic_info", and it also overrides the static method "parse" to extract specific
	fields of data from the raw response.
	"""

	def __init__(self, token):
		self.url   = "https://%s:%s/api/basic_infos" % (BASE_DOMAIN, CONN_PORT)
		self.token = token
		DBConnecter.__init__(self, self.url, self.token)

	def get(self, key, vals, start_time=None, end_time=None):
		"""
		Override function get in DBConnecter. 


		"""

		all_res = DBConnecter.get(self, key, vals)
		if start_time and end_time:
			all_res = [ item \
						for item in all_res 
						if item["incident_date_timestamp"] >= start_time and \
						   item["incident_date_timestamp"] <= end_time ]
		new_res = sorted(all_res, key=lambda k: k['incident_date_timestamp']) 
		return new_res

	@staticmethod
	def parse(result):
		"""
		Overriding of "parse" in DBConnecter
		
		This function mainly focus on parsing raw data in the response, which includes parsing 
		date string into unix timestamp, converting gps positions into float numbers and so on. And
		it would return None if there is any possible expection occurs at any time and throw a 
		self-defined exception to the console.
		"""
		# try:
		incident_num = result["incident_num"]
		avg_lat  = float(result["avg_lat"])/100000.0 
		avg_long = float(result["avg_long"])/100000.0 
		city     = result["city"].strip()
		date     = arrow.get(result["incident_date"], "YYYY-MM-DD HH:mm:ss").timestamp
		priority = int(result["priority"])

		category = result["crime_desc"]
		incident_date_timestamp = result["incident_date_timestamp"]

		# If the gps position is not located within the area of Atlanta
		if (avg_lat > 90 or avg_lat < -90) or \
			(avg_long > 180 or avg_long < -180):
			raise Exception("Invalid GPS position.")
			return None
		# If the priority is not included in 0 to 9
		if priority not in range(10):
			raise Exception("Invalid priority.")
			return None
		# Return parsed result
		return {
			"id":       incident_num,
			"avg_lat":  avg_lat,
			"avg_long": avg_long,
			"city":     city,
			"date":		date,
			"priority": priority,
			"category": category,
			"incident_date_timestamp": incident_date_timestamp
			}
		# Ensure the result can be returend as expected even if there is an unexpected exception
		# when parsing the raw data.
		# except Exception:
		# 	raise Exception("Invalid Data Format.")
		# 	return None

class ReportText(DBConnecter):
	"""
	Basic Info 

	This class is a data model for the table "report_text" of database "APD_Data" in local MySQL.
	Basically, this class persists a unique url (/api/report_text) for acquiring information
	from table "report_text", and it also overrides the static method "parse" to extract specific
	fields of data from the raw response.
	"""

	def __init__(self, token):
		self.url   = "https://%s:%s/api/report_texts" % (BASE_DOMAIN, CONN_PORT)
		self.token = token
		DBConnecter.__init__(self, self.url, self.token)

	def getMatchedKeywords(self, keywords, limit):
		"""
		Get Matched Keywords

		It would return the items whose "remarks" field contains the specific keywords. It basically
		utilizes the like and nlike operator in the mysql to generate a restful request. For now,
		it only supports querying one individous keyword (any string). 
		"""

		filter = { "limit": limit, 
			"where": { "remarks": { "like": "%c%s%c" % ("%", keywords ,"%"), "option": "i" } } }
		params = { "access_token": self.token, "filter": json.dumps(filter) }
		r = requests.get(url=self.url, headers=self.headers, params=params, verify=False)
		# Return result if success (status == 2XX)
		if r.status_code / 10 == 20:
			return [ self.parse(item,keywords) for item in r.json() ]
		# Invalid request
		else:
			return r.json()

	@staticmethod
	def parse(result,keywords = ""): 
		"""
		Overriding of "parse" in DBConnecter
		
		This function mainly focus on parsing raw data in the response, which includes parsing 
		date string into unix timestamp, extracting text part from remarks and so on. And it
		would return None if there is any possible expection occurs at any time and throw a 
		self-defined exception to the console.
		"""
		try:
			incident_num = result["incident_num"]
			update_date  = arrow.get(result["ent_upd_datetime"], "YYYY-MM-DD HH:mm:ss").timestamp
			remarks      = result["remarks"]
			
			# Return parsed result
			return {
				"id":          incident_num,
				"update_date": update_date,
				"remarks":     remarks
			}
		# Ensure the result can be returend as expected even if there is an unexpected exception
		# when parsing the raw data.
		except Exception:
			raise Exception("Invalid Data Format.")
			return None



if __name__ == "__main__":

	# dao = DBConnecter("https://139.162.173.91:3000/api/basic_infos", "gatech1234!")
	# print dao["161881787"]

	# dao = DBConnecter("https://139.162.173.91:3000/api/basic_infos", "gatech1234!")
	# print dao.get("incident_num", ["130010040", "130010041", "130010039"])

	# dao = BasicInfo("gatech1234!")
	# print dao.get("incident_num", ["130010040", "130010038", "130010039"])

	dao = ReportText("gatech1234!")
	# print dao.get("incident_num", ["130010077", "130010038", "130010027"])
	print dao.getMatchedKeywords("liberty pkwy nw")
