#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Links to Nodes

 
"""

import sys
import arrow
import argparse

def main():

	# Parse the input parameters
	parser = argparse.ArgumentParser(description="Specify the indices information for link record")
	parser.add_argument("-s", "--src_id_ind", required=True, type=int, help="The query id")
	parser.add_argument("-t", "--trg_id_ind", required=True, type=int, help="Return the top n results")
	parser.add_argument("-S", "--src_info_inds", required=True, help="Return the results that have the similarities above the threshold")
	parser.add_argument("-T", "--trg_info_inds", required=True, help="The path of the configuration file")
	args = parser.parse_args()
	src_id_ind = args.src_id_ind
	trg_id_ind = args.trg_id_ind
	src_info_inds = [ int(ind) for ind in args.src_info_inds.strip().split(",") ]
	trg_info_inds = [ int(ind) for ind in args.trg_info_inds.strip().split(",") ]

	for link in iter_obj:
		link[]
		print()
		link[]

if __name__ == "__main__":
	main()

