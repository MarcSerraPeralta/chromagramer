# Big Data Analysis of Music using MIDI files

Analysis of the chromagram, lenght (_L_) and vocabulary (_V_) of a given corpus of MIDI files. 

The corpus must have the structure described in [`dat/README.md`](dat/README.md). 
The corpus used for our results is the [Kunstderfuge dataset](http://www.kunstderfuge.com/) and its Zipf data can be found in `dat/zipf_midi_original.zip`. 


## Installation

Suggested steps are:

1. Clone repository.
1. Create a conda environment (may use `requirements.txt` file).
1. The following folder structure will be produced by the repo. From the git folder:
    - `lib/`: contains all the scripts.
    - `dat/`: will contain all the corpus and extracted data.
1. Copy the corpus' folder inside `dat/` (see [`dat/README.md`](dat/README.md) for further information). 
1. Install `midi2abc` ([guide](https://command-not-found.com/midi2abc))

> :warning: **Check that the following command can be run on terminal**: `midi2abc -h`
> 
> This command is needed to transform MIDI files to txt files in [`lib/midi2txt.py`](lib/midi2txt.py). 


## Running the code

All the following instructions are assumed to be run from the git folder. 

### Replicating the results (_Kunstderfuge_ corpus)

Firstly, change the variable `corpus_folder` inside `script.py` to the _Kunstderfuge_ folder's name (or change the _Kunstderfuge_ folder's name to _midi_kunstderfuge_). 

Secondly, execute:
```
python script.py
```

### Using any corpus

Delete the lines of corpus' preparation in `script.py`. Change the variable `corpus_folder` inside `script.py` to the corpus folder's name. Finally, execute:
```
python script.py
```

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


## Results

Brief description of the output files and their format. 

### 1) Continous chromagram folder (`chr_kunstderfuge` by default)

It has the same tree structure as _Kunstderfuge_ corpus' folder and its files have the same names as the input ones. 
The structure of each file is:
1. First line: time in which the piece changes its key signature (`.2f` separated by spaces).
1. Second line: time and bar of the different parts of the piece (`.2f X/Y` separated by two spaces).
1. Rest of the lines: continous chromagran with chroma duration specified by `Atmin` in `lib/txt2input.py` (12 `.2f` separated by spaces, each line).

### 2) `zipf_authors` folder

It contains the Zipf information of each author in the dataset (joined author's pieces). 

For further information of the format, check `zipf2note` function in `lib/extra.py`. 

### 3) `zipf_corpus_...` file

Same structure as the files in `zipf_authors` folder. All corpus' pieces have been joined together for this Zipf. 

### 4) `LV_authors_...` and `LV_pieces_...` files

Both files contains the following information for each author/piece: `author L V`

### 5) `table_LV...` and `table_richness...` files

Check `LV_table` function in `lib/extra.py` and `LV2richness` function in `lib/LV2richness.py` respectively. 

### 6) `histogram_keys.txt` and `histogram_keys.pdf`

The txt file contains the key signature of each piece (separated by a space). 

The pdf file is the histogram representation of the information in `histogram_keys.txt`. 


## Notes

- We do not provide any support or assistance for the supplied code nor we offer any other compilation/variant of it.
- We assume no responsibility regarding the provided code.
