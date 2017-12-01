#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import arrow
import argparse
import numpy as np

from graph import Graph
from geopy.geocoders import Nominatim
from collections import defaultdict
from pprint import pprint


class SfExpressGraph(Graph):
	"""
	SF-Express Graph

	Subclass of Graph for converting SF-Express logistics records into graph 
	data structure. It mainly override the preprocess method in order to adapt
	its own business logic. 
	"""

	def __init__(self, iterobj=None):
		# Definition of nodes
		company_info_terms = [
			"company_id", "business", "oversea","industry_lv1", "industry_lv2", \
			"industry_lv3", "area_code", "area_desc", "area_city", "coop_months" ]
		# Definition of links
		transac_info_terms = [
			"transac_id", "ship_time", "deliver_time", "ship_compony_id", "deliver_company_id"]
		# Initialize graph object
		Graph.__init__(self, iterobj=iterobj,
			node_terms=company_info_terms, link_terms=transac_info_terms)

	def preprocess(self, record):
		"""
		Override preprocess of class graph. This function defines the companies as
		nodes and shipment transactions as links, and extracts the information from 
		raw records
		"""
		# Terms about company information
		company_pair = [ record[0:10], record[13:23] ]
		# Terms about transaction information
		transac_info = record[10:13] + [ record[0], record[13] ]
		# Terms about item information
		item         = [] if record[23].strip() == "NULL" else json.loads(record[23].strip())
		# Adding link information
		self.links.append(dict(zip(self.link_terms, transac_info)))
		# Adding company information
		for company in company_pair:
			if company[0] not in self.nodes:
				self.nodes[company[0]] = dict(zip(self.node_terms, company))

	def postprocess(self):
		"""
		Override postprocess of class graph. Reformat some data fields of nodes 
		and links, majorly converting Chinese characters into other formats like 
		booleans, numbers or english words. 
		"""
		# Convert cityname into its latitude and longitude, and reorganize them into 
		# a dictionary.
		def getGeoByCity(cityname):
			# Remove slash from the city name
			cityname = cityname.strip().split("/")[0]
			try: 
			    geolocator = Nominatim()
			    location2 = geolocator.geocode(cityname)
			    lat = location2.latitude
			    lng = location2.longitude
			except:
				lat = None
				lng = None
			return { "city_name": cityname, "lat": lat, "lng": lng }

		print("Getting cities\" geolocation ...")
		cities_geo = { city: getGeoByCity(city)
			for city in list(set([ node["area_city"] for node in self.nodes.values() ])) }
		pprint(cities_geo)

		print("Reformatting nodes ...")
		# Reformat nodes
		for company_id, company_info in self.nodes.items():
			company_info["oversea"]   = True if company_info["oversea"] == "是" else False
			company_info["area_city"] = cities_geo[company_info["area_city"]]

		print("Reformatting links ...")
		# Reformat links
		for link in self.links:
			link["ship_time"]    = None if link["ship_time"] == "NULL" \
		        else arrow.get(link["ship_time"], "YYYY-MM-DD HH:mm:ss").timestamp
			link["deliver_time"] = None if link["deliver_time"] == "NULL" \
				else arrow.get(link["deliver_time"], "YYYY-MM-DD HH:mm:ss").timestamp

	def send_rec_ratio_dist(self):
		"""
		Send Receive Ratio Distribution

		It would return the distribution of send & receive ratio over all the nodes
		(companies). The ratio is calculated by quantity of sending and receiving of 
		one node.  
		"""
		send_rec_stat = defaultdict(lambda: {
			"send": 0, "rec": 0
			})
		for link in self.links:
			send_rec_stat[link["ship_compony_id"]]["send"] += 1
			send_rec_stat[link["deliver_company_id"]]["rec"] += 1
		# for company_id, stats in send_rec_stat.items():
		# 	send_rec_stat[company_id]["send_rec_ratio"] = stats["send"] / stats["rec"] \
		# 		if stats["rec"] != 0 else None
		ratio_stats = [
			stats["send"] / stats["rec"] 
			for company_id, stats in send_rec_stat.items() 
			if stats["rec"] != 0 ]
		ratio_dist, ratio_bins = np.histogram(ratio_stats, bins=np.linspace())
		return ratio_dist, ratio_bins



