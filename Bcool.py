#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import time
import shlex, subprocess, glob
import struct
import shutil
import os.path
import tempfile
import argparse
import threading
import multiprocessing
# from random import randint
from operator import itemgetter
from subprocess import Popen, PIPE, STDOUT

# ***************************************************************************
#
#							   Bcool:
#				 Short reads corrector de Bruijn graph based
#
#
#
# ***************************************************************************

# ############################################################################
#									Utils functions
# ############################################################################


def printCommand(cmd,pc=True):
	if pc:
		print(cmd,flush=True)

# get the platform
def getPlatform():
	if sys.platform == "linux" or sys.platform == "linux2":
		return "linux"
	elif sys.platform == "darwin":
		return "OSX"
	else:
		print("[ERROR] BCOOL is not compatible with Windows.")
		sys.exit(1);


# get the timestamp as string
def getTimestamp():
	return "[" + time.strftime("%H:%M:%S") + " " + time.strftime("%d/%m/%Y") + "] "



# check if reads files are present
def checkReadFiles(readfiles):
	if readfiles is None:
		return True
	allFilesAreOK = True
	#~ for file in readfiles:
	if not os.path.isfile(readfiles):
		print("[ERROR] File \""+file+"\" does not exist.")
		allFilesAreOK = False
	if not allFilesAreOK:
		dieToFatalError("One or more read files do not exist.")


# check if files written by BCOOL are present
def checkWrittenFiles(files):
	allFilesAreOK = True
	if not os.path.isfile(files):
		print("[ERROR] There was a problem writing \"" + files + "\".")
		allFilesAreOK = False
	if not allFilesAreOK:
		dieToFatalError("One or more files could not be written.")



# to return if an error makes the run impossible
def dieToFatalError (msg):
  print("[FATAL ERROR] " + msg)
  print("Try `BCOOL --help` for more information")
  sys.exit(1);


# launch subprocess
def subprocessLauncher(cmd, argstdout=None, argstderr=None,	 argstdin=None):
	args = shlex.split(cmd)
	p = subprocess.Popen(args, stdin = argstdin, stdout = argstdout, stderr = argstderr).communicate()
	return p

def printTime(msg, seconds):
	m, s = divmod(seconds, 60)
	h, m = divmod(m, 60)
	return msg + " %d:%02d:%02d" % (h, m, s)


def printWarningMsg(msg):
	print("[Warning] " + msg)


# ############################################################################
#			   graph generation with BCALM + BTRIM + BGREAT
# ############################################################################

