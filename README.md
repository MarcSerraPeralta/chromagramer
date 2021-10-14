# Heaps' Law and Vocabulary Richness in the History of Classical Music Harmony

### Abstract

Music is a fundamental human construct, and harmony provides the building blocks of musical language. Using the Kunstderfuge corpus of classical music, we analyze the historical evolution of the richness of harmonic vocabulary of 76 classical composers, covering almost 6 centuries. Such corpus comprises about 9500 pieces, resulting in more than 5 million tokens of music codewords. The fulfilment of Heaps' law for the relation between the size of the harmonic vocabulary of a composer (in codeword types) and the total length of his works (in codeword tokens), with an exponent around 0.35, allows us to define a relative measure of vocabulary richness that has a transparent interpretation. When coupled with the considered corpus, this measure allows us to quantify harmony richness across centuries, unveiling a clear increasing linear trend. In this way, we are able to rank the composers in terms of richness of vocabulary, in the same way as for other related metrics, such as entropy. We find that the latter is particularly highly correlated with our measure of richness. Our approach is not specific for music and can be applied to other systems built by tokens of different types, as for instance natural language.

### Reference

Serra-Peralta, M., Serrà, J. & Corral, Á. Heaps’ law and vocabulary richness in the history of classical music harmony. EPJ Data Sci. 10, 40 (2021). https://doi.org/10.1140/epjds/s13688-021-00293-8


## Description

Big Data analysis of music using MIDI files through their lenght (_L_), vocabulary (_V_) and token-type distribution (_f(n)_). 

The corpus must have the structure described in [`dat/README.md`](dat/README.md). 
The corpus used for our results is the [Kunstderfuge dataset](http://www.kunstderfuge.com/) and its Zipf data can be found in `dat/zipf_midi_original.zip`. 


## Installation

Suggested steps are:

1. Clone repository.
1. Create a conda environment (see `requirements.txt` file).
1. The following folder structure will be produced by the repo. From the git folder:
    - `lib/`: contains all the scripts.
    - `dat/`: will contain all the corpus and extracted data.
1. Copy the corpus' folder inside `dat/` (see [`dat/README.md`](dat/README.md) for further information). 
1. Install `midi2abc` ([guide](https://command-not-found.com/midi2abc))

> :warning: **Check that the following command can be run on terminal**: `midi2abc -h`
> 
> This command is needed to transform MIDI files to txt files in [`lib/midi2txt.py`](lib/midi2txt.py). 


## Replicating the results (_Kunstderfuge_ corpus)

Firstly, change the variable `corpus_folder` inside `script.py` to the _Kunstderfuge_ folder's name (or change the _Kunstderfuge_ folder's name to _midi_kunstderfuge_). 

Secondly, execute:
```
python script.py
python lib/fit_max_likelihood.py
python lib/select_best_distribution.py
```

> :bookmark: All functions can be used for other datasets following the same structure as defined in [`dat/README.md`](dat/README.md). 
>
> The only change needed in [`script.py`](script.py) is to delete the `prepare_corpus(...)` line. 


## Structure of the code

The code has two steps:

1. Extracting L,V and frequency counts
1. Performing fits to the probability density function of the frequency

> :warning: All the following instructions are assumed to be run from the git folder. 

### Using `main.database` function (in `lib/main.py`)

This function is useful to analyse a dataset that has any tree structure with the files to analyse. 

In generall, the following procedure is followed:
1. `PREFUNCT` is executed
1. `FUNCTION` is executed to each file of the given directory
1. `POSTFUNCT` is executed

The variable `intranet` allows to use previous information or to store data from each file. 

If `OUTDIR` is specified, it creates the same tree structure of `INDIR`. 

The variable `ARGS` is a list to pass extra arguments to `FUNCTION` function. 

For further information check `functionexample`, `prefunct`, `postfunct` and `database` functions in `lib/main.py`. 

### Using `lib/fit_max_likelihood.py`

This script fits (1) truncated power-law, (2) untruncated power-law, and (3) truncated lognormal pdf in a given random variable. 
The fit is accepted if the p-value is greater or equal than a threshold (0.20 by default). 
The outputs of the fitting functions are:

1. `truncated_power_law`: a, b, beta, beta_error, pvalue, N, xmax
1. `untruncated_power_law`: a, beta, beta_error, pvalue, N, xmax
1. `untruncated_power_law_2`: a, b, beta, beta_error, pvalue, N, xmax
1. `truncated_lognormal`: a, mu, mu_error, sigma, sigma_error, pvalue, N, xmax

where `a` is the lower limit of the fitting, `b` is the upper limit of the fit, `beta` is the power-law exponent (`beta_error` its error), `pvalue` is the p-value of the Montecarlo simulations, `N` is the number of data points fitted, `xmax` is the maximum value of the data points, `mu` is the mean of the lognormal (`mu_error` its error), and `sigma` is the standard deviation of the lognormal (`sigma_error` its error).  

The `untruncated_power_law` performs an untruncated-power-law likelihood fit and `untruncated_power_law_2` performs a truncated-power-law likelihood fit with `b=1E100`. 


## Results

Brief description of the output files and their format can be found in [`description_results.md`](description_results.md).

For further data processing, there are some useful functions in [`lib/extra.py`](lib/extra.py):
1. `get_Ltotal`: returns total L of a Zipf or LV file.
1. `get_Vtotal`: returns total V of a Zipf or LV file.
1. `get_hist_keys`: saves the key counts of all database in `histogram_keys.txt` file. 
1. `plot_hist_keys`: plots a histogram of `histogram_keys.txt` file. 
1. `LV_table`: creates CSV table containing: Author, Birth, Death, L, V, #pieces.
1. `LV_regression`: returns the linear-regression parameters of logV vs logL. 
1. `cdw2note`: returns the musical notes of a binary codeword. 
1. `zipf2note`: returns the musical notes of a Zipf file. 

## Notes

- We do not provide any support or assistance for the supplied code nor we offer any other compilation/variant of it.
- We assume no responsibility regarding the provided code.
