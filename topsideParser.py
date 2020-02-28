#! python
# topsideParser.py
# Contains functions required for parsing topside logs
# of the format PSK_Log.mode932.YYMMDD.* -> toaTbl-YY-MM-DD.csv

import subprocess, os
import time
import numpy
from struct import unpack

def topsideParse( files, buoyCode): #, saveDir ):
	# topsideParse - parses binary topside files to .mat format for processing
	# input args:
	# 	files: array of log files of the format PSK_Log.mode932*
	#	buoyCode: decimal representation of binary value to choose buoys (1111 -> 15 for all 4)
	# output values:
	#	topsideData: matrix of all buoy ranges for processing
	N = len(files)
	toa = numpy.empty((1,5), float)
	for n in range(N):
		subprocess.run(["psk_log_track4.exe", "-buoy="+str(buoyCode), "toaTbl", files[n]])
		m9Data = m9Read('toaTbl.m9l')
		#BuoyID = m9Data[1,:]
		toa = numpy.append(toa,m9Data[1:len(m9Data),:], axis=0)
		#print(len(m9Data[2:len(m9Data),:]))
		#print(numpy.shape(toa))

		#toa.append(m9Data[2:len(m9Data),:])
	os.remove('toaTbl.m9l')
	toa = numpy.delete(toa,0,0)
	toa[numpy.where(toa==-1)] = numpy.nan
	topsideData = toa[toa[:,0].argsort()]
	#topsideData = toa
	return topsideData

def m9Read( filename ):
	# m9Read - reads .m9l file and converts to matrix of buoy ranges
	# input args:
	#	filename: binary file to read. should always be 'toaTbl.m9l'
	# output values:
	# 	matrix: matrix of recorded buoy ranges

	# Open filename with specified byte-order format
	#machine_format = filename[-1:] # slice off end of filename

	# Open file to begin reading
	datafile = open(filename, 'rb')

	# Read header data
	header_part1 = unpack('4i',datafile.read(16)) # cast 16 bytes -> 4 int
	if len(header_part1) != 4:
		raise Exception('	Error reading elements of file header')
	header_part2 = unpack('2d',datafile.read(16)) # cast 16 bytes -> 2 double
	if len(header_part2) != 2:
		raise Exception('	Error reading checksum from file header')
	# Assign header elements to appropriate variables
	data_format 	= header_part1[0]
	complex_flag 	= header_part1[1]
	num_rows		= header_part1[2]
	num_columns		= header_part1[3]
	total_size = num_rows * num_columns
	checksum_hdr 	= header_part2[0] + 1j*header_part2[1]

	if data_format != 8:
		datafile.close()
		raise Exception('	Unrecognized data format.')
	if num_rows <= 0:
		datafile.close()
		raise Exception('	Num_rows must be greater than 0')
	if num_columns <= 0:
		datafile.close()
		raise Exception('	Num_columns must be greater than 0')

	# Read real part of matrix from file
	arg = str(total_size)+'d'
	matrix = unpack(arg, datafile.read(total_size*8)) # Cast total_size*8 bytes -> total_size double
	if len(matrix) != num_rows*num_columns:
		datafile.close()
		raise Exception('	Error reading matrix from file, real part')

	# reshape to num_rows x num_columns matrix
	matrix = numpy.reshape(matrix,(num_rows,num_columns), order='F')
	#print(num_rows)
	#print(num_columns)

	if(complex_flag):
		matrix_imag = unpack(arg, datafile.read(total_size))
		if len(matrix_imag) != total_size:
			datafile.close()
			raise Exception('	Error reading matrix from file, imaginary part')
		matrix_imag = numpy.reshape(matrix_imag,(num_rows,num_columns), order='F')
		matrix = matrix + (1j*matrix_imag)

	datafile.close()
	return matrix

if __name__ == "__main__":
	files = ["PSK_Log.mode932.180419.083205","PSK_Log.mode932.180419.092435"]
	topsideData = topsideParse(files, 15)
	print(topsideData)

	# Retrieve test date from file name of PSK_Log.mode932.YY.MM.DD.*
	dateRaw = files[0].split(".")[2]
	dateSplit = [dateRaw[i:i+2] for i in range(0, len(dateRaw), 2)]
	date = dateSplit[0] + "-" + dateSplit[1] + "-" + dateSplit[2]
	numpy.savetxt("toaTbl-" + date +".csv",topsideData,delimiter=",")