def graphConstruction(BCOOL_MAIN, BCOOL_INSTDIR, OUT_DIR, fileBcalm, kmerSize, solidity, toolsArgs, nb_cores, mappingEffort, unitigCoverage, missmatchAllowed,aSize, OUT_LOG_FILES):
	try:
		inputBcalm=fileBcalm
		print("\n" + getTimestamp() + "--> Building the graph...",flush=True)
		os.chdir(OUT_LOG_FILES)
		logBcalm = "logBcalm"
		logBcalmToWrite = open(logBcalm, 'w')
		logTips = "logTips"
		logTipsToWrite = open(logTips, 'w')
		logBgreat = "logBgreat"
		logBgreatToWrite = open(logBgreat, 'w')
		logK2000 = "logK2000"
		logK2000ToWrite = open(logK2000, 'w')
		#~ os.chdir(BCOOL_MAIN)
		os.chdir(OUT_DIR)
		indiceGraph = 1
		coreUsed = "20" if nb_cores == 0 else str(nb_cores)

		if(os.path.isfile(OUT_DIR +"/dbg" + str(kmerSize)+".fa")):
			print("\t#Graph dbg" + str(kmerSize)+".fa: Already here ! Let us use it ", flush=True)
		else:
			print("\t#Graph  dbg" + str(kmerSize)+".fa: Construction... ", flush=True)
			# BCALM
			cmd=BCOOL_INSTDIR + "/bcalm -max-memory 10000 -in " + OUT_DIR + "/" + inputBcalm + " -kmer-size " + str(kmerSize) + " -abundance-min " + str(solidity) + " -out " + OUT_DIR + "/out " + " -nb-cores " + coreUsed

			printCommand( "\t\t"+cmd)
			p = subprocessLauncher(cmd, logBcalmToWrite, logBcalmToWrite)
			checkWrittenFiles(OUT_DIR + "/out.unitigs.fa")

			#  Graph Cleaning
			print("\t\t #Graph cleaning... ", flush=True)
			# BTRIM
			if(solidity == 1):
				cmd=BCOOL_INSTDIR + "/btrim out.unitigs.fa "+str(kmerSize)+" "+str(2*int(kmerSize-1))+" "+coreUsed+" 8"
			else:
				cmd=BCOOL_INSTDIR + "/btrim out.unitigs.fa "+str(kmerSize)+" "+str(2*int(kmerSize-1))+" "+coreUsed+" 8 "+str(unitigCoverage)
			printCommand("\t\t\t"+cmd)
			p = subprocessLauncher(cmd, logTipsToWrite, logTipsToWrite)
			checkWrittenFiles(OUT_DIR + "/tipped_out.unitigs.fa")
			#~ os.remove(OUT_DIR + "/out.unitigs.fa")
			#~ cmd="rm out.*"
			#~ printCommand("\t\t\t"+cmd)
			#~ p = subprocessLauncher(cmd)
			cmd="mv tipped_out.unitigs.fa dbg" + str(kmerSize) + ".fa"
			printCommand("\t\t\t"+cmd)
			p = subprocessLauncher(cmd)
			for filename in glob.glob(OUT_DIR + "/out.*"):
				os.remove(filename)
			for filename in glob.glob(OUT_DIR + "/trashme*"):
				os.remove(filename)

		if(os.path.isfile(OUT_DIR +"/dbg" + str(kmerSize)+".fa")):
			# Read Mapping
			print("\t#Read mapping with BGREAT... ", flush=True)
			# BGREAT
			cmd=BCOOL_INSTDIR + "/bgreat -k " + str(kmerSize) + "  -u original_reads.fa -g dbg" + str(kmerSize) + ".fa -t " + coreUsed + " -a "+str(aSize)+" -m "+str(missmatchAllowed)+" -c -O -f read_corrected.fa -e "+str(mappingEffort)
			printCommand("\t\t"+cmd)
			p = subprocessLauncher(cmd, logBgreatToWrite, logBgreatToWrite)
			checkWrittenFiles(OUT_DIR + "/read_corrected.fa")

		os.chdir(BCOOL_MAIN)

		print(getTimestamp() + "--> Done!")
		return {'indiceGraph': indiceGraph, 'kmerSize': kmerSize}
	except SystemExit:	# happens when checkWrittenFiles() returns an error
		sys.exit(1);
	except KeyboardInterrupt:
		sys.exit(1);
	except:
		print("Unexpected error during graph construction:", sys.exc_info()[0])
		dieToFatalError('')



