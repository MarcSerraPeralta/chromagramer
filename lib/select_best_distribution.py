import numpy as np

##############################

NAME_untruncated = "dat/zipf_authors_untruncated.csv"
NAME_truncated = "dat/zipf_authors_truncated.csv"
NAME_lognormal = "dat/zipf_authors_lognormal.csv"

NAME_OUTPUT = "dat/best_distribution_authors.csv"

min_diff_exponents = 0.5 # for the double Zipf, the fit is discarded if abs(beta1 - beta2) <= min_diff_exponents

index_untruncated = [0, 1, 6, 2] # indexs of the output file for name, a, n_max, beta
index_truncated = [0, 1, 2, 3] # indexs of the output file for name, a, b, beta
index_lognormal = [0, 1] # indexs of the output file for name, a

##############################

# LOAD DATA

	# UNTRUNCATED

DATA_UNTRUNCATED = {}
f = open(NAME_untruncated, "r")
data = f.read()
f.close()
for line in data.split("\n")[1:-1]: # skip header
	values = line.split(",")
	if ",-" in line:
		DATA_UNTRUNCATED[values[index_untruncated[0]]] = None
	else:
		name = values[index_untruncated[0]]
		values = [float(values[i]) for i in index_untruncated[1:]]
		DATA_UNTRUNCATED[name] = values


	# TRUNCATED

DATA_TRUNCATED = {}
f = open(NAME_truncated, "r")
data = f.read()
f.close()
for line in data.split("\n")[1:-1]: # skip header
	values = line.split(",")
	if ",-" in line:
		DATA_TRUNCATED[values[index_truncated[0]]] = None
	else:
		name = values[index_truncated[0]]
		values = [float(values[i]) for i in index_truncated[1:]]
		DATA_TRUNCATED[name] = values


	# LOGNORMAL

DATA_LOGNORMAL = {}
f = open(NAME_lognormal, "r")
data = f.read()
f.close()
for line in data.split("\n")[1:-1]: # skip header
	values = line.split(",")
	if ",-" in line:
		DATA_LOGNORMAL[values[index_lognormal[0]]] = None
	else:
		name = values[index_lognormal[0]]
		values = [float(values[i]) for i in index_lognormal[1:]]
		DATA_LOGNORMAL[name] = values

##############################

# SELECTION BEST FIT

NAMES = (set(DATA_UNTRUNCATED.keys()).union(DATA_TRUNCATED.keys())).union(DATA_LOGNORMAL.keys())
DISTRIBUTIONS = {}

for name in NAMES:

	fits = []

	# CONDITIONS
	c_PL, c_DPL, c_LOGN = False, False, False
	if name in DATA_UNTRUNCATED.keys():
		if DATA_UNTRUNCATED[name] is not None:
			fits += [[DATA_UNTRUNCATED[name][0], "simple"]] # [a, distribution]
	if name in DATA_LOGNORMAL.keys():
		if DATA_LOGNORMAL[name] is not None:
			fits += [[DATA_LOGNORMAL[name][0], "lognormal"]] # [a, distribution]
	if (name in DATA_UNTRUNCATED.keys()) and (name in DATA_TRUNCATED.keys()):
		if (DATA_UNTRUNCATED[name] is not None) and (DATA_TRUNCATED[name] is not None):
			a2, nmax, beta2 = DATA_UNTRUNCATED[name]
			a1, b, beta1 = DATA_TRUNCATED[name]
			if (a2 <= b) and (np.abs(beta1 -  beta2) >= min_diff_exponents):
				fits += [[DATA_TRUNCATED[name][0], "double"]] # [a, distribution]

	# SELECTION
	best_fit = [1E9, "none"]
	fits = sorted(fits, key=lambda x: x[0]) # sort by "a"
	for a, dist in fits:
		if a >= 32: continue
		if a == best_fit[0]: # simple = 1 parameter, lognormal = 2, power-law = 3
			if dist == "simple":
				best_fit = [a, dist]
			elif dist == "lognormal":
				if best_fit[1] != "simple":
					best_fit = [a, dist]
		if a < best_fit[0]:
			best_fit = [a, dist]

	DISTRIBUTIONS[name] = best_fit[1]

##############################

# PRINT
print("simple:", len([i for i in DISTRIBUTIONS.values() if i=="simple"]))
print("double:", len([i for i in DISTRIBUTIONS.values() if i=="double"]))
print("lognormal:", len([i for i in DISTRIBUTIONS.values() if i=="lognormal"]))
print("none:", len([i for i in DISTRIBUTIONS.values() if i=="none"]))

# SAVE
f = open(NAME_OUTPUT, "w")
for name in sorted(DISTRIBUTIONS.keys()):
	f.write("{},{}\n".format(name, DISTRIBUTIONS[name]))
f.close()
