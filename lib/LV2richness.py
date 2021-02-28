import numpy as np
from scipy import stats


def LV2richness(At, threshold, transposed=True, f_output=None):
	"""
	Creates and saves CSV table containing: Author,(Birth+Death+20)/2,log10(L),log10(V),V/L,I_G,I_H,R,S,<F>.
	The following files must exist:
	* author_year.csv
	* LV_authors_... for the selected At and threshold
	* zipf_authors/zipf_... for the selected At and threshold
	"""
	# INPUT PARAMETERS
	TYPE = "raw"
	if transposed: TYPE = "transposed"
	if f_output is None: 
		f_output = "dat/table_richness_{0}_{1:0.2f}_{2:0.4f}".format(TYPE, At, threshold).replace(".", "-") + ".csv"
	input_LVauthors = "dat/LV_authors_{0}_{1:0.2f}_{2:0.4f}".format(TYPE, At, threshold).replace(".", "-") + ".txt"
	input_Zipfauthors = "dat/zipf_authors/zipf_AUTHOR_{0}_{1:0.2f}_{2:0.4f}".format(TYPE, At, threshold).replace(".", "-") + ".txt"

	# LOAD YEAR
	f = open("dat/author_year.csv", "r")
	author2years = f.read()
	f.close()
	author2years = [i.split(",") for i in author2years.split("\n")[1:-1]]
	author2years = {author2years[i][0]:[int(author2years[i][1]), int(author2years[i][2])] for i in range(len(author2years))} # dict = author : [year_1, year_2]
	authors = list(author2years.keys())

	# LOAD L,V
	f = open(input_LVauthors, "r")
	LV = f.read()
	f.close()
	LV = [i.split(" ") for i in LV.split("\n")[:-1]] 
	LV = {i[0]:[int(i[1]), int(i[2])] for i in LV} # dic = author : [L, V]

	# CALCULATE ENTROPY AND ONES
	S = {a:None for a in authors}
	F = {a:None for a in authors}
	for author in S.keys():
		f = open(input_Zipfauthors.replace("_AUTHOR_", "_{}_".format(author)), "r")
		zipf = f.read()
		f.close()

		cdw = [i.split(" ")[0] for i in zipf.split("\n")[:-1]]
		zipf = [int(i.split(" ")[1]) for i in zipf.split("\n")[:-1]]
		total = sum(zipf)
		prob = np.array([i/total for i in zipf])

		S[author] = -np.sum( prob*np.log2(prob) )
		F[author] = np.average([sum([int(j) for j in list(i)]) for i in cdw])

	# INDEXS AND RICHNESS
	# V/L
	I_VL = {a:V/L for a,(L,V) in LV.items()}
	# GUIRAUD
	I_G = {a:V/np.sqrt(L) for a,(L,V) in LV.items()}
	# HERDAN
	I_H = {a:np.log10(V)/np.log10(L) for a,(L,V) in LV.items()}
	# HEAP
	L, V = [i[0] for i in LV.values()], [i[1] for i in LV.values()]
	b, a, r, _, _ = stats.linregress(np.log10(L), np.log10(V)) # slope, intercept, r_value, p_value, std_err 
	R = ( np.log10(V)-(a+b*np.log10(L)) ) / ( np.std(np.log10(V))*np.sqrt(1 - r**2) )
	R = {authors[i]:R[i] for i in range(len(R))}

	# SAVE DATA IN TABLE
	f = open(f_output, "w")
	f.write("Author,(Birth+Death+20)/2,log10(L),log10(V),V/L,I_G,I_H,R,S,<F>\n")
	for a in authors:
		f.write(",".join([  a, str((author2years[a][0] + author2years[a][1] + 20)/2),
							str(np.log10(LV[a][0])), str(np.log10(LV[a][1])),
							str(I_VL[a]), str(I_G[a]), str(I_H[a]), str(R[a]),
							str(S[a]), str(F[a])]) + "\n")
	f.close()

	return

