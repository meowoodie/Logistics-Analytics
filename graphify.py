#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
The script is used to graphify (make it graphical) sf-express logistics data into 
undirected graph. The graph consists of two major properties, including nodes and 
links, which is persisted in a json format. The json graph data can be further used
in visualization, company relationship studies, and so on.
'''

import os
import sys
import json
import arrow
# import uniout
import argparse

from geopy.geocoders import Nominatim
from pprint import pprint

company_info_terms = [
	'company_id', 'business', 'oversea','industry_lv1', 'industry_lv2', \
	'industry_lv3', 'area_code', 'area_desc', 'area_city', 'coop_months' ]
transac_info_terms = [
	'transac_id', 'ship_time', 'deliver_time', 'ship_compony_id', 'deliver_company_id']



class Graph():
	'''
	Graph

	It is an abstract class for generating, manipulating, and visualizing graphs
	data structure.
	'''

	def __init__(self, node_terms, link_terms, iterobj):

		self.iterobj    = iterobj
		self.node_terms = node_terms
		self.link_terms = link_terms
		self.graphify()

	def preprocess(self, record):
		'''
		Preprocess

		An abstract method for extracting nodes and links information and 
		reformat them into json objects.
		'''

		self.nodes = {}
		self.links = []


	def graphify(self):
		'''
		Graphify

		The basic method for generating graph by the inputing iterated records.
		Generally, the function iterate each of the records and updates nodes and 
		links information by calling abstract function "preprocess", which you can 
		override it and implement customized preprocessing procedures. 
		'''

		self.nodes = {}
		self.links = []

		line_no = 0
		for record_str in self.iterobj:
			try:
				# Split raw data line into record terms
				record = record_str.strip('\n').split('\t')
				# Preprocess each record of the iterated object, and 
				# update nodes and links
				self.preprocess(record)

			# Report all possible exceptions and s the iteration
			except Exception as e:
				print(record_str)
				print(e)
				break

			# Monitor the preprocess
			if line_no % 100000 == 0:
				print('processed %s records ...' % line_no)
			line_no += 1

	def load(self, path):
		'''
		'''

		nodes_path = '%s/nodes.json' % path
		links_path = '%s/links.json' % path
		if os.path.exists(nodes_path) and os.path.exists(links_path):
			with open(nodes_path, 'r') as f_nodes, \
			     open(links_path, 'r') as f_links:
				self.nodes = json.loads(f_nodes.read())
				self.links = json.loads(f_links.read())

	def save(self, path):
		'''

		'''

		if os.path.exists(path) and os.path.isdir(path):
			nodes_str = json.dumps(self.nodes)
			links_str = json.dumps(self.links)
			with open('%s/nodes.json' % path, 'w') as f_nodes, \
			     open('%s/links.json' % path, 'w') as f_links:
				f_nodes.write(nodes_str)
				f_links.write(links_str)



class SfExpressGraph(Graph):
	'''
	'''

	def __init__(self, iterobj=sys.stdin,
			node_terms=company_info_terms, link_terms=transac_info_terms):
		Graph.__init__(self, iterobj=iterobj,
			node_terms=node_terms, link_terms=link_terms)
		self.reformatNodesLinks()

	def preprocess(self, record):
		'''
		'''

		# # Terms about company information
		company_pair = [ record[0:10], record[13:23] ]
		# Terms about transaction information
		transac_info = record[10:13] + [ record[0], record[13] ]
		# Terms about item information
		item         = [] if record[23].strip() == 'NULL' else json.loads(record[23].strip())
		# Adding link information
		self.links.append(dict(zip(self.link_terms, transac_info)))
		# Adding company information
		for company in company_pair:
			if company[0] not in self.nodes:
				self.nodes[company[0]] = dict(zip(self.node_terms, company))

	def reformatNodesLinks(self):
		'''
		Reformat some data fields of nodes and links, majorly converting Chinese 
		characters into other formats like booleans, numbers or english words. 
		'''

		# Convert cityname into its latitude and longitude, and reorganize them into 
		# a dictionary.
		def getGeoByCity(cityname):
			# Remove slash from the city name
			cityname = cityname.strip().split('/')
			try: 
			    geolocator = Nominatim()
			    location2 = geolocator.geocode(cityname)
			    lat = location2.latitude
			    lng = location2.longitude
			except:
				lat = None
				lng = None
			return { 'city_name': cityname, 'lat': lat, 'lng': lng }

		print('Getting cities\' geolocation ...')
		cities_geo = { city: getGeoByCity(city)
			for city in list(set([ node['area_city'] for node in self.nodes.values() ])) }
		pprint(cities_geo)

		print('Reformatting nodes ...')
		# Reformat nodes
		for company_id, company_info in self.nodes.items():
			company_info['oversea']   = True if company_info['oversea'] == '是' else False
			company_info['area_city'] = cities_geo[company_info['area_city']]

		print('Reformatting links ...')
		# Reformat links
		for link in self.links:
			link['ship_time']    = None if link['ship_time'] == 'NULL' \
		        else arrow.get(link['ship_time'], 'YYYY-MM-DD HH:mm:ss').timestamp
			link['deliver_time'] = None if link['deliver_time'] == 'NULL' \
				else arrow.get(link['deliver_time'], 'YYYY-MM-DD HH:mm:ss').timestamp
	
		pprint(self.nodes)
		pprint(self.links)

if __name__ == '__main__':

	g = SfExpressGraph()
	# g.graphify()
	g.save('/Users/woodie/Desktop/sfexpress/graph')
