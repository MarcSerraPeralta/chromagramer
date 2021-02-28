import numpy as np
import os
import math


##################################################################
#						   TXT2INPUT							 #
##################################################################

def txt2input(INDIR, path, fname, OUTDIR, ARGS, intranet):
	"""
	Converts an output txt file (from 'abc2midi') to a continuous chromagram. 
	ARGS = [duration of chromas in units of beat duration (duration of a beat = 1)]
	Default value for ARGS = [0.25] (semiquaver). 

	Txt output structure:
	* first line = times (normalized by ARGS[0]) where the key changes (given by the MIDI file).
	* second line = changes of bar (given by the MIDI file).
	* next lines = each line is a continuous chroma
	"""
	# DEFAULT PARAMETERS
	if len(ARGS) == 0: ARGS = [0.25] # default (ARGS is a list)
	At = ARGS[0] 

	# CHECK TXT IS UTF-8
	try:
		file = open(INDIR + "/" + path + fname, "r")
		_ = file.read()
		file.close()
	except UnicodeDecodeError:
		intranet += [INDIR + "/" + path + fname]
		return intranet

	# GET BAR
	file = open(INDIR + "/" + path + fname, "r")
	time_signature = []
	for line in file:
		if "Metatext time signature=" in line: 
			time = float(line[:line.index("Metatext time signature=")])
			compass = line[line.index("Metatext time signature=") + 24:-1]
			time_signature += [[time, compass]]
	file.close()
	if len(time_signature) == 0: # skips piece without time signature and reports its name
		intranet += [INDIR + "/" + path + fname]
		return intranet
	time_signature.sort() # sort for ti < ti+1

	# GET MATRIX on off NOTES
	file = open(INDIR + "/" + path + fname, "r")
	M_track = [] 
	
	for line in file:
		if line[:5] == "Track":
			M_track += [[np.array([[0, 0]]), np.array([[0, 0]])]] # M on , M off (time, pitch)
			continue
		if "Note on" in line: # M on
			t = Umidi2Ubeats(float(line[:line.index("   ")]), time_signature)
			pitch = note2number(line[line.index("(") + 1 : line.index(")") -1]) + 12*int(line[line.index(")") - 1 : line.index(")")])
			volume = float(line[line.index(")") + 1 : line.index(")") + 5]) # there is "\n"
			if volume != 0: # note on ==> M on
				M_track[-1][0] = np.append(M_track[-1][0], [[t, pitch]], axis=0)
			else: # equivalent to note off ==> M off
				M_track[-1][1] = np.append(M_track[-1][1], [[t, pitch]], axis=0)
		if "Note off" in line: # M off
			t = Umidi2Ubeats(float(line[:line.index("   ")]), time_signature)
			pitch = note2number(line[line.index("(") + 1 : line.index(")") -1]) + 12*int(line[line.index(")") - 1 : line.index(")")])
			M_track[-1][1] = np.append(M_track[-1][1], [[t, pitch]], axis=0)

	for i in range(len(M_track)):
		M_track[i][0] = np.delete(M_track[i][0], 0, 0) # deletes first row of M on (empty)
		M_track[i][1] = np.delete(M_track[i][1], 0, 0) # deletes first row of M off (empty)

	file.close()
	
	# MATRIX TO CHROMAGRAM  
	chromagram = np.zeros((1,12))

	for M in M_track:
		Mon, Moff = M
		total = len(Mon)

		while len(Mon) != 0:
			tf = None
			# get first "note on"
			ti = Mon[0,0]
			p = Mon[0,1]
			Mon = np.delete(Mon, 0, axis=0)
			# search closest end of this note
			for i, tpv in zip(range(len(Moff)), Moff):
				if tpv[1] == p and tpv[0] >= ti: 
					tf = tpv[0]
					Moff = np.delete(Moff, i, axis=0)
					break
			if tf is None: continue # there are some errors in abc2midi
			# check if chromagram is big enough for this note
			if len(chromagram)*At <= tf:
				more = math.ceil(tf/At) + 1 - len(chromagram)
				chromagram = np.append(chromagram, np.zeros((more,12)), axis=0)
			# adds time of this note in chromagram
			Ni = int(ti/At)
			Nf = int(tf/At)
			p = int(p % 12) # convert from p=0...127 to p=0...11
			if Nf - Ni == 0: # note is in the same element of chromagram
				chromagram[ Ni, p ] += tf - ti
			elif Nf - Ni == 1: # note is in two chromagram elements
				chromagram[ Ni, p ] += At - (ti % At)
				chromagram[ Nf, p ] += (tf % At)
			elif Nf - Ni >= 2: # notes is in more than two chromagram elements
				chromagram[ Ni, p ] += At - (ti % At)
				chromagram[ Nf, p ] += (tf % At)
				chromagram[ Ni+1:Nf-1, p] += At

	# GET KEY CHANGES 
	txt = open(INDIR + "/" + path + fname, "r")
	time = [] # beat in which the key changes
	keys = [] 
	previouskey = ""

	file = txt.read().split("\n")
	txt.close()
	for line in file:
		if "Metatext key signature" in line:
			key = line[line.index("Metatext key signature"):].split(" ")[3]
			if previouskey != key:
				t = float(line[:7])
				time += [t]
				keys += [key2num(key)]
			previouskey = key
	
	# For the problem of having multiple t=0 and other times in the same music sheet
	time = ["{0:0.2f}".format(i/At) for i in sorted(time)]

	if len(keys)==0 or -1 in keys or time[0] != "0.00": # cheks if there is any key or if there is a (null) key
		time = ["None"]

	# SAVE CHROMAGRAM
	f = open(OUTDIR + "/" + path + fname, "w") 
	f.write(" ".join(time) + "\n")
	f.write("  ".join(["{0:0.2f} {1}".format(*i) for i in time_signature]) + "\n")
	for line in chromagram:
		f.write(" ".join(["{0:0.2f}".format(j) for j in line]) + "\n")
	f.close()

	return intranet

