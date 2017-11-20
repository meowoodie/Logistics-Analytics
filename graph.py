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
from collections import defaultdict
from pprint import pprint



class Graph():
	'''
	Graph

	It is an abstract class for generating, manipulating, and visualizing graphs
	data structure.
	'''

	def __init__(self, node_terms, link_terms, iterobj=None):

		self.node_terms = node_terms
		self.link_terms = link_terms
		# Build the graph if the iterobj was provided
		if iterobj != None:
			self.iterobj = iterobj
			self.build()

	def preprocess(self, record):
		'''
		Preprocess

		An abstract method for extracting nodes and links information and 
		reformat them into json objects. 

		In this function self.nodes, self.links, and their definitions self.node_terms,
		self.link_terms are available for using.
		'''
		pass

	def postprocess(self):
		'''
		Postprocess

		An abstract method for updating nodes and links information after 
		preprocessing all the records in the raw data. This funciton is usually 
		used to calculate some attributes that requires all the information of the
		graph. 
		'''
		pass


	def build(self):
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
			# Split raw data line into record terms
			record = record_str.strip('\n').split('\t')
			# Preprocess each record of the iterated object, and 
			# update nodes and links
			self.preprocess(record)
			# DO NOT CATCH ANY EXCEPTION HERE
			# LET BUGS OR DATA INCONSISTENCY SHOW THEMSELVES BY THEIR OWN
			# Monitor the preprocess
			if line_no % 100000 == 0:
				print('processed %s records ...' % line_no)
			line_no += 1
		# Update nodes and links after preprocessing for each of the records
		self.postprocess()

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
				# Check if the definitions of nodes and links are compatible
				# with the inputed parameters
				defs_nodes = set(list(self.nodes.values())[0].keys())
				defs_links = set(self.links[0].keys())
				if defs_nodes != set(self.node_terms) or \
				   defs_links != set(self.link_terms):
					raise Exception('There is an inconsistency between the definitions of \
						loading graph and specified definitions.')
		else:
			raise Exception('The specified path [%s] is not existed.' % path)

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
		else:
			raise Exception('The specified path [%s] is not existed.' % path)

	def shape(self):
		'''
		Return the size of the graph, including the amount of links and the numbers of
		nodes of the graph.
		'''
		return (len(self.nodes), len(self.links))

	def preview(self):
		'''
		Get a preview of the nodes and links
		'''
		pprint(dict(list(self.nodes.items())[0:2]))
		pprint(self.links[0:5])



class SfExpressGraph(Graph):
	'''
	SF-Express Graph

	Subclass of Graph for converting SF-Express logistics records into graph 
	data structure. It mainly override the preprocess method in order to adapt
	its own business logic. 
	'''

	def __init__(self, iterobj=None):
		# Definition of nodes
		company_info_terms = [
			'company_id', 'business', 'oversea','industry_lv1', 'industry_lv2', \
			'industry_lv3', 'area_code', 'area_desc', 'area_city', 'coop_months' ]
		# Definition of links
		transac_info_terms = [
			'transac_id', 'ship_time', 'deliver_time', 'ship_compony_id', 'deliver_company_id']
		# Initialize graph object
		Graph.__init__(self, iterobj=iterobj,
			node_terms=company_info_terms, link_terms=transac_info_terms)

	def preprocess(self, record):
		'''
		Override preprocess of class graph. This function defines the companies as
		nodes and shipment transactions as links, and extracts the information from 
		raw records
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

	def postprocess(self):
		'''
		Override postprocess of class graph. Reformat some data fields of nodes 
		and links, majorly converting Chinese characters into other formats like 
		booleans, numbers or english words. 
		'''
		# Convert cityname into its latitude and longitude, and reorganize them into 
		# a dictionary.
		def getGeoByCity(cityname):
			# Remove slash from the city name
			cityname = cityname.strip().split('/')[0]
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

class MapBasedGraph(SfExpressGraph):
	'''
	'''
	def __init__(self):
		# Initialize sf-express graph object
		SfExpressGraph.__init__(self, iterobj=None)
		# Load SF-Express Graph from file

	def build(self, path):
		'''
		'''
		super(SfExpressGraph, self).load(path)
		# Initialize new links
		mp_links = defaultdict(lambda: {
			'source': None, 'target': None, 'value': 0
			})
		# Reorganize links
		for link in self.links:
			source = self.nodes[link['ship_compony_id']]['area_city']['city_name']
			target = self.nodes[link['deliver_company_id']]['area_city']['city_name']
			key = '%s %s' % (source, target)
			mp_links[key]['source'] = source
			mp_links[key]['target'] = target
			mp_links[key]['value'] += 1
		# Update links
		self.links = list(mp_links.values())
		# Initialize and define new nodes structure
		mp_nodes = defaultdict(lambda: {
			'city_name': None, 'lat': None, 'lng': None,
			'area_code': None, 'area_desc': None,
			'company_num': 0, 'oversea_num': 0,
			'coop_months_dist': defaultdict(lambda: 0),
			'industry_lv1_dist': defaultdict(lambda: 0),
			'industry_lv2_dist': defaultdict(lambda: 0),
			'industry_lv3_dist': defaultdict(lambda: 0)
			})
		# Reorganize nodes
		for company_id, company_info in self.nodes.items():
			mp_nodes[company_info['area_city']['city_name']]['city_name'] = \
				company_info['area_city']['city_name']
			mp_nodes[company_info['area_city']['city_name']]['lat'] = \
				company_info['area_city']['lat']
			mp_nodes[company_info['area_city']['city_name']]['lng'] = \
				company_info['area_city']['lng']
			mp_nodes[company_info['area_city']['city_name']]['area_code'] = \
				company_info['area_code']
			mp_nodes[company_info['area_city']['city_name']]['area_desc'] = \
				company_info['area_desc']
			mp_nodes[company_info['area_city']['city_name']]['company_num'] += 1
			mp_nodes[company_info['area_city']['city_name']]['oversea_num'] += 1 \
				if company_info['oversea'] else 0
			mp_nodes[company_info['area_city']['city_name']]['coop_months_dist'][company_info['coop_months']] += 1
			mp_nodes[company_info['area_city']['city_name']]['industry_lv1_dist'][company_info['industry_lv1']] += 1
			mp_nodes[company_info['area_city']['city_name']]['industry_lv2_dist'][company_info['industry_lv2']] += 1
			mp_nodes[company_info['area_city']['city_name']]['industry_lv3_dist'][company_info['industry_lv3']] += 1
		# Update nodes
		self.nodes = mp_nodes


if __name__ == '__main__':

	# g = SfExpressGraph(iterobj=sys.stdin)
	# g.save('/Users/woodie/Desktop/sfexpress/basic_graph')

	# g = SfExpressGraph()
	# g.load('/Users/woodie/Desktop/sfexpress/basic_graph')
	# print('Numbers of nodes %d, number of links %d.' % g.shape())

	g = MapBasedGraph()
	g.build('/Users/woodie/Desktop/sfexpress/basic_graph')
	print('Numbers of nodes %d, number of links %d.' % g.shape())
	g.save('/Users/woodie/Desktop/sfexpress/map_based_graph')
	g.preview()

