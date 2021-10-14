import os, shutil

##################################################################

# PREPARE AND CHECKS THE CORPUS TO REPLICATE RESULTS

def prepare_corpus(corpus_folder, repeated_songs_file = "repeated_songs.txt"): 
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
	print("Deleting non-MIDI files... ", end="")
	for r, d, files in os.walk("dat/" + corpus_folder):
		for f in files:
			if ".mid" not in f: os.remove(os.path.join(r, f))
	print("Done")
	# TOTAL NUMBER OF FILES
	n_files = sum([len(files) for r, d, files in os.walk("dat/" + corpus_folder)])
	print("Total number of files in corpus:", n_files)

	# DELETE MISCELLANEOUS FOLDERS
	print("Deleting miscellaneous folders... ", end="")
	delete_dir = ["!various-composers!", "!!piano-rolls-collection!!", "out", "!miscellaneous!", "!!live!!", "suelto", "anonymous"]
	for folder in delete_dir:
		if folder in os.listdir("dat/" + corpus_folder):
			shutil.rmtree("dat/" + corpus_folder + "/" + folder)
	print("Done")
	# TOTAL NUMBER OF FOLDERS
	folders = [f for f in os.listdir("dat/" + corpus_folder) if os.path.isdir(os.path.join("dat/" + corpus_folder, f))]
	print("Total number of authors in corpus:", len(folders))
	# TOTAL NUMBER OF FILES
	n_files = sum([len(files) for r, d, files in os.walk("dat/" + corpus_folder)])
	print("Total number of files in corpus:", n_files)

	# DELETE REPEATED SONGS
	print("Deleting repeated songs... ", end="")
	if repeated_songs_file in os.listdir("dat"):
		f = open("dat/" + repeated_songs_file, "r")
		repeated_songs = f.read()
		f.close()
		repeated_songs = [i for i in repeated_songs.split("\n") if i != ""]
		ERROR = False
		for name in repeated_songs:
			try:
				os.remove("dat/" + corpus_folder + "/" + name)
			except:
				if not ERROR: print(""); ERROR = True
				print("Error: file does not exist '{}'".format(name))
		print("Done")
	else:
		print("Error: no file '{}}' found in 'dat/'".format(repeated_songs_file))

	# TOTAL NUMBER OF FOLDERS
	folders = [f for f in os.listdir("dat/" + corpus_folder) if os.path.isdir(os.path.join("dat/" + corpus_folder, f))]
	print("Total number of authors in corpus:", len(folders))
	# TOTAL NUMBER OF MIDI FILES
	n_midi_files = sum([len([f for f in files if ".mid" in f]) for r, d, files in os.walk("dat/" + corpus_folder)])
	print("Total number of files in corpus:", n_midi_files)

	return