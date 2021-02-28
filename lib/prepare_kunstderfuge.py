import os, shutil

##################################################################

# PREPARE AND CHECKS THE CORPUS TO REPLICATE RESULTS

def prepare_corpus(corpus_folder): 
	"""
	Prepares Kunstderfuge corpus to get reproducible results. 
	"""
	print("CORPUS FOLDER:", corpus_folder)
	# TOTAL NUMBER OF FILES
	n_files = sum([len(files) for r, d, files in os.walk("dat/" + corpus_folder)])
	print("Total number of files in corpus:", n_files)

	# TOTAL NUMBER OF MIDI FILES
	n_midi_files = sum([len([f for f in files if ".mid" in f]) for r, d, files in os.walk("dat/" + corpus_folder)])
	print("Total number of MIDI files in corpus:", n_midi_files)

	# DELETE FILES THAT ARE NOT MIDI
	for r, d, files in os.walk("dat/" + corpus_folder):
		for f in files:
			if ".mid" not in f: os.remove(os.path.join(r, f))
	print("Deleted non-MIDI files")

	# TOTAL NUMBER OF FILES
	n_files = sum([len(files) for r, d, files in os.walk("dat/" + corpus_folder)])
	print("Total number of files in corpus:", n_files)

	# DELETE MISCELLANEOUS FOLDERS
	delete_dir = ["!various-composers!", "!!piano-rolls-collection!!", "out", "!miscellaneous!", "!!live!!", "suelto", "anonymous"]
	for folder in delete_dir:
		if folder in os.listdir("dat/" + corpus_folder):
			shutil.rmtree("dat/" + corpus_folder + "/" + folder)
	print("Deleted miscellaneous folders")
	# check number of folders
	folders = [f for f in os.listdir("dat/" + corpus_folder) if os.path.isdir(os.path.join("dat/" + corpus_folder, f))]
	print("Number of authors in corpus:", len(folders), "(should be 77)")

	# TOTAL NUMBER OF MIDI FILES
	n_midi_files = sum([len([f for f in files if ".mid" in f]) for r, d, files in os.walk("dat/" + corpus_folder)])
	print("Total number of files in corpus:", n_midi_files, "(should be 10523)")

	return


if __name__ == '__main__':
	# directory that contains all the data to analyse
	corpus_folder = "midi_kunstderfuge"

	prepare_corpus(corpus_folder)