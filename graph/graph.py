#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
The script is used to graphify (make it graphical) sf-express logistics data into 
undirected graph. The graph consists of two major properties, including nodes and 
links, which is persisted in a json format. The json graph data can be further used
in visualization, company relationship studies, and so on.
"""

import os
import sys
import json

from pprint import pprint
from collections import defaultdict


class Graph():
	"""
	Graph

	It is an abstract class for generating, manipulating, and visualizing graphs
	data structure.
	"""

	def __init__(self, node_terms=[], link_terms=[], 
		node_key=None, link_src_key=None, link_trg_key=None, iterobj=None):
		self.node_key     = node_key
		self.link_src_key = link_src_key
		self.link_trg_key = link_trg_key
		self.node_terms = node_terms
		self.link_terms = link_terms
		# Build the graph if the iterobj was provided
		if iterobj != None:
			self.iterobj = iterobj
			self.build()

	def preprocess(self, record):
		"""
		Preprocess

		An abstract method for extracting nodes and links information and 
		reformat them into json objects. 

		In this function self.nodes, self.links, and their definitions self.node_terms,
		self.link_terms are available for using.
		"""
		pass

	def postprocess(self):
		"""
		Postprocess

		An abstract method for updating nodes and links information after 
		preprocessing all the records in the raw data. This funciton is usually 
		used to calculate some attributes that requires all the information of the
		graph. 
		"""
		pass


	def build(self):
		"""
		Graphify

		The basic method for generating graph by the inputing iterated records.
		Generally, the function iterate each of the records and updates nodes and 
		links information by calling abstract function "preprocess", which you can 
		override it and implement customized preprocessing procedures. 
		"""
		self.nodes = {}
		self.links = []

		line_no = 0
		for record_str in self.iterobj:
			# Split raw data line into record terms
			record = record_str.strip("\n").split("\t")
			# Preprocess each record of the iterated object, and 
			# update nodes and links
			self.preprocess(record)
			# DO NOT CATCH ANY EXCEPTION HERE
			# LET BUGS OR DATA INCONSISTENCY SHOW THEMSELVES ON THEIR OWN
			# Monitor the preprocess
			if line_no % 100000 == 0:
				print("processed %s records ..." % line_no)
			line_no += 1
		# Update nodes and links after preprocessing for each of the records
		self.postprocess()

	def load(self, path):
		"""
		Load existed json file of graph
		"""
		nodes_path = "%s/nodes.json" % path
		links_path = "%s/links.json" % path
		if os.path.exists(nodes_path) and os.path.exists(links_path):
			with open(nodes_path, "r") as f_nodes, \
			     open(links_path, "r") as f_links:
				self.nodes = json.loads(f_nodes.read())
				self.links = json.loads(f_links.read())
				# Check if the definitions of nodes and links are compatible
				# with the inputed parameters
				defs_nodes = set(list(self.nodes.values())[0].keys())
				defs_links = set(self.links[0].keys())
				if defs_nodes != set(self.node_terms) or \
				   defs_links != set(self.link_terms):
					raise Exception("There is an inconsistency between the definitions of \
						loading graph and specified definitions.")
		else:
			raise Exception("The specified path [%s] is not existed." % path)

	def save(self, path):
		"""
		Save the graph into json files
		"""
		if os.path.exists(path) and os.path.isdir(path):
			nodes_str = json.dumps(self.nodes)
			links_str = json.dumps(self.links)
			with open("%s/nodes.json" % path, "w") as f_nodes, \
			     open("%s/links.json" % path, "w") as f_links:
				f_nodes.write(nodes_str)
				f_links.write(links_str)
		else:
			raise Exception("The specified path [%s] is not existed." % path)

	def merge_links(self):
		"""
		Merge links

		Merge all links between two arbitrary nodes, set the number of the links 
		as the value of the merged link.
		"""
		merged_links = defaultdict(lambda: {"value": 0})
		for link in self.links:
			key = "%s %s" % (link[self.link_src_key], link[self.link_trg_key])
			merged_links[key][self.link_src_key] = link[self.link_src_key]
			merged_links[key][self.link_trg_key] = link[self.link_trg_key]
			merged_links[key]["value"] += 1
		self.links = list(merged_links.values())
		self.link_terms = [self.link_src_key, self.link_trg_key, "value"]

	def simplify_nodes(self, keep_node_terms):
		"""
		"""
		simplified_nodes = defaultdict(lambda: {})
		for key, node in self.nodes.items():
			for term in keep_node_terms:
				if term in self.node_terms:
					simplified_nodes[key][term] = node[term]
		self.nodes = simplified_nodes
		self.node_terms = keep_node_terms

	def get_subgraph_by_nodes(self, nodes):
		"""
		"""
		sub_nodes = dict([ [ node, self.nodes[node] ] for node in nodes ])
		sub_links = [ link
			for link in self.links 
			if link[self.link_src_key] in sub_nodes and \
			   link[self.link_trg_key] in sub_nodes ]
		# Create a new object with the same class
		subgraph = self.__class__()
		subgraph.nodes = sub_nodes
		subgraph.links = sub_links
		subgraph.node_key = self.node_key 
		subgraph.link_src_key = self.link_src_key
		subgraph.link_trg_key = self.link_trg_key
		subgraph.node_terms = self.node_terms
		subgraph.link_terms = self.link_terms

		return subgraph
		# return sub_nodes, sub_links

	# def get_contacting_subgraph(self, node, contact_degree=1):
	# 	"""
	# 	Get Subgraph by Indicated Node

	# 	Ideally this function would return a new graph class which contains 
	# 	sub nodes and links. 
	# 	"""
	# 	sub_nodes = [
	# 		set([ node ]) # Degree 0 (The center node itself of the subgraph)
	# 		# [ ... ],      Degree i (continuously appended into this list in accordance with the contact_degree)
	# 	]
	# 	sub_links = []
	# 	# Find all the nodes that has relationship with the indicated node within specific contact degree
	# 	for degree in range(contact_degree):
	# 		# Init nodes list for degree i 
	# 		sub_nodes.append(set([]))
	# 		# Traverse all links for each of contact degrees
	# 		# Add links which have directed connections with nodes in <degree> contact-degree
	# 		for link in self.links:
	# 			if link[self.link_src_key] in sub_nodes[degree]:
	# 				sub_nodes[degree+1].add(link[self.link_trg_key])
	# 			elif link[self.link_trg_key] in sub_nodes[degree]:
	# 				sub_nodes[degree+1].add(link[self.link_src_key])
	# 	# Remove the duplicated nodes for each of the set of nodes in different contact-degree
	# 	for degree in range(contact_degree):
	# 		closer_nodes = set([])
	# 		for d in range(degree+1):
	# 			closer_nodes = set.union(closer_nodes, sub_nodes[d])
	# 		sub_nodes[degree+1] -= closer_nodes
	# 	# Flatten nodes list
	# 	sub_nodes = [j for i in sub_nodes for j in i]

	# 	return self.get_subgraph_by_nodes(sub_nodes)

	def shape(self):
		"""
		Return the size of the graph, including the amount of links and the numbers of
		nodes of the graph.
		"""
		return (len(self.nodes), len(self.links))

	def preview(self):
		"""
		Get a preview of the nodes and links
		"""
		pprint(dict(list(self.nodes.items())[0:2]))
		pprint(self.links[0:5])
