#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import time
import shlex, subprocess
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
#							   Bwise:
#				 High order De Bruijn graph assembler
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
		print("[ERROR] BWISE is not compatible with Windows.")
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


# check if files written by BWISE are present
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
  print("Try `Bwise --help` for more information")
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
#									Correction fonction using Bloocoo
# ############################################################################

def correctionReads(BWISE_MAIN, BWISE_INSTDIR, paired_readfiles, single_readfiles, toolsArgs, fileCase, nb_correction_steps, OUT_DIR, nb_cores, OUT_LOG_FILES):
	try:
		print("\n" + getTimestamp() + "--> Starting Read Correction with Bloocoo...")
		slowParameter = " -slow "
		kmerSizeCorrection = ["31", "63", "95", "127"]
		bloocooversion = ["32", "64", "128", "128"]
		os.chdir(OUT_LOG_FILES)
		logBloocoo = "logBloocoo"
		logBloocooToWrite = open(logBloocoo, 'w')
		os.chdir(BWISE_MAIN)
		os.chdir(OUT_DIR)
		indiceCorrection = 0
		for indiceCorrection in range(min(nb_correction_steps, len(kmerSizeCorrection))):
			#~ logHistoCorr = "histocorr" + str(kmerSizeCorrection[indiceCorrection])
			#~ logHistoCorrToWrite = open(logHistoCorr, 'w')
			# Bloocoo
			cmd=BWISE_INSTDIR + "/Bloocoo" + bloocooversion[indiceCorrection] + " -file " + toolsArgs['bloocoo'][fileCase] + slowParameter + "-kmer-size " + kmerSizeCorrection[indiceCorrection] + " -nbits-bloom 24  -out reads_corrected" + str(indiceCorrection + 1) + ".fa -nb-cores " + str(nb_cores)
			print("\tCorrection step " + str(indiceCorrection + 1), flush=True)
			printCommand( "\t\t"+cmd)
			p = subprocessLauncher(cmd, logBloocooToWrite, logBloocooToWrite)
			# Deal with files after Bloocoo

			#TODO=put back the histogram creation
			# cmd=BWISE_INSTDIR + "/h5dump -y -d histogram_"+kmerSizeCorrection[indiceCorrection]+" reads_corrected" + str(indiceCorrection + 1) + ".fa.h5"
			# print("\t\t"+cmd)
			# p = subprocessLauncher(cmd, logHistoCorrToWrite, logHistoCorrToWrite)
			checkWrittenFiles(OUT_DIR + "/reads_corrected" + str(indiceCorrection + 1) + ".fa.h5")
			os.remove(OUT_DIR + "/reads_corrected" + str(indiceCorrection + 1) + ".fa.h5")
			# if (indiceCorrection > 0):
			#	  cmd="rm -f " + OUT_DIR + "/reads_corrected" + str(indiceCorrection) + "* "
			#	  print("\t\t\t"+cmd)
			#	  p = subprocessLauncher(cmd, None, logHistoCorrToWrite)
			if fileCase == 3:
				cmd="mv reads_corrected" + str(indiceCorrection + 1) + "_0_.fasta reads_corrected" + str(indiceCorrection + 1) + "1.fa "
				printCommand("\t\t\t"+cmd)
				p = subprocessLauncher(cmd)
				p = subprocessLauncher("mv reads_corrected" + str(indiceCorrection + 1) + "_1_.fasta reads_corrected" + str(indiceCorrection + 1) + "2.fa ")
				checkWrittenFiles(OUT_DIR + "/reads_corrected" + str(indiceCorrection + 1) + "1.fa")
				checkWrittenFiles(OUT_DIR + "/reads_corrected" + str(indiceCorrection + 1) + "2.fa")
				toolsArgs['bloocoo'][fileCase] = OUT_DIR + "/reads_corrected" + str(indiceCorrection + 1) + "1.fa," + OUT_DIR + "/reads_corrected" + str(indiceCorrection + 1) + "2.fa"
			else:
				checkWrittenFiles(OUT_DIR + "/reads_corrected" + str(indiceCorrection + 1) + ".fa")
				toolsArgs['bloocoo'][fileCase] = OUT_DIR + "/reads_corrected" + str(indiceCorrection + 1) + ".fa "
			#~ logHistoCorrToWrite.close()
			#~ checkWrittenFiles(OUT_DIR + "/histocorr" + str(kmerSizeCorrection[indiceCorrection]))

		os.chdir(BWISE_MAIN)
		# links and file check
		if nb_correction_steps == 0:
			if fileCase == 3:
				# no correction : linking raw read files to reads_corrected1.fa and reads_corrected2.fa
				cmd="ln -fs " + paired_readfiles + " " + OUT_DIR + "/reads_corrected1.fa"
				printCommand("\t\t\t"+cmd)
				p = subprocessLauncher(cmd, None, subprocess.DEVNULL)
				cmd="ln -fs " + single_readfiles + " " + OUT_DIR + "/reads_corrected2.fa"
				printCommand("\t\t\t"+cmd)
				p = subprocessLauncher(cmd, None, subprocess.DEVNULL)
				checkWrittenFiles(OUT_DIR + "/reads_corrected1.fa")
				checkWrittenFiles(OUT_DIR + "/reads_corrected2.fa")
			else:
				cmd="ln -fs " + toolsArgs['bloocoo'][fileCase] + " " + OUT_DIR + "/reads_corrected.fa"
				printCommand("\t\t\t"+cmd)
				p = subprocessLauncher(cmd, None, subprocess.DEVNULL)
				checkWrittenFiles(OUT_DIR + "/reads_corrected.fa")
		else:
			if fileCase == 3:
				# linking last corrected reads files to reads_corrected1.fa and reads_corrected2.fa
				cmd="ln -fs " + OUT_DIR + "/reads_corrected" + str(indiceCorrection + 1) + "1.fa " + OUT_DIR + "/reads_corrected1.fa"
				printCommand("\t\t\t"+cmd)
				p = subprocessLauncher(cmd, None, subprocess.DEVNULL)
				cmd="ln -fs " + OUT_DIR + "/reads_corrected" + str(indiceCorrection + 1) + "2.fa " + OUT_DIR + "/reads_corrected2.fa"
				printCommand("\t\t\t"+cmd)
				p = subprocessLauncher(cmd, None, subprocess.DEVNULL)
				checkWrittenFiles(OUT_DIR + "/reads_corrected1.fa")
				checkWrittenFiles(OUT_DIR + "/reads_corrected2.fa")
			else:
				cmd="ln -fs " + toolsArgs['bloocoo'][fileCase] + " " + OUT_DIR + "/reads_corrected.fa"
				printCommand("\t\t\t"+cmd)
				p = subprocessLauncher(cmd)
				checkWrittenFiles(OUT_DIR + "/reads_corrected.fa")

		print("\n" + getTimestamp() + "--> Correction Done")
	except SystemExit:	# happens when checkWrittenFiles() returns an error
		sys.exit(1);
	except KeyboardInterrupt:
		sys.exit(1);
	except:
		print("Unexpected error during read correction:", sys.exc_info()[0])
		dieToFatalError('')




