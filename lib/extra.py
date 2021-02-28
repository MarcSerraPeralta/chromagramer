import numpy as np
import matplotlib.pyplot as plt
import sys, os
from scipy import stats

from . import input2LVzipf


########################################################################

# GET L AND V TOTAL

def get_Ltotal(name, PRINT=True):
	"""
	Returns (and prints) L_total of a Zipf or LV file in 'dat'.
	"""
	f = open("dat/" + name, "r")
	data = f.read()
	f.close()

	L_total = 0
	for line in data.split("\n")[:-1]:
		# Zipf file (cdw_i, n_i)
		if len(line.split(" ")) == 2: 
			_, ni = line.split(" ")
			L_total += int(ni)
		# LV file (author_i, L_i, V_i)
		if len(line.split(" ")) == 3: 
			_, L, V = line.split(" ")
			L_total += int(L)

	if PRINT: print("L_total ({}): {}".format(name, L_total))

	return L_total

def get_Vtotal(name, PRINT=True):
	"""
	Returns (and prints) V_total of a Zipf or LV file in 'dat'.
	"""
	f = open("dat/" + name, "r")
	data = f.read()
	f.close()

	V_total = len(data.split("\n")[:-1])

	if PRINT: print("V_total ({}): {}".format(name, V_total))

	return V_total

########################################################################

# HISTOGRAM OF KEYS

def get_hist_keys(INDIR, path, fname, OUTDIR, ARGS, intranet):
	"""
	Returns intranet with the key of the continuous chromagram given by INDIR, path and fname. 
	INDIR = folder containing all the files with containing the continuous chromagrams to analyse
	ARGS = [Atmin, At, threshold]
	
	When used in 'main.dataset' function:
	- POSTFUNCT = 'post_get_hist_keys'
	- no need to determine OUTDIR or PREFUNCT
	"""
	Atmin = ARGS[0]
	At = ARGS[1]
	threshold = ARGS[2]

	# GET CONTINUOUS CHROMAGRAM
	file = open(INDIR + "/" + path + fname, "r")
	key_metadata = file.readline()[:-1]
	key_time_signature = file.readline()[:-1]

	chromagram = []
	for line in file:
		chromagram += [[float(i) for i in line[:-1].split(" ")]]
	chromagram = np.array(chromagram)

	file.close()
	
	# SUM CHROMAS TO GET DESIRED At (FROM Atmin)
	N  = int(At/Atmin)
	if (len(chromagram) % N) != 0: # adds extra zeros at the end for length to be multiple of N
		chromagram = np.append(chromagram, np.zeros((N - (len(chromagram) % N),12)), axis=0)
	newchromagram = np.zeros((int(len(chromagram)/N), 12))
	for i in range(N):
		newchromagram += chromagram[i::N]

	chromagram = newchromagram
	del newchromagram

	# DISCRETIZE CHROMAS
	chromagram = np.where(chromagram < threshold, 0, 1) 

	# GET KEYS
	key = input2LVzipf.get_keys(chromagram)

	intranet += [key]

	return intranet

def post_get_hist_keys(INDIR, FUNCTION, OUTDIR, ARGS, intranet):
	"""
	Saves keys in intranet to 'histogram_keys.txt'.
	For plotting use 'plot_hist_keys' function. 
	"""
	f = open("histogram_keys.txt", "w")
	f.write(" ".join([str(i) for i in intranet]))
	f.close()

	# if intranet = [], postfunct does not write a report   
	return []

def plot_hist_keys(f_input="dat/histogram_keys.txt", f_output="dat/histogram_keys.pdf"):
	"""
	Plots a histogram with the keys in 'f_input' and saves it as 'f_output'.
	Default values selected to use 'post_get_hist_keys' output.
	"""
	f = open(f_input, "r")
	data = [int(i) for i in f.read().split(" ")]
	f.close()

	fig = plt.figure(figsize=(5,4))
	ax = fig.add_subplot(111)

	unique, counts = np.unique(data, return_counts=True) 
	ax.bar(unique, counts, align='center')	

	ax.set_xlabel("keytones", size=12)
	ax.set_ylabel("\\# pieces", size=12)
	fig.tight_layout()
	fig.savefig(f_output, format="pdf")	

	return

########################################################################

# LV TABLE (Author,Birth,Death,L,V,# pieces)

