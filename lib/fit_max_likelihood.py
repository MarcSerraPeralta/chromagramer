import numpy as np
from scipy import stats
from scipy.optimize import minimize
from scipy import special
import os

# disabling warnings
import warnings
warnings.filterwarnings("ignore")

##############################

INPUT_DIR = "dat/zipf_authors" # Performs fit to all files in "INPUT_DIR" folder. See "LOAD DATA" for more information about the input files
OUTPUT_FILE = INPUT_DIR + "_DISTRIBUTION.csv" # "DISTRIBUCTION" will be changed by the fitted distribution for each case of "TODO"

TODO = ["truncated", "untruncated", "lognormal", "untruncated2"] # List of fits to perform, from "truncated", "untruncated", "lognormal", "untruncated2"

pvalue_threshold = 0.20 # accept fit if p-value >= pvalue_threshold
Nsimulaitons = 100 # number of simulations
step_partitions = 0.05 # division per logarithmic decade (10^x to 10^x+1) done while searching for "a"

optimization_precision = 1E-6 # precision for the maximum of the loglikelihood function
beta_bounds = (0.5, 7) # range for the "beta" exponent in the power laws
logn_bounds = [(-20, 20), (0, 10)] # range for "mu" and "sigma" in the lognormal
a_upperbound = 32 # maximum value of "a" to fit. If a_upperbound = None ==> a_upperbound = max(data). It may not be exactly the same value due to the step_partitions
a_lowerbound = 1 # minimum value of "a" to fit. If a_lowerbound = None ==> a_lowerbound = min(data)

##############################
##############################
##############################

DATA_VARIABLES = {} # stores the name of output variables of each fit

##############################

# TRUNCATED POWER LAW

DATA_VARIABLES["truncated"] = ["a", "b", "beta", "beta_error", "pvalue", "Nfit", "n_max"]

def cdf_TPL(x, a, beta, b):
	"""
	Cumulative function for truncated power law. 
	pdf(x) = (beta-1)/(a*(1-c^(beta-1))) * (a/x)^beta
	for a <= x <= b
	"""
	F = (1-(a/x)**(beta-1))/(1-(a/b)**(beta-1))
	return F

def loglikelihood_TPL(beta, data, a, b):
	"""
	(Minus) Loglikelihood function for truncated power law
	beta = exponent
	a, b = range of the power law (a < b)
	data = np.array of frequencies
	The minus is for the minimization (to be maximization)
	"""
	N = len(data)
	logL = N*np.log((beta - 1)/(a**(1-beta) - b**(1-beta))) - beta*np.sum(np.log(data))
	return - logL