# ############################################################################
#									Main
# ############################################################################
def main():

	wholeT = time.time()
	print("\n*** This is Bcool - de Bruin graph based corrector  ***\n")
	BCOOL_MAIN = os.path.dirname(os.path.realpath(__file__))
	BCOOL_INSTDIR =	 BCOOL_MAIN + "/bin"  # todo : change using getPlatform()
	print("Binaries are in: " + BCOOL_INSTDIR)

	# ========================================================================
	#						 Manage command line arguments
	# ========================================================================
	parser = argparse.ArgumentParser(description='BCOOL - De Bruijn graph based read corrector ')

	# ------------------------------------------------------------------------
	#							 Define allowed options
	# ------------------------------------------------------------------------
	parser.add_argument("-u", action="store", dest="single_readfiles",		type=str,					help="input fasta read files. Several read files must be concatenated.")
	parser.add_argument('-s', action="store", dest="min_cov",				type=int,	default = 2,	help="an integer, k-mers present strictly less than this number of times in the dataset will be discarded (default 2)")
	parser.add_argument('-S', action="store", dest="unitig_Coverage",				type=int,	default = 5,	help="unitig Coverage for  cleaning (default 5)")
	parser.add_argument('-o', action="store", dest="out_dir",				type=str,	default=os.getcwd(),	help="path to store the results (default = current directory)")
	parser.add_argument('-k', action="store", dest="kSize",					type=int,	default = 0,	help="an integer,  k-mer size (default AUTO)")
	parser.add_argument('-a', action="store", dest="aSize",	type=int,	default = 41,	help="an integer, Size of the anchor to use (default 41)")
	parser.add_argument('-t', action="store", dest="nb_cores",				type=int,	default = 0,	help="number of cores used (default max)")
	parser.add_argument('-e', action="store", dest="mapping_Effort",				type=int,	default = 1000,	help="Anchors to test for mapping ")
	parser.add_argument('-m', action="store", dest="missmatch_allowed",				type=int,	default = 10,	help="missmatch allowed in mapping (default 10)")
	parser.add_argument('--version', action='version', version='%(prog)s 0.0.1')


	# ------------------------------------------------------------------------
	#				Parse and interpret command line arguments
	# ------------------------------------------------------------------------
	options = parser.parse_args()

	# ------------------------------------------------------------------------
	#				  Print command line
	# ------------------------------------------------------------------------
	print("The command line was: " + ' '.join(sys.argv))


	# ------------------------------------------------------------------------
	#				  Misc parameters
	# ------------------------------------------------------------------------
	kSize				= options.kSize
	min_cov				= options.min_cov
	aSize = options.aSize
	nb_cores			= options.nb_cores
	mappingEffort		= options.mapping_Effort
	unitigCoverage		= options.unitig_Coverage
	missmatchAllowed		= options.missmatch_allowed

	# ------------------------------------------------------------------------
	#				Create output dir and log files
	# ------------------------------------------------------------------------
	OUT_DIR = options.out_dir
	try:
		if not os.path.exists(OUT_DIR):
			os.mkdir(OUT_DIR)
		else:
			printWarningMsg(OUT_DIR + " directory already exists, BCOOL will use it.")

		OUT_LOG_FILES = OUT_DIR + "/logs"
		if not os.path.exists(OUT_LOG_FILES):
			os.mkdir(OUT_LOG_FILES)
		outName = OUT_DIR.split("/")[-1]
		OUT_DIR = os.path.dirname(os.path.realpath(OUT_DIR)) + "/" + outName
		parametersLog = open(OUT_DIR + "/ParametersUsed.txt", 'w');
		parametersLog.write("kSize:%s	k-mer_solidity:%s	unitig_solidity:%s	aSize:%s	mapping_effort:%s	missmatch_allowed:%s\n " %(kSize, min_cov, unitigCoverage,aSize, mappingEffort,missmatchAllowed))
		parametersLog.close()

		print("Results will be stored in: ", OUT_DIR)
	except:
		print("Could not write in out directory :", sys.exc_info()[0])
		dieToFatalError('')

	# ------------------------------------------------------------------------
	#				  Parse input read options
	# ------------------------------------------------------------------------
	try:
		bankBcalm = open(OUT_DIR + "/bankBcalm.txt", 'w');
	except:
		print("Could not write in out directory :", sys.exc_info()[0])

	# check if the given paired-end read files indeed exist
	paired_readfiles = None
	single_readfiles = None
	errorReadFile = 0
	paired_readfiles = None
	errorReadFile = 1

	# check if the given single-end read files indeed exist
	if options.single_readfiles:
		single_readfiles = ''.join(options.single_readfiles)
		try:
			single_readfiles = os.path.abspath(single_readfiles)
			checkReadFiles(options.single_readfiles)
			errorReadFile *= 0
		except:
			single_readfiles = None
			errorReadFile *= 1
	else:
		single_readfiles = None
		errorReadFile *= 1

	if errorReadFile:
		parser.print_usage()
		dieToFatalError("Bcool requires at least a read file")

	bloocooArg = ""
	bgreatArg = ""
	paired = '' if paired_readfiles is None else str(paired_readfiles)
	single = '' if single_readfiles is None else str(single_readfiles)
	both = paired + "," + single
	toolsArgs = {'bloocoo':{1: paired + " " , 2:  single + " " , 3: both + " "}, 'bgreat':{1:" -x original_reads.fa ", 2: " -u original_reads.fa ", 3: " -x reads_corrected1.fa  -u reads_corrected2.fa "}}




	if single_readfiles is not None and paired_readfiles is not None:  # paired end + single end
		fileCase = 3
		bankBcalm.write(OUT_DIR + "/reads_corrected1.fa\n" + OUT_DIR + "/reads_corrected2.fa\n")
	elif single_readfiles is None:	# paired end only
		fileCase = 1
		bankBcalm.write(OUT_DIR + "/original_reads.fa\n")
	else:  # single end only
		fileCase = 2
		bankBcalm.write(OUT_DIR + "/original_reads.fa\n")
	# bankBcalm.write(OUT_DIR + "lost_unitig.fa")
	bankBcalm.close()

	# ========================================================================
	#									RUN
	# ========================================================================


	# ------------------------------------------------------------------------
	#						   Kmer size selection
	# ------------------------------------------------------------------------
	t = time.time()
	os.chdir(OUT_DIR)
	cmd="ln -fs " + single_readfiles + " " + OUT_DIR + "/original_reads.fa"
	printCommand("\t\t\t"+cmd)
	p = subprocessLauncher(cmd)
	os.chdir(BCOOL_MAIN)

	if(kSize==0):
	#~ correctionReads(BCOOL_MAIN, BCOOL_INSTDIR, paired_readfiles, single_readfiles, toolsArgs, fileCase, nb_correction_steps, OUT_DIR, nb_cores, OUT_LOG_FILES)
		#~ os.chdir(BCOOL_MAIN)
		os.chdir(OUT_DIR)
		cmd=BCOOL_INSTDIR + "/ntcard -k 21,31,41,51,61,71,81,91,101,111,121,131,141 -t "+str(nb_cores)+" -p reads "+single_readfiles
		#~ cmd=BCOOL_INSTDIR + "/ntcard -k 21,31 -t "+str(nb_cores)+" -p reads "+single_readfiles
		printCommand("\t\t\t"+cmd)
		p = subprocessLauncher(cmd)
		cmd=BCOOL_INSTDIR + "/badvisor reads "+str(unitigCoverage)
		printCommand("\t\t\t"+cmd)
		kSize = int(subprocess.check_output(cmd, shell=True))
		if kSize<21:
			print("\nWARNING : I could not determine a good kmer size sorry :( \n")
			print("I try with k=21 anyway...\n")
			kSize=21
		for filename in glob.glob(OUT_DIR + "/*.hist"):
			os.remove(filename)
		os.chdir(BCOOL_MAIN)


	print(printTime("Kmer selected : k="+str(kSize), time.time() - t))


	# ------------------------------------------------------------------------
	#						   Graph construction and cleaning
	# ------------------------------------------------------------------------
	t = time.time()
	valuesGraph = graphConstruction(BCOOL_MAIN, BCOOL_INSTDIR, OUT_DIR, "bankBcalm.txt", kSize, min_cov, toolsArgs, nb_cores, mappingEffort, unitigCoverage, missmatchAllowed,aSize, OUT_LOG_FILES)
	print(printTime("Correction took: ", time.time() - t))






if __name__ == '__main__':
	main()
