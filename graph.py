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
		Load existed json file of graph
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
		Save the graph into json files
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