def truncated_power_law(data, a_upperbound=a_upperbound, a_lowerbound=a_lowerbound, pvalue_threshold=pvalue_threshold, Nsimulaitons=Nsimulaitons, 
								step_partitions=step_partitions, optimization_precision=optimization_precision, beta_bounds=beta_bounds):

	# INICIALIZE VARIABLES
	if a_upperbound is None: a_upperbound = np.max(data) 
	if a_lowerbound is None: a_lowerbound = np.min(data)
	xmin = np.min(data) 
	xmax = np.max(data) 

	OUTPUT = []

	##############################

	# PARAMETERS "a" AND "beta" DETERMINATION BY MAXIMUM LIKELIHOOD METHOD

	a_previous = -1E10
	b_previous = -1E10

	for a in 10**np.arange(np.log10(a_lowerbound), np.log10(a_upperbound)+step_partitions, np.abs(step_partitions)): # logarithmic binning (from left to right)

		if np.abs(a - a_previous) < 1:
				continue

		for b in 10**np.arange(np.log10(xmax), np.log10(a), -np.abs(step_partitions)): # logarithmic binning (from right to left)

			if np.abs(b - b_previous) < 1:
				continue

			# "beta" DETERMINATION (maximum likelihood)
			data_ = data[np.where((a <= data) & (data <= b))]
			N = len(data_)
			if (N == 0) or (np.abs(a-b) < 2.1): # if they have less diference than 2, they only include 2 types of frequencies = a line
				print("\ra={:9.1f}  | b={:9.1f}  | # simulations={:4d}    | EXITED".format(a, b, i+1, pvalue), end="")
				continue # empty data to fit

			guess = beta = 1 + 1/(-np.log(a) + np.sum(np.log(data_))/N) # initial guess

			res = minimize(loglikelihood_TPL, guess, method='SLSQP', bounds=[beta_bounds], tol=optimization_precision, args=(data_,a,b)) 
			beta = res.x[0]

			KS_dist, _ = stats.kstest(data_, cdf_TPL, args=(a, beta, b)) 

			# MONTE-CARLO SIMULATIONS
			list_beta_sim = []
			pvalue = 0
			for i in range(Nsimulaitons):
				print("\ra={:9.1f}  | b={:9.1f}  | # simulations={:4d}".format(a, b, i+1), end="")
				# Inverse transform sampling
				data_sim = a*(1-(1-(a/b)**(beta-1))*np.random.rand(N))**(1/(1-beta))
				# "beta" simulation determination
				res = minimize(loglikelihood_TPL, 2.5, method='SLSQP', bounds=[beta_bounds], tol=optimization_precision, args=(data_sim,a,b)) # x0 = 2.5 initial guess
				beta_sim = res.x[0]
				list_beta_sim += [beta_sim] # for beta error
				KS_dist_sim, _ = stats.kstest(data_sim, cdf_TPL, args=[a, beta_sim, b])
				# acception/rejection
				if KS_dist_sim >= KS_dist: 
					pvalue += 1

			# Final values
			pvalue = pvalue/Nsimulaitons
			beta_error = np.std(list_beta_sim)
			OUTPUT += [[a, b, beta, beta_error, pvalue, N, xmax]]

			print("\ra={:9.1f}  | b={:9.1f}  | # simulations={:4d}    | p-value={:0.2f}".format(a, b, i+1, pvalue), end="")

			b_previous = b

		a_previous = a

	print("")

	##############################

	# SELECT BEST FIT

	max_ba = 0
	best_fit = []

	for i in range(len(OUTPUT)):
		a = OUTPUT[i][DATA_VARIABLES["truncated"].index("a")]
		b = OUTPUT[i][DATA_VARIABLES["truncated"].index("b")]
		pvalue = OUTPUT[i][DATA_VARIABLES["truncated"].index("pvalue")]
		if (pvalue >= pvalue_threshold) and (b/a > max_ba): # b/a = maximum distance in logaritmic axis
			best_fit = OUTPUT[i]
			max_ba = b/a

	if len(best_fit) == 0: # no fit found that has pvalue >= pvalue_threshold 
		return None

	return best_fit


##############################

# UNTRUNCATED POWER LAW

DATA_VARIABLES["untruncated"] = ["a", "beta", "beta_error", "pvalue", "Nfit", "n_max"]

def cdf_UPL(x, a, beta):
	"""
	Cumulative function for untruncated power law. 
	pdf(x) = (beta-1)/a * (a/x)^beta
	for x >= a
	"""
	F = 1-(a/x)**(beta-1)
	return F

