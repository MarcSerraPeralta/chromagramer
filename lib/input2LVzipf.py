import numpy as np
import sys, shutil, os


##################################################################

# FROM INPUT CALCULATE L, V AND ZIPF

def input2LVzipf(INDIR, path, fname, OUTDIR, ARGS, intranet):
	"""
	Returns intranet with the name,L,V of the continuous chromagram given by INDIR, path and fname. 
	INDIR = folder containing all the files with containing the continuous chromagrams to analyse
	ARGS = [Atmin, At, threshold, TYPE]
	OUTDIR = folder to temporarly store Zipf of each piece

	Observations:
	* Atmin = chroma duration of the input chromagrams
	* At = chroma duration to analyse
	* TYPE = "transposed" or "raw" (to analyse chromas transposed or not transposed)
	* threshold's units = fraction of the chroma duration (At)
	
	When used in 'main.dataset' function:
	- PREFUNCT = 'pre_input2LVzipf'
	- POSTFUNCT = 'post_input2LVzipf'
	"""
	# INPUT PARAMETERS
	Atmin = ARGS[0]
	At = ARGS[1]
	threshold = ARGS[2]
	TYPE = ARGS[3]
	threshold = threshold*Atmin/At # average is done (instead of the sum) for each group of chromas

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
	# average
	for i in range(N):
		newchromagram += chromagram[i::N]
	newchromagram /= N

	chromagram = newchromagram
	del newchromagram

	# DISCRETIZE CHROMAS
	chromagram = np.where(chromagram <= threshold, 0, 1) 

	# DELETE SILENCE IN THE BEGINNING
	while chromagram[0].sum() == 0:
		chromagram = np.delete(chromagram, 0, 0) 
		if len(chromagram) == 0:
			return intranet

	# DELETE SILENCE IN THE END
	while chromagram[-1].sum() == 0:
		chromagram = np.delete(chromagram, -1, 0) 
		if len(chromagram) == 0:
			return intranet

	# TRANPOSITION (if needed)
	if TYPE == "transposed":
		chromagram = transpose(chromagram)

	# DETERMINE L,V 
	# GET ZIPF
	unique, counts = np.unique(chromagram, return_counts=True, axis=0) 
	keys = unique.tolist()
	dic = [[counts[i]] + keys[i] for i in range(len(counts))] # dic = [count, cdw]
	dic.sort(reverse=True) # sort using counts
	# GET LV
	L, V = len(chromagram), len(unique)

	# SAVE ZIPF
	f = open(OUTDIR + "/" + path + fname.replace(".txt", "_{}.txt".format(TYPE)), "w")
	for i in range(0, len(keys)): 
		f.write("".join([str(int(j)) for j in dic[i][1:]]) + " " + str(dic[i][0]) + "\n")
	f.close()

	intranet += [[OUTDIR + "/" + path + fname, L, V]]

	return intranet

def pre_input2LVzipf(INDIR, FUNCTION, OUTDIR, ARGS):
	"""
	Performs checks for 'input2LVzipf'
	"""
	all_TYPES = ["raw", "transposed"]
	# check
	if ARGS[3] not in all_TYPES: 
		print("ERROR: '{}' is not a valid TYPE ({})".format(ARGS[3], ", ".join(all_TYPES)))
		sys.exit(0)

	# creates folder to save author's zipf
	if "zipf_authors" not in os.listdir(): os.mkdir("zipf_authors")

	return []

