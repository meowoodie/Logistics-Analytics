#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is the main script for a Flask project, which defines various of interfaces for getting
access to backend services or data.
"""

import json
import arrow
from flask import Flask, request, url_for, render_template

from dao import CompanyInfo, RecommendResult

app = Flask(__name__)

# Global Variables
token = "gatech1234!"

# Data Handler
company_id_handler    = CompanyInfo(token)
recommend_res_handler = RecommendResult(token)

# Renderring main web page
@app.route("/recommendation")
def Recommendation():
    return render_template("recommendation.html")

# API for searching similar company ids with their scores by query id
@app.route("/similarCompanies", methods=["POST"])
def similar_companies():
	matched_items = {}
	# Parse requested parameters
	if request.method == "POST":
		para_dict   = json.loads(request.data)
		company_id  = para_dict["companyId"]
		down_stream = para_dict["downStream"]
        up_stream   = para_dict["upStream"]
        rec_num     = para_dict["recNum"]
        areas       = para_dict["areas"]
        # fetch results from database
        res = recommend_res_handler[company_id]
        up_ids      = res["up_ids"][:rec_num]
        up_scores   = res["up_scores"][:rec_num]
        down_ids    = res["down_ids"][:rec_num]
        down_scores = res["down_scores"][:rec_num]
        if up_stream:
            matched_items["ups"] = company_id_handler[up_ids]
        if down_stream:
            matched_items["downs"] = company_id_handler[down_ids]
	else:
		return json.dumps({
			"status": 1,
			"msg": "Invalid Request Type" })

	return json.dumps({
		"status": 0,
		"res": matched_items })