class MapBasedGraph(SfExpressGraph):
	"""
	"""

	def __init__(self):
		# Initialize sf-express graph object
		SfExpressGraph.__init__(self, iterobj=None)

	def load(self, path):
		"""
		"""
		super(SfExpressGraph, self).load(path)
		# Initialize new links
		mb_links = defaultdict(lambda: {
			"source": None, "target": None, "value": 0
			})
		# Reorganize links
		for link in self.links:
			source = self.nodes[link["ship_compony_id"]]["area_city"]["city_name"]
			target = self.nodes[link["deliver_company_id"]]["area_city"]["city_name"]
			key = "%s %s" % (source, target)
			mb_links[key]["source"] = source
			mb_links[key]["target"] = target
			mb_links[key]["value"] += 1
		# Update links
		self.links = list(mb_links.values())
		# Initialize and define new nodes structure
		mb_nodes = defaultdict(lambda: {
			"city_name": None, "lat": None, "lng": None,
			"area_code": None, "area_desc": None,
			"company_num": 0, "oversea_num": 0,
			"coop_months_dist": defaultdict(lambda: 0),
			"industry_lv1_dist": defaultdict(lambda: 0),
			"industry_lv2_dist": defaultdict(lambda: 0),
			"industry_lv3_dist": defaultdict(lambda: 0)
			})
		# Reorganize nodes
		for company_id, company_info in self.nodes.items():
			mb_nodes[company_info["area_city"]["city_name"]]["city_name"] = \
				company_info["area_city"]["city_name"]
			mb_nodes[company_info["area_city"]["city_name"]]["lat"] = \
				company_info["area_city"]["lat"]
			mb_nodes[company_info["area_city"]["city_name"]]["lng"] = \
				company_info["area_city"]["lng"]
			mb_nodes[company_info["area_city"]["city_name"]]["area_code"] = \
				company_info["area_code"]
			mb_nodes[company_info["area_city"]["city_name"]]["area_desc"] = \
				company_info["area_desc"]
			mb_nodes[company_info["area_city"]["city_name"]]["company_num"] += 1
			mb_nodes[company_info["area_city"]["city_name"]]["oversea_num"] += 1 \
				if company_info["oversea"] else 0
			mb_nodes[company_info["area_city"]["city_name"]]["coop_months_dist"][company_info["coop_months"]] += 1
			mb_nodes[company_info["area_city"]["city_name"]]["industry_lv1_dist"][company_info["industry_lv1"]] += 1
			mb_nodes[company_info["area_city"]["city_name"]]["industry_lv2_dist"][company_info["industry_lv2"]] += 1
			mb_nodes[company_info["area_city"]["city_name"]]["industry_lv3_dist"][company_info["industry_lv3"]] += 1
		# Update nodes
		self.nodes = mb_nodes



class ForceDirectedGraph(SfExpressGraph):
	"""
	"""

	def __init__(self):
		# Initialize sf-express graph object
		SfExpressGraph.__init__(self, iterobj=None)

	def load(self, path):
		"""
		"""
		super(SfExpressGraph, self).load(path)
		# Initialize new links
		mb_links = defaultdict(lambda: {
			"source": None, "target": None, "value": 0
			})
		# Reorganize links
		for link in self.links:
			source = self.nodes[link["ship_compony_id"]]["industry_lv3"]
			target = self.nodes[link["deliver_company_id"]]["industry_lv3"]
			key = "%s %s" % (source, target)
			mb_links[key]["source"] = source
			mb_links[key]["target"] = target
			mb_links[key]["value"]  += 1
		# Update links
		self.links = list(mb_links.values())
		# Initialize and define new nodes structure
		mb_nodes = defaultdict(lambda: {
			"industry_lv1": defaultdict(lambda: 0),
			"industry_lv2": defaultdict(lambda: 0),
			"industry_lv3": defaultdict(lambda: 0), # Primary key
			"coop_months_dist": defaultdict(lambda: 0),
			"city_dist": defaultdict(lambda: 0),
			"company_num": 0, "oversea_num": 0
			})
		# Reorganize nodes
		for company_id, company_info in self.nodes.items():
			mb_nodes[company_info["industry_lv3"]]["industry_lv1"] = company_info["industry_lv1"]
			mb_nodes[company_info["industry_lv3"]]["industry_lv2"] = company_info["industry_lv2"]
			mb_nodes[company_info["industry_lv3"]]["industry_lv3"] = company_info["industry_lv3"]
			mb_nodes[company_info["industry_lv3"]]["company_num"] += 1
			mb_nodes[company_info["industry_lv3"]]["oversea_num"] += 1 \
				if company_info["oversea"] else 0
			mb_nodes[company_info["industry_lv3"]]["coop_months_dist"][company_info["coop_months"]] += 1
			mb_nodes[company_info["industry_lv3"]]["city_dist"][company_info["area_city"]["city_name"]] += 1
		# Update nodes
		self.nodes = mb_nodes


if __name__ == "__main__":

	# g = SfExpressGraph(iterobj=sys.stdin)
	# g.save("/Users/woodie/Desktop/sfexpress/basic_graph")
	# g.preview()

	g = SfExpressGraph()
	g.load("/Users/woodie/Desktop/sfexpress/basic_graph")
	print("Numbers of nodes %d, number of links %d." % g.shape(), file=sys.stderr)
	# print(json.dumps(g.send_rec_ratio_dist()))
	dist, bins = g.send_rec_ratio_dist()
	print(dist)
	print(bins)
	# g.preview()

	# g = MapBasedGraph()
	# g.load("/Users/woodie/Desktop/sfexpress/basic_graph")
	# print("Numbers of nodes %d, number of links %d." % g.shape())
	# g.save("/Users/woodie/Desktop/sfexpress/map_based_graph")
	# g.preview()

	# g = ForceDirectedGraph()
	# g.load("/Users/woodie/Desktop/sfexpress/basic_graph")
	# print("Numbers of nodes %d, number of links %d." % g.shape())
	# g.save("/Users/woodie/Desktop/sfexpress/force_directed_graph")
	# g.preview()


