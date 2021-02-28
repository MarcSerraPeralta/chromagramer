import subprocess as sub


##################################################################
#                           MID2TXT                              #
##################################################################

def mid2txt(INDIR, path, fname, OUTDIR, ARGS, intranet):
    """
    Description
    -----------
    Converts a MIDI file to a txt file (using midi2abc).
    """
    f_input = INDIR + "/" + path + fname
    f_output = OUTDIR + "/" + path + fname[:-4] + ".txt"

    p = sub.Popen("""midi2abc "{0}" -mftext > "{1}" """.format(f_input, f_output), stdout=sub.PIPE, shell=True)
    p.communicate()    

    return intranet