def untruncated_power_law(data, a_upperbound=a_upperbound, a_lowerbound=a_lowerbound, pvalue_threshold=pvalue_threshold, Nsimulaitons=Nsimulaitons, 
								step_partitions=step_partitions, optimization_precision=optimization_precision, beta_bounds=beta_bounds):

	# INICIALIZE VARIABLES
	if a_upperbound is None: a_upperbound = np.max(data) 
	if a_lowerbound is None: a_lowerbound = np.min(data)
	xmin = np.min(data) 
	xmax = np.max(data) 

	##############################

	# PARAMETERS "a" AND "beta" DETERMINATION BY MAXIMUM LIKELIHOOD METHOD

	for a in 10**np.arange(np.log10(a_lowerbound), np.log10(a_upperbound)+step_partitions, np.abs(step_partitions)): # logarithmic binning
		# "beta" DETERMINATION
		data_ = data[np.where(data >= a)]
		N = len(data_)
		beta = 1 + 1/(-np.log(a) + np.sum(np.log(data_))/N)
		KS_dist, _ = stats.kstest(data_, cdf_UPL, args=(a, beta))

		# MONTE-CARLO SIMULATIONS
		list_beta_sim = []
		pvalue = 0
		for i in range(Nsimulaitons):
			print("\ra={:9.1f}  | # simulations={:4d}".format(a, i+1), end="")
			# Inverse transform sampling
			data_sim = a*(1-np.random.rand(N))**(1/(1-beta))
			# "beta" simulation determination
			beta_sim = 1 + 1/(-np.log(a) + np.sum(np.log(data_sim))/N)
			list_beta_sim += [beta_sim] # for beta error
			KS_dist_sim, _ = stats.kstest(data_sim, cdf_UPL, args=[a, beta_sim])
			# acception/rejection
			if KS_dist_sim >= KS_dist: 
				pvalue += 1

		# Final values
		pvalue = pvalue/Nsimulaitons
		beta_error = np.std(list_beta_sim)

		print("\ra={:9.1f}  | # simulations={:4d}    | p-value={:0.2f}".format(a, i+1, pvalue), end="")

		if pvalue >= pvalue_threshold:
			break

	print("")

	if pvalue < pvalue_threshold:
		return None

	return [a, beta, beta_error, pvalue, N, xmax]

##############################

DATA_VARIABLES["untruncated2"] = ["a", "b", "beta", "beta_error", "pvalue", "Nfit", "n_max"]


def untruncated_power_law_2(data, a_upperbound=a_upperbound, a_lowerbound=a_lowerbound, pvalue_threshold=pvalue_threshold, Nsimulaitons=Nsimulaitons, 
								step_partitions=step_partitions, optimization_precision=optimization_precision, beta_bounds=beta_bounds):

	# INICIALIZE VARIABLES
	if a_upperbound is None: a_upperbound = np.max(data) 
	if a_lowerbound is None: a_lowerbound = np.min(data)
	xmin = np.min(data) 
	xmax = np.max(data) 

	b = 1E100

	##############################

	# PARAMETERS "a" AND "beta" DETERMINATION BY MAXIMUM LIKELIHOOD METHOD

	for a in 10**np.arange(np.log10(a_lowerbound), np.log10(a_upperbound)+step_partitions, np.abs(step_partitions)): # logarithmic binning (from left to right)

		# "beta" DETERMINATION (maximum likelihood)
		data_ = data[np.where((a <= data) & (data <= b))]
		N = len(data_)
		if (N == 0) or (np.abs(a-b) < 2.1): # if they have less diference than 2, they only include 2 types of frequencies = a line
			print("\ra={:9.1f}  | # simulations={:4d}    | EXITED".format(a, i+1, pvalue), end="")
			continue # empty data to fit

		guess = beta = 1 + 1/(-np.log(a) + np.sum(np.log(data_))/N) # initial guess

		res = minimize(loglikelihood_TPL, guess, method='SLSQP', bounds=[beta_bounds], tol=optimization_precision, args=(data_,a,b))
		beta = res.x[0]

		KS_dist, _ = stats.kstest(data_, cdf_TPL, args=(a, beta, b)) 

		# MONTE-CARLO SIMULATIONS
		list_beta_sim = []
		pvalue = 0
		for i in range(Nsimulaitons):
			print("\ra={:9.1f}  | # simulations={:4d}".format(a, i+1), end="")
			# Inverse transform sampling
			data_sim = a*(1-(1-(a/b)**(beta-1))*np.random.rand(N))**(1/(1-beta))
			# "beta" simulation determination
			res = minimize(loglikelihood_TPL, 2.5, method='SLSQP', bounds=[beta_bounds], tol=optimization_precision, args=(data_sim,a,b)) # x0 = 2.5 initial guess
			beta_sim = res.x[0]
			list_beta_sim += [beta_sim] # for beta error
			KS_dist_sim, _ = stats.kstest(data_sim, cdf_TPL, args=[a, beta_sim, b])
			# acception/rejection
			if KS_dist_sim >= KS_dist: 
				pvalue += 1

		# Final values
		pvalue = pvalue/Nsimulaitons
		beta_error = np.std(list_beta_sim)

		print("\ra={:9.1f}  | # simulations={:4d}    | p-value={:0.2f}".format(a, i+1, pvalue), end="")

		if pvalue >= pvalue_threshold:
			break

	print("")

	if pvalue < pvalue_threshold:
		return None

	return a, b, beta, beta_error, pvalue, N, xmax


