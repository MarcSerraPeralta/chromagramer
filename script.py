import os

from lib import main
from lib import extra, input2LVzipf, LV2richness, mid2txt, txt2input
from lib.prepare_kunstderfuge import prepare_corpus

##################################################################

# directory that contains all the data to analyse
corpus_folder = "midi_kunstderfuge"

# file with list of songs to be deleted because they are repeated
repeated_songs_file = "list_repeated_pieces.txt"

# minimum lenght (in beats) that songs must have (deletes songs with L <= Lmin)
Lmin = 15

# output folders
output_txt = "txt_kunstderfuge"
output_chr = "chr_kunstderfuge"

##################################################################

# PREPARE CORPUS 
# Deletes miscellaneous folders, files that are not MIDIs, repeated songs
print("STARTING PREPARING CORPUS...")
prepare_corpus(corpus_folder, repeated_songs_file=repeated_songs_file)
print("PREPARING CORPUS DONE")

# GENERATE TXT FILES FROM MIDI FILES
print("\nSTARTING GENERATING TXT FILES...")
main.database(corpus_folder, mid2txt.mid2txt, OUTDIR=output_txt) 
print("GENERATING TXT FILES DONE")
# calculate txt files
n_files = sum([len(files) for r, d, files in os.walk("dat/" + output_txt)])
print("Total number of txt files in corpus:", n_files)
print("(midi files that are not corrupted and can be translated to txt)")

# GENERATE CONTINUOUS CHROMAS
print("\nSTARTING GENERATING CONTINUOUS CHROMAS...")
main.database(output_txt, txt2input.txt2input, OUTDIR=output_chr, POSTFUNCT=txt2input.post_txt2input)
print("GENERATING CONTINUOUS CHROMAS DONE")
# calculate txt files
n_files = sum([len(files) for r, d, files in os.walk("dat/" + output_chr)])
print("Total number of chr files in corpus:", n_files)
print("(txt files that fulfill all the requirements (bar, not-empty,...))")

# DETELE PIECES SHORTER THAN Lmin (L <= Lmin)
main.database(output_chr, extra.get_short_pieces, ARGS = [Lmin, "list_short_pieces.txt"], POSTFUNCT=extra.post_get_short_pieces)
f = open("dat/list_short_pieces.txt", "r")
short_pieces = f.read()
f.close()
for name in [i for i in short_pieces.split("\n") if i != ""]:
	os.remove("dat/" + name)
# calculate txt files
n_files = sum([len(files) for r, d, files in os.walk("dat/" + output_chr)])
print("Total number of chr files in corpus:", n_files)
print("(chr files that fulfill all the requirements (not-short, bar, not-empty,...))")

# CALCULATE L,V,zipf_authors
print("\nSTARTING CALCULATING L,V,ZIPF_AUTHORS...")
main.database(output_chr, input2LVzipf.input2LVzipf, OUTDIR="tmp", ARGS=[0.25, 1, 0.1, "transposed"], 
	PREFUNCT=input2LVzipf.pre_input2LVzipf, POSTFUNCT=input2LVzipf.post_input2LVzipf)
print("CALCULATING L,V,ZIPF_AUTHORS DONE")
# calculate Ltotal, Vtotal corpus
Ltotal = extra.get_Ltotal("zipf_corpus_transposed_1-00_0-1000.txt", PRINT=False)
Vtotal = extra.get_Vtotal("zipf_corpus_transposed_1-00_0-1000.txt", PRINT=False)
print("Total L and V of corpus: L={} V={}".format(Ltotal, Vtotal))