def post_input2LVzipf(INDIR, FUNCTION, OUTDIR, ARGS, intranet):
	"""
	Saves L,V of pieces and L,V,Zipf of authors and Zipf of total corpus.
	"""
	# INPUT PARAMETERS
	At, threshold, TYPE = ARGS[1], ARGS[2], ARGS[3]
	output_LVpieces = "LV_pieces_{0}_{1:0.2f}_{2:0.4f}".format(TYPE, At, threshold).replace(".", "-") + ".txt"
	output_LVauthors = "LV_authors_{0}_{1:0.2f}_{2:0.4f}".format(TYPE, At, threshold).replace(".", "-") + ".txt"
	output_Zipfauthors = "zipf_AUTHOR_{0}_{1:0.2f}_{2:0.4f}".format(TYPE, At, threshold).replace(".", "-") + ".txt"
	output_Zipfcorpus = "zipf_corpus_{0}_{1:0.2f}_{2:0.4f}".format(TYPE, At, threshold).replace(".", "-") + ".txt"

	# LOAD DATA
	LV_pieces = {} # author:[pairs of L,V for each piece]
	LV_author = {} # author:{chroma_i:counts_i of the author}
	LV_corpus = {} # chroma_i:counts_i of the total corpus

	for path, L, V in intranet:
		author = path.split("/")[1]
		print("\r" + author, end="")

		# pieces
		if author not in LV_pieces.keys(): LV_pieces[author] = []
		LV_pieces[author] += [[L,V]]

		# author
		if author not in LV_author.keys(): LV_author[author] = {}
		f = open(path.replace(".txt", "_{}.txt".format(TYPE)), "r")
		zipf = f.read()
		zipf = [[i[:12], int(i[13:])] for i in zipf.split("\n")[:-1]]
		f.close()
		for cdw, n in zipf: # fuse Zipf pieces
			if cdw in LV_author[author].keys():
				LV_author[author][cdw] += n
			else:
				LV_author[author][cdw] = n

	# corpus
	for author in LV_author.keys():
		for cdw, n in LV_author[author].items(): # fuse Zipf authors
			if cdw in LV_corpus.keys():
				LV_corpus[cdw] += n
			else:
				LV_corpus[cdw] = n

	LV_corpus = [[i[1],i[0]] for i in LV_corpus.items()] # list = [count, cdw]
	LV_corpus.sort(reverse=True) # sorts using counts

	# SAVE DATA
	f = open(output_LVpieces, "w")
	for author in LV_pieces.keys():
		for L,V in LV_pieces[author]:
			f.write(author + " {} {}\n".format(L,V))
	f.close()

	f = open(output_LVauthors, "w")
	for author in LV_author.keys():
		zipf = LV_author[author]
		V = len(zipf.keys())
		L = sum(zipf.values())
		f.write(author + " {} {}\n".format(L,V))
	f.close()

	for author in LV_author.keys():
		zipf = [[i[1],i[0]] for i in LV_author[author].items()]
		zipf.sort(reverse=True) # sorts using counts
		f = open("zipf_authors/" + output_Zipfauthors.replace("_AUTHOR_", "_{}_".format(author)), "w")
		for n, cdw in zipf:
			f.write("{} {}\n".format(cdw,n))
		f.close()

	f = open(output_Zipfcorpus, "w")
	for n, cdw in LV_corpus:
		f.write("{} {}\n".format(cdw,n))
	f.close()

	# DELETE TEMPORAL ZIPF OF PIECES
	shutil.rmtree(OUTDIR)

	print("")
	# if intranet = [], postfunct does not write a report  
	return []

##################################################################

# DETERMINE KEYS AND TRANSPOSITION

def transpose(cdw):
	"""
	Returns tranposed numpy chromagram 
	"""
	# GET KEYS = [time, key]
	key = get_keys(cdw)
	keys = [[0, key], [len(cdw), None]] # time, key

	# TRANSPOSE
	newcdw = np.empty((0,12))
	for i in range(len(keys)-1):
		ti = keys[i][0]
		tf = keys[i+1][0]
		k = keys[i][1]
		if k < 15: # Major
			transp = np.concatenate((cdw[ti:tf,k:],cdw[ti:tf,:k]), axis=-1) # transposition
		else: 
			k -= 29 # to A min
			transp = np.concatenate((cdw[ti:tf,k:],cdw[ti:tf,:k]), axis=-1) # transposition
		newcdw = np.concatenate((newcdw, transp))

	return newcdw

def get_keys(cdw):
	"""
	Returns global key of a numpy chromagram. 
	Keys nomeclature:
	* Major: C= 0, C#= 1, ...
	* Minor: C=20, C#=21, ...
	"""
	# CORRELATION
	cdwave = np.zeros(12)
	for i in range(12):
		cdwave[i] = cdw[:,i].sum()
	cdwave = cdwave/cdwave.sum() # normalitzation, not needed for correlation
	corr = np.zeros(32)
	# correlation values from paper: 
	# D. Temperley. What’s key for key? The Krumhansl-Schmuckler key-finding algorithm reconsidered. Music Perception, 17(1):65–100, 1999.
	major = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
	minor = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
	
	# MAJOR
	for i in range(12):
		corr[i] = np.corrcoef([np.roll(cdwave, -i), major])[1,0] # selects coefficient from the correlation matrix
	# MINOR
	for i in range(12):
		corr[i+20] = np.corrcoef([np.roll(cdwave, -i), minor])[1,0] # selects coefficient from the correlation matrix

	# KEY
	key = int(np.argmax(corr))

	return key