##############################

# LOGNORMAL

DATA_VARIABLES["lognormal"] = ["a", "mu", "mu_error", "sigma", "sigma_error", "pvalue", "Nfit", "n_max"]

def cdf_TLOGN(x, a, mu, sigma):
	"""
	Cumulative function for truncated lognormal. 
	pdf(x) = 1/(x*sigma)*sqrt(2/pi)*(1 - erf((ln a - mu)^2/(2*sigma^2)))^-1*exp(-(ln x - mu)^2/(2*sigma^2))
	for x >= a
	"""
	z   = (np.log(x) - mu)/(np.sqrt(2)*sigma)
	z_a = (np.log(a) - mu)/(np.sqrt(2)*sigma)
	F = (special.erf(z) - special.erf(z_a))/(1 - special.erf(z_a))
	return F

def loglikelihood_TLOGN(x, data, a):
	"""
	(Minus) Loglikelihood function for truncated lognormal
	x = mu, sigma = mean, deviation
	a = range of truncated lognormal (x >= a)
	data = np.array of frequencies
	The minus is for the minimization (to be maximization)
	"""
	mu, sigma = x
	N = len(data)
	z_a   = (np.log(a) - mu)/(np.sqrt(2)*sigma)
	logL = N*np.log( np.sqrt(2/np.pi)*1/(sigma*(1 - special.erf(z_a))) ) - np.sum(np.log(data) + (np.log(data) - mu)**2 / (2*sigma**2))
	return - logL

