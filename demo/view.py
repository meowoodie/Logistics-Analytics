#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is the main script for a Flask project, which defines various of interfaces for getting
access to backend services or data.
"""

import json
import arrow
from flask import Flask, request, url_for, render_template

from dao import BasicInfo, ReportText
 # from holmes.features.bow.feature import Feature

app = Flask(__name__)

# Global Variables
token = "gatech1234!"

# Data Handler
basic_info_handler  = BasicInfo(token)
report_text_handler = ReportText(token)

# NLP Model
# f = Feature()

# Renderring main web page
@app.route("/map")
def Map():
    return render_template("map.html")
@app.route("/recommendation")
def Recommendation():
    return render_template("recommendation.html")
# API for searching correlated crime records via crime id
@app.route("/searchCrimeId", methods=["POST"])
def searchCrimeId():
	crime_id   = ""
	limit      = 1
	start_time = 0
	end_time   = 0

	# Parse requested parameters
	if request.method == "POST":
		para_dict  = json.loads(request.data)
		crime_id   = para_dict["crimeId"]
		limit      = int(para_dict["limit"])
		start_time = int(para_dict["startTime"]/1000) # change milliseconds to seconds by /1000
		end_time   = int(para_dict["endTime"]/1000)   # change milliseconds to seconds by /1000
	else:
		return json.dumps({
			"status": 1,
			"msg": "Invalid Request Type"})

	# Get matched crime records by input crime id
	# matched_crimes = f.query_via_id(crime_id,limit)
	# if matched_crimes == None:
	# 	return json.dumps({
	# 		"status": 1,
	# 		"msg": "Invalid Crime ID"})

	matched_crimes = [['163560154', 0.20330104, 'ROB-STREET-GUN'], ['153322796', 0.2092959, 'ROB-STREET-GUN'], ['162021796', 0.21052736, ''], ['161070352', 0.21449465, 'ROB-STREET-GUN'], ['150772900', 0.23019572, ''], ['163572101', 0.30466831, 'FRAUD-IMPERS.<$10,000'], ['160362333', 0.40189749, 'THEFT OF TRUCK/VAN/BUS'], ['153142632', 0.41234228, 'DAMAGE TO PROP PRIVATE'], ['170160001', 1.0000001, 'Ped Robbery'], ['170152497', 1.0000001, 'ROB-STREET-GUN']]

	# Transpose the 2D list "matched_crimes".
	# And get informations by fields
	trans_mat    = map(list, zip(*matched_crimes)) # For Python 3.x: list(map(list, zip(*matched_crimes)))
	ids          = trans_mat[0]
	sims         = trans_mat[1]
	# Retrieve matched crime records' related informations by their ids.
	# Including: GPS positions, updated dates, and so on


	# basic_infos  = basic_info_handler.get("incident_num", ids, start_time, end_time)
	basic_infos  = basic_info_handler.get("incident_num", ids, start_time, end_time)
	if len(basic_infos) < 1:
		return json.dumps({
			"status": 0,
			"res": [] })

	filter_ids   = [ basic_info["id"] for basic_info in basic_infos ]
	dates 		 = [ basic_info["incident_date_timestamp"] for basic_info in basic_infos ]
	cities       = [ basic_info["city"] for basic_info in basic_infos ]
	positions    = [ (basic_info["avg_lat"], basic_info["avg_long"]) for basic_info in basic_infos ]
	priorities   = [ basic_info["priority"] for basic_info in basic_infos ]
	categories   = [ basic_info["category"] for basic_info in basic_infos ]

	report_texts = report_text_handler.get("incident_num", filter_ids)
	update_dates = [ report_text["update_date"] for report_text in report_texts ]
	remarks      = [ report_text["remarks"] for report_text in report_texts ]

	# Return reorganized data to the front-end
	return json.dumps({
		"status": 0,
		"res": [{
			"id": filter_ids[ind],
			"similarity": float(sims[ind]),
			"label": categories[ind],
			"position": { "lat": positions[ind][0], "lng": -1 * positions[ind][1] },
			"city": cities[ind],
			"priority": priorities[ind],
			"update_dates": update_dates[ind],
			"date": dates[ind],
			"text": remarks[ind] }
			for ind in range(len(filter_ids))
			if len(ids[ind]) >= 9 ]})



# API for searching correlated crime records by keywords
@app.route("/searchKeywords", methods=["POST"])
def searchKeywords():
	keywords   = ""
	limit      = 1
	start_time = 0
	end_time   = 0
	# Parse requested parameters
	if request.method == "POST":
		para_dict  = json.loads(request.data)
		keywords   = para_dict["keywords"].strip()
		limit      = int(para_dict["limit"])
		# start_time = int(para_dict["startTime"])
		# end_time   = int(para_dict["endTime"])
	else:
		return json.dumps({
			"status": 1,
			"msg": "Invalid Request Type" })

	matched_items = report_text_handler.getMatchedKeywords(keywords, limit)

	return json.dumps({
		"status": 0,
		"res": matched_items })

@app.route("/getSimilaritiesMatrix", methods=["POST"])
def getSimilaritiesMatrix():
	crime_ids = []
	if request.method == "POST":
		para_dict = json.loads(request.data)
		crime_ids = para_dict["crimeIds"]
	else:
		return json.dumps({
			"status": 1,
			"msg": "Invalid Request Type" })

	# return json.dumps({
	# 	"status": 0,
	# 	"res": f.get_similarity_matrix(crime_ids) })

	return json.dumps({
		"status": 0,
		"res": [] })

# API for getting basic info via crime ids
@app.route("/getBasicInfos", methods=["POST"])
def getBasicInfos():
	crime_ids = []
	# Parse requested parameters
	if request.method == "POST":
		para_dict  = json.loads(request.data)
		crime_ids  = para_dict["crimeIds"]
	else:
		return json.dumps({
			"status": 1,
			"msg": "Invalid Request Type" })

	basic_infos = basic_info_handler.get("incident_num", crime_ids)
	if basic_infos == None or basic_infos == []:
		return json.dumps({
			"status": 0,
			"res": [] })

	return json.dumps({
		"status": 0,
		"res": [{
			"id": basic_info["id"],
			"city": basic_info["city"],
			"date": basic_info["date"],
			"priority": basic_info["priority"],
			"label": basic_info["category"],
			"position": { "lat": basic_info["avg_lat"], "lng": -1 * basic_info["avg_long"] }}
			for basic_info in basic_infos] })



# API for getting remarks and updated date via crime id
@app.route("/getReportRemarks", methods=["POST"])
def getReportRemarks():
	crime_ids = []
	# Parse requested parameters
	if request.method == "POST":
		para_dict = json.loads(request.data)
		crime_ids = para_dict["crimeIds"]
	else:
		return json.dumps({
			"status": 1,
			"msg": "Invalid Request Type" })

	report_texts = report_text_handler.get("incident_num", crime_ids)
	if report_texts == None or report_texts == []:
		return json.dumps({
			"status": 0,
			"res": [] })

	return json.dumps({
		"status": 0,
		"res": report_texts })
