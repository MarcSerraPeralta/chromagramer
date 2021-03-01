import os

from lib import main

from lib import extra
from lib import input2LVzipf
from lib import LV2richness
from lib import mid2txt
from lib import txt2input
from lib.prepare_kunstderfuge import prepare_corpus

##################################################################

# directory that contains all the data to analyse
corpus_folder = "midi_kunstderfuge"

# output folders
output_txt = "txt_kunstderfuge"
output_chr = "chr_kunstderfuge"

##################################################################

# PREPARE CORPUS
print("PREPARING CORPUS...")
prepare_corpus(corpus_folder)
print("Done")

# GENERATE TXT FILES FROM MIDI FILES
print("\nGENERATING TXT FILES...")
main.database(corpus_folder, mid2txt.mid2txt, OUTDIR=output_txt) 
print("Done")
# calculate txt files
n_files = sum([len(files) for r, d, files in os.walk("dat/" + output_txt)])
print("Total number of txt files in corpus:", n_files, "(should be 10523)")
print("(midi files that are not corrupted and can be translated to txt)")

# GENERATE CONTINUOUS CHROMAS
print("\nGENERATING CONTINUOUS CHROMAS...")
main.database(output_txt, txt2input.txt2input, OUTDIR=output_chr, POSTFUNCT=txt2input.post_txt2input)
print("Done")
# calculate txt files
n_files = sum([len(files) for r, d, files in os.walk("dat/" + output_chr)])
print("Total number of chr files in corpus:", n_files, "(should be 9564)")
print("(txt files that fulfill all the requirements (bar, not-empty,...))")

# CALCULATE L,V,zipf_authors
print("\nCALCULATING L,V,ZIPF_AUTHORS...")
main.database(output_chr, input2LVzipf.input2LVzipf, OUTDIR="tmp", ARGS=[0.25, 1, 0.1, "transposed"], 
	PREFUNCT=input2LVzipf.pre_input2LVzipf, POSTFUNCT=input2LVzipf.post_input2LVzipf)
print("Done")
# calculate Ltotal, Vtotal corpus
Ltotal = extra.get_Ltotal("zipf_corpus_transposed_1-00_0-1000.txt", PRINT=False)
Vtotal = extra.get_Vtotal("zipf_corpus_transposed_1-00_0-1000.txt", PRINT=False)
print("Total L and V of corpus: L={} V={}".format(Ltotal, Vtotal), "(should be 5152589 and 4085)")

# LINEAR REGRESSION logV vs logL
print("\nLINEAR REGRESSION logV vs logL")
extra.LV_regression(["LV_authors_transposed_1-00_0-1000.txt","LV_pieces_transposed_1-00_0-1000.txt"])
print("Done")

# CREATE TABLE LV AND HISTOGRAM OF KEYS
print("\nCREATE TABLE LV...")
extra.LV_table(1, 0.1)
print("Done")
print("\nPLOTS HISTOGRAM OF KEYS...")
main.database(output_chr, extra.get_hist_keys, ARGS=[0.25, 1, 0.1], POSTFUNCT=extra.post_get_hist_keys)
extra.plot_hist_keys()
print("Done")

# CREATE TABLE RICHNESS
print("\nCREATE TABLE RICHNESS...")
LV2richness.LV2richness(1, 0.1)
print("Done")