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

@app.route("/analysis")
def Analysis():
    return render_template("analysis.html")

# API for searching similar company ids with their scores by query id
@app.route("/similarCompanies", methods=["POST"])
def similar_companies():
    matched_items = {}
    # Parse requested parameters
    print request.method
    if request.method == "POST":
    	para_dict   = json.loads(request.data)
        print para_dict
        company_id  = para_dict["companyId"]
        down_stream = para_dict["downStream"]
        up_stream   = para_dict["upStream"]
        rec_num     = int(para_dict["recNum"])
        areas       = para_dict["areas"]
        # fetch results from database
        res = recommend_res_handler[company_id]
        up_ids      = res["up_ids"][:rec_num]
        up_scores   = res["up_scores"][:rec_num]
        down_ids    = res["down_ids"][:rec_num]
        down_scores = res["down_scores"][:rec_num]
        if up_stream:
            unsorted_items = company_id_handler.get("company_id", up_ids)
            matched_items["ups"] = []
            for i in range(len(up_ids)):
                _id   = up_ids[i]
                score = up_scores[i]
                cand  = {}
                for item in unsorted_items:
                    if item["company_id"] == _id and item["area_code"] in areas:
                        cand = item
                        break
                cand["score"] = score
                matched_items["ups"].append(cand)
        if down_stream:
            unsorted_items = company_id_handler.get("company_id", down_ids)
            matched_items["downs"] = []
            for i in range(len(down_ids)):
                _id   = down_ids[i]
                score = down_scores[i]
                cand  = {}
                for item in unsorted_items:
                    if item["company_id"] == _id and item["area_code"] in areas:
                        cand = item
                        break
                cand["score"] = score
                matched_items["downs"].append(cand)
    else:
    	return json.dumps({
    		"status": 1,
    		"msg": "Invalid Request Type" })

    return json.dumps({
    	"status": 0,
    	"res": matched_items })