def truncated_lognormal(data, a_upperbound=a_upperbound, a_lowerbound=a_lowerbound, pvalue_threshold=pvalue_threshold, Nsimulaitons=Nsimulaitons, 
								step_partitions=step_partitions, optimization_precision=optimization_precision, beta_bounds=beta_bounds):

	# INICIALIZE VARIABLES
	if a_upperbound is None: a_upperbound = np.max(data) 
	if a_lowerbound is None: a_lowerbound = np.min(data)
	xmin = np.min(data) 
	xmax = np.max(data) 

	##############################

	# PARAMETERS "a", "mu" AND "sigma" DETERMINATION BY MAXIMUM LIKELIHOOD METHOD

	for a in 10**np.arange(np.log10(a_lowerbound), np.log10(a_upperbound)+step_partitions, np.abs(step_partitions)): # logarithmic binning
		# "mu", "sigma" DETERMINATION
		data_ = data[np.where(data >= a)]
		N = len(data_)

		res = minimize(loglikelihood_TLOGN, (2.5, 1), method='SLSQP', tol=optimization_precision, args=(data_,a)) # x0 = (2.5, 1) initial guess
		mu, sigma = res.x[0], res.x[1]

		KS_dist, _ = stats.kstest(data_, cdf_TLOGN, args=(a, mu, sigma))

		# MONTE-CARLO SIMULATIONS
		list_mu_sim = []
		list_sigma_sim = []
		pvalue = 0
		for i in range(Nsimulaitons):
			print("\ra={:9.1f}  | # simulations={:4d}".format(a, i+1), end="")
			# Inverse transform sampling
			B = special.erf((np.log(a) - mu)/(np.sqrt(2)*sigma))
			data_sim = np.exp(mu + np.sqrt(2)*sigma*special.erfinv( np.random.rand(N)*(1-B) + B ))
			# "beta" simulation determination
			res = minimize(loglikelihood_TLOGN, (2.5, 1), method='SLSQP', bounds=logn_bounds, tol=optimization_precision, args=(data_sim,a)) # x0 = (2.5, 1) initial guess
			mu_sim, sigma_sim = res.x[0], res.x[1]
			list_mu_sim += [mu_sim] # for mu error
			list_sigma_sim += [sigma_sim] # for sigma error
			KS_dist_sim, _ = stats.kstest(data_sim, cdf_TLOGN, args=[a, mu_sim, sigma_sim])
			# acception/rejection
			if KS_dist_sim >= KS_dist: 
				pvalue += 1

		# Final values
		pvalue = pvalue/Nsimulaitons
		mu_error = np.std(list_mu_sim)
		sigma_error = np.std(list_sigma_sim)

		print("\ra={:9.1f}  | # simulations={:4d}    | p-value={:0.2f}".format(a, i+1, pvalue), end="")

		if pvalue >= pvalue_threshold:
			break

	print("")

	if pvalue < pvalue_threshold:
		return None

	return [a, mu, mu_error, sigma, sigma_error, pvalue, N, xmax]


##############################
##############################
##############################

# PERFORM THE FITTINGS 

OUTPUT_ALL = {name:{i:[] for i in TODO} for name in os.listdir(INPUT_DIR)}

for INPUT_NAME in sorted(os.listdir(INPUT_DIR)):
	# LOAD DATA
	# data = array of frequencies distributed following a untruncated power law, 
	# equivalent to the absolute frequencies obtained from the type counts ("Zipf counts"). 
	# This section can vary depending on the input format. 

	print(INPUT_NAME)

	f = open(INPUT_DIR + "/" + INPUT_NAME)
	data = f.read()
	f.close()
	data = np.array([int(i.split(" ")[1]) for i in data.split("\n") if i!=""]) # example of line: "010100010101 431" 

	# PERFOM SELECTED FITS

	if "untruncated" in TODO:
		data_fit = untruncated_power_law(data, a_upperbound=None)
		OUTPUT_ALL[INPUT_NAME]["untruncated"] = data_fit

	if "untruncated2" in TODO:
		data_fit = untruncated_power_law_2(data, a_upperbound=None)
		OUTPUT_ALL[INPUT_NAME]["untruncated2"] = data_fit

	if "truncated" in TODO:
		data_fit = truncated_power_law(data)
		OUTPUT_ALL[INPUT_NAME]["truncated"] = data_fit

	if "lognormal" in TODO:
		data_fit = truncated_lognormal(data)
		OUTPUT_ALL[INPUT_NAME]["lognormal"] = data_fit


##############################

# SAVE VALUES

for type_dist in TODO:

	f = open(OUTPUT_FILE.replace("DISTRIBUTION", type_dist), "w")
	f.write(",".join(["file_name"] + DATA_VARIABLES[type_dist]) + "\n")

	for INPUT_NAME in sorted(os.listdir(INPUT_DIR)):
		if OUTPUT_ALL[INPUT_NAME][type_dist] is None: 
			f.write(",".join([INPUT_NAME] + ["-"]*len(DATA_VARIABLES[type_dist])) + "\n")
		else:
			f.write(",".join([INPUT_NAME] + [str(i) for i in OUTPUT_ALL[INPUT_NAME][type_dist]]) + "\n")

	f.close()



