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

BASE_DOMAIN = "139.162.173.91"
# BASE_DOMAIN = "127.0.0.1"
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



class CompanyInfo(DBConnecter):

	def __init__(self, token):
		self.url   = "https://%s:%s/api/company_infos" % (BASE_DOMAIN, CONN_PORT)
		self.token = token
		DBConnecter.__init__(self, self.url, self.token)

class RecommendResult(DBConnecter):

	def __init__(self, token):
		self.url   = "https://%s:%s/api/recom_res" % (BASE_DOMAIN, CONN_PORT)
		self.token = token
		DBConnecter.__init__(self, self.url, self.token)

	@staticmethod
	def parse(result):
		return {
			"company_id":  result["company_id"],
			"up_ids":      result["up_ids"].split(","),
			"up_scores":   map(float, result["up_scores"].split(",")),
			"down_ids":    result["down_ids"].split(","),
			"down_scores": map(float, result["down_scores"].split(","))
		}



if __name__ == "__main__":

	# dao = CompanyInfo("gatech1234!")
	# print dao.get("company_id", ["0000841919", "0000536923"])

	dao = RecommendResult("gatech1234!")
	print dao["0000536923"]