def post_txt2input(INDIR, FUNCTION, OUTDIR, ARGS, intranet):
	"""
	Deletes authors without any piece. 

	Can report pieces without time signature (stored in intranet)
	"""
	print("\n")
	for a in os.listdir(OUTDIR):
		if ("." not in a) and (len(os.listdir(OUTDIR + "/" + a)) == 0): # excludes possible files "*.*"
			os.rmdir(OUTDIR + "/" + a)
			print("WARNING: Deleted {} because its folder was empty".format(a))

	return []

##################################################################

def key2num(key):
	"""
	Translates MIDI key to a number. 
	"""
	key2num = {"C": 0, "Db": 1, "D": 2, "Eb": 3, "E": 4, "F": 5, "Gb": 6, "G": 7, "Ab": 8, "A": 9, "Bb": 10, "B": 11, 
				"Cb": 11, "C#": 1, "D#": 3, "F#": 6, "G#": 8, "A#": 10, "B#": 0, 
	"Cmin": 20, "Dbmin": 21, "Dmin": 22, "Ebmin": 23, "Emin": 24, "Fmin": 25, "Gbmin": 26, "Gmin": 27, "Abmin": 28, "Amin": 29, "Bbmin": 30, "Bmin": 31, 
	"Cbmin": 31, "C#min": 21, "D#min": 23, "F#min": 26, "G#min": 28, "A#min": 30, "minB#": 20, 
	"(null)": -1}   
	return key2num[key]

def note2number(note):
	"""
	Translates MIDI note to a number from 0 to 11 (C=0, C#=1 ...). 
	"""
	note2number = {" c": 0, "c#": 1, " d": 2, "d#": 3, " e": 4, " f": 5, "f#": 6, 
					" g": 7, "g#": 8, " a": 9, "a#": 10, " b": 11, 
					"c-": 0, "c#-": 1, "d-": 2, "d#-": 3, "e-": 4, "f-": 5, "f#-": 6, 
					"g-": 7, "g#-": 8, "a-": 9, "a#-": 10, "b-": 11}
	return note2number[note]

def Umidi2Ubeats(tmidi, time_signature):
	"""
	Converts time in the MIDI's units (quarter note) to beat units. 
	"""
	compass = time_signature.copy()
	compass += [[1E99, "None"]] # for last compass to be taken in consideration

	tbeat = 0
	for i in range(len(compass)-1):
		c = compass[i][1]
		Y = int(c.split("/")[1]) # format of c = "X/Y" (ex. 3/4 bar)
		if tmidi >= compass[i+1][0]:
			tbeat += (Y/4)*(compass[i+1][0] - compass[i][0])
		if (compass[i][0] < tmidi) and (tmidi < compass[i+1][0]):
			tbeat += (Y/4)*(tmidi - compass[i][0])
			break

	return tbeat