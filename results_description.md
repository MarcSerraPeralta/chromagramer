## Text files folder (`txt_kunstderfuge` by default)

It has the same tree structure as input folder (_Kunstderfuge_ corpus' folder by default) and its files have the same names as the input ones. 
The text files are the output files of `midi2abc`. 

## Continous chromagram folder (`chr_kunstderfuge` by default)

It has the same tree structure as input folder (_Kunstderfuge_ corpus' folder by default) and its files have the same names as the input ones. 
The structure of each file is:
1. First line: time in which the piece changes its key signature (`.2f` separated by spaces).
1. Second line: time and bar of the different parts of the piece (`.2f X/Y` separated by two spaces).
1. Rest of the lines: continous chromagran with chroma duration specified by `Atmin` in `lib/txt2input.py` (12 `.2f` separated by spaces, each line).

## `zipf_authors` folder

It contains the Zipf information (meaning the codeword's type frequencies) of each author in the dataset (aggregated author's pieces). 
Each row of the file has the token and types of each codeword (sorted descending):
```
100010010000 1659     # codeword 100010010000 appears with absolute frequency = 1659
000000000000 1461
100001000100 1157
(...)
```

> :bookmark: `zipf2note` function in [`lib/extra.py`](lib/extra.py) translates binary codewords to chords
>
> example: "010010000100" ==> ['C#', 'E', 'A'] 

## `list_short_pieces.txt` file

It contains the full path and name of the pieces with `L <= Lmin` (see [`script.py`](script.py))

## `zipf_corpus_(...).txt` file 

It is the aggregation of all pieces in the input folder, with the same structure as the files in `zipf_authors` folder. 

By default, its name is `zipf_corpus_transposed_1-00_0-1000.txt`. 

## `LV_authors_(...).txt` and `LV_pieces_(...).txt` files 

Both files contain the following information for each author/piece: `author L V`:
```
albeniz 42313 1666
albinoni 29245 711
albrechtsberger 4760 511
```
By default, their names are `LV_authors_transposed_1-00_0-1000` and `LV_pieces_transposed_1-00_0-1000`. 

## `zipf_authors_(...).csv` files 

It contains a table with the parameters of the maximum likelihood fit of each author, as well as other important variables. 

## `best_distribution_authors.csv` file

It contains the best fit of each author following the criteria of [`select_best_distribution.py`](lib/select_best_distribution.py). 