# ############################################################################
#			   graph generation with BCALM + BTRIM + BGREAT
# ############################################################################

def graphConstruction(BWISE_MAIN, BWISE_INSTDIR, OUT_DIR, fileBcalm, kmerSize, solidity, toolsArgs, nb_cores, mappingEffort, unitigCoverage, missmatchAllowed, OUT_LOG_FILES):
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
		os.chdir(BWISE_MAIN)
		os.chdir(OUT_DIR)
		indiceGraph = 1
		coreUsed = "20" if nb_cores == 0 else str(nb_cores)

		if(os.path.isfile(OUT_DIR +"/dbg" + str(kmerSize)+".fa")):
			print("\t#Graph dbg" + str(kmerSize)+".fa: Already here ! Let us use it ", flush=True)
		else:
			print("\t#Graph  dbg" + str(kmerSize)+".fa: Construction... ", flush=True)
			# BCALM
			cmd=BWISE_INSTDIR + "/bcalm -max-memory 10000 -in " + OUT_DIR + "/" + inputBcalm + " -kmer-size " + str(kmerSize) + " -abundance-min " + str(solidity) + " -out " + OUT_DIR + "/out " + " -nb-cores " + coreUsed

			printCommand( "\t\t"+cmd)
			p = subprocessLauncher(cmd, logBcalmToWrite, logBcalmToWrite)
			checkWrittenFiles(OUT_DIR + "/out.unitigs.fa")

			#  Graph Cleaning
			print("\t\t #Graph cleaning... ", flush=True)
			# BTRIM
			if(solidity == 1):
				cmd=BWISE_INSTDIR + "/btrim out.unitigs.fa "+str(kmerSize)+" "+str(2*int(kmerSize-1))+" "+coreUsed+" 8"
			else:
				cmd=BWISE_INSTDIR + "/btrim out.unitigs.fa "+str(kmerSize)+" "+str(2*int(kmerSize-1))+" "+coreUsed+" 8 "+str(unitigCoverage)
			printCommand("\t\t\t"+cmd)
			p = subprocessLauncher(cmd, logTipsToWrite, logTipsToWrite)
			checkWrittenFiles(OUT_DIR + "/tipped_out.unitigs.fa")
			#~ os.remove(OUT_DIR + "/out.unitigs.fa")
			cmd="rm out.*"
			printCommand("\t\t\t"+cmd)
			p = subprocessLauncher(cmd)
			cmd="mv tipped_out.unitigs.fa dbg" + str(kmerSize) + ".fa"
			printCommand("\t\t\t"+cmd)
			p = subprocessLauncher(cmd)
			cmd="rm out.*"
			printCommand("\t\t\t"+cmd)
			p = subprocessLauncher(cmd)

		if(os.path.isfile(OUT_DIR +"/dbg" + str(kmerSize)+".fa")):
			# Read Mapping
			print("\t#Read mapping with BGREAT... ", flush=True)
			# BGREAT
			cmd=BWISE_INSTDIR + "/bgreat -k " + str(kmerSize) + "  -u reads_corrected.fa -g dbg" + str(kmerSize) + ".fa -t " + coreUsed + " -a 31 -m "+str(missmatchAllowed)+" -c -O -e "+str(mappingEffort)
			printCommand("\t\t"+cmd)
			p = subprocessLauncher(cmd, logBgreatToWrite, logBgreatToWrite)
			checkWrittenFiles(OUT_DIR + "/paths")

		os.chdir(BWISE_MAIN)

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
	BWISE_MAIN = os.path.dirname(os.path.realpath(__file__))
	BWISE_INSTDIR =	 BWISE_MAIN + "/bin"  # todo : change using getPlatform()
	print("Binaries are in: " + BWISE_INSTDIR)

	# ========================================================================
	#						 Manage command line arguments
	# ========================================================================
	parser = argparse.ArgumentParser(description='Bwise - High order De Bruijn graph assembler ')

	# ------------------------------------------------------------------------
	#							 Define allowed options
	# ------------------------------------------------------------------------
	parser.add_argument("-u", action="store", dest="single_readfiles",		type=str,					help="input fasta read files. Several read files must be concatenated.")
	parser.add_argument('-s', action="store", dest="min_cov",				type=int,	default = 2,	help="an integer, k-mers present strictly less than this number of times in the dataset will be discarded (default 2)")
	parser.add_argument('-o', action="store", dest="out_dir",				type=str,	default=os.getcwd(),	help="path to store the results (default = current directory)")
	parser.add_argument('-k', action="store", dest="kSize",					type=int,	default = 63,	help="an integer,  k-mer size (default 63)")
	parser.add_argument('-c', action="store", dest="nb_correction",	type=int,	default = 0,	help="an integer, number of steps of read correction (default 0)")
	parser.add_argument('-t', action="store", dest="nb_cores",				type=int,	default = 0,	help="number of cores used (default max)")
	parser.add_argument('-e', action="store", dest="mapping_Effort",				type=int,	default = 100,	help="Anchors to test for mapping (default 100)")
	parser.add_argument('-C', action="store", dest="unitig_Coverage",				type=int,	default = 5,	help="unitigCoverage for first cleaning (default 5)")
	parser.add_argument('-m', action="store", dest="missmatch_allowed",				type=int,	default = 10,	help="missmatch allowed in mapping (default 2)")
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
	nb_correction_steps = options.nb_correction
	nb_cores			= options.nb_cores
	mappingEffort		= options.mapping_Effort
	unitigCoverage		= options.unitig_Coverage
	missmatchAllowed		= options.missmatch_allowed

	if nb_correction_steps > 4:
		dieToFatalError("Please use value <= 4 for correction steps.")

	# ------------------------------------------------------------------------
	#				Create output dir and log files
	# ------------------------------------------------------------------------
	OUT_DIR = options.out_dir
	try:
		if not os.path.exists(OUT_DIR):
			os.mkdir(OUT_DIR)
		else:
			printWarningMsg(OUT_DIR + " directory already exists, BWISE will use it.")

		OUT_LOG_FILES = OUT_DIR + "/logs"
		if not os.path.exists(OUT_LOG_FILES):
			os.mkdir(OUT_LOG_FILES)
		outName = OUT_DIR.split("/")[-1]
		OUT_DIR = os.path.dirname(os.path.realpath(OUT_DIR)) + "/" + outName
		parametersLog = open(OUT_DIR + "/ParametersUsed.txt", 'w');
		parametersLog.write("kSize:%s	k-mer_solidity:%s	unitig_solidity:%s	correction_steps:%s	mapping_effort:%s	missmatch_allowed:%s\n " %(kSize, min_cov, unitigCoverage,nb_correction_steps, mappingEffort,missmatchAllowed))
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
		dieToFatalError("BWISE requires at least a read file")

	bloocooArg = ""
	bgreatArg = ""
	paired = '' if paired_readfiles is None else str(paired_readfiles)
	single = '' if single_readfiles is None else str(single_readfiles)
	both = paired + "," + single
	toolsArgs = {'bloocoo':{1: paired + " " , 2:  single + " " , 3: both + " "}, 'bgreat':{1:" -x reads_corrected.fa ", 2: " -u reads_corrected.fa ", 3: " -x reads_corrected1.fa  -u reads_corrected2.fa "}}




	if single_readfiles is not None and paired_readfiles is not None:  # paired end + single end
		fileCase = 3
		bankBcalm.write(OUT_DIR + "/reads_corrected1.fa\n" + OUT_DIR + "/reads_corrected2.fa\n")
	elif single_readfiles is None:	# paired end only
		fileCase = 1
		bankBcalm.write(OUT_DIR + "/reads_corrected.fa\n")
	else:  # single end only
		fileCase = 2
		bankBcalm.write(OUT_DIR + "/reads_corrected.fa\n")
	# bankBcalm.write(OUT_DIR + "lost_unitig.fa")
	bankBcalm.close()

	# ========================================================================
	#									RUN
	# ========================================================================


	# ------------------------------------------------------------------------
	#						   Correction
	# ------------------------------------------------------------------------
	t = time.time()
	correctionReads(BWISE_MAIN, BWISE_INSTDIR, paired_readfiles, single_readfiles, toolsArgs, fileCase, nb_correction_steps, OUT_DIR, nb_cores, OUT_LOG_FILES)
	print(printTime("Pre-Correction took: ", time.time() - t))


	# ------------------------------------------------------------------------
	#						   Graph construction and cleaning
	# ------------------------------------------------------------------------
	t = time.time()
	valuesGraph = graphConstruction(BWISE_MAIN, BWISE_INSTDIR, OUT_DIR, "bankBcalm.txt", kSize, min_cov, toolsArgs, nb_cores, mappingEffort, unitigCoverage, missmatchAllowed, OUT_LOG_FILES)
	print(printTime("Correction took: ", time.time() - t))






if __name__ == '__main__':
	main()