def LV_table(At, threshold, transposed=True, f_output=None):
	"""
	Creates and saves CSV table containing: Author,Birth,Death,L,V,# pieces.
	The following files must exist:
	* author_year.csv
	* LV_authors_... for the selected At and threshold
	* LV_pieces_... for the selected At and threshold
	"""
	# CHECKS
		# input parameters
	TYPE = "raw"
	if transposed: TYPE = "transposed"
	if f_output is None: 
		f_output = "dat/table_LV_{0}_{1:0.2f}_{2:0.4f}".format(TYPE, At, threshold).replace(".", "-") + ".csv"
	input_LVauthors = "dat/LV_authors_{0}_{1:0.2f}_{2:0.4f}".format(TYPE, At, threshold).replace(".", "-") + ".txt"
	input_LVpieces = "dat/LV_pieces_{0}_{1:0.2f}_{2:0.4f}".format(TYPE, At, threshold).replace(".", "-") + ".txt"
		# files exist
	list_files = os.listdir("dat")
	if "author_year.csv" not in list_files: 
		print("ERROR: 'author_year.csv' not found in 'dat' (there is a copy in the github repository)")
		sys.exit(0)
	if input_LVauthors.split("/")[-1] not in list_files: 
		print("ERROR: '{}' not found (execute 'input2LVzipf' function)".format(input_LVauthors))
		sys.exit(0)
	if input_LVpieces.split("/")[-1] not in list_files: 
		print("ERROR: '{}' not found (execute 'input2LVzipf' function)".format(input_LVpieces))
		sys.exit(0)

	# LOAD AUTHOR, BIRTH, DEATH
	f = open("dat/author_year.csv", "r")
	data = f.read()
	f.close()
	data = [i.split(",") for i in data.split("\n")[1:-1]] # skips first line with headers
	data = {data[i][0]:[int(data[i][1]), int(data[i][2])] for i in range(len(data))} # dict = author : [year_1, year_2]

	# LOAD L, V
	f = open(input_LVauthors, "r")
	txt = f.read()
	f.close()
	for line in txt.split("\n")[:-1]:
		author, L, V = line.split(" ") 
		data[author] += [int(L), int(V)] # dict = author : [year_1, year_2, L, V]

	# LOAD NUMBER PIECES
	n_pieces = {i:0 for i in data.keys()}
	f = open(input_LVpieces, "r")
	txt = f.read()
	f.close()
	for line in txt.split("\n")[:-1]:
		author = line[:-1].split(" ")[0] # ends with \n
		n_pieces[author] += 1 

	for author in data.keys():
		data[author] += [n_pieces[author]] # dict = author : [year_1, year_2, L, V, #pieces]

	# SAVE TABLE
	f = open(f_output, "w")
	f.write("Author,Birth,Death,L,V,# pieces\n")
	for author in data.keys():
		f.write(",".join([author] + [str(i) for i in data[author]]) + "\n")
	f.close()

	return

########################################################################

# logV vs logL REGRESSION

def LV_regression(names, PRINT=True):
	"""
	Returns (and prints) linear regressions parameters of logV vs logL. 
	names = [list of files LV_authors_... and/or LV_pieces_... inside 'dat/']
	"""
	for name in names:
		f = open("dat/" + name, "r")
		data = f.read()
		f.close()

		L = np.array([int(i.split(" ")[1]) for i in data.split("\n")[:-1]]) 
		V = np.array([int(i.split(" ")[2]) for i in data.split("\n")[:-1]]) 

		slope, intercept, r_value, p_value, std_err = stats.linregress(np.log10(L), np.log10(V))
		sigma_c = np.std(np.log10(V))*np.sqrt(1 - r_value**2)

		if PRINT:
			print("{}\n=====\nslope: {}\nintercept: {}\nr_value: {}\nstd_err: {}\nsigma_c: {}\n".format(name, slope, intercept, r_value, std_err, sigma_c))

	return slope, intercept, r_value, sigma_c

########################################################################

# TRANSFORM DISCRETE CHROMA TO CHORD NOTES

def cdw2note(cdw):
	"""
	Returns the notes of a discrete chroma. 
	cdw = str or list of 12 elements. 

	example "010010000100" or [0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0] ==> ['C#', 'E', 'A'] 
	"""
	num2note = {0:"C", 1:"C#", 2:"D", 3:"D#", 4:"E", 5:"F", 6:"F#", 
				7:"G", 8:"G#", 9:"A", 10:"A#", 11:"B"}

	# converts str to list
	if type(cdw)==str: 
		cdw = [int(i) for i in list(cdw)]
	# check
	if len(cdw) != 12: 
		return "ERROR: input is not a chroma (len != 12)"
	# calculation
	notes = [] 
	for i in range(12):
		if cdw[i] != 0:
			notes += [num2note[i]]

	return notes

def zipf2note(zipf):
	"""
	Returns the notes of several chromas from a Zipf file format. 
	zipf = str of format 'cdw int' where 'cdw'=discrete chroma and 'int'=any integer.

	example "010010000100 123" ==> ['C#', 'E', 'A'] 
	"""
	for line in zipf.split("\n"):
		print(" ".join(cdw2note(line[:12])))

	return 

########################################################################