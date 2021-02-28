import numpy as np
import os, sys
import shutil
import subprocess as sub
import datetime

###############################################################################
#                             FUNCTION EXAMPLES                               #
###############################################################################
    
def functionexample(INDIR, path, fname, OUTDIR, ARGS, intranet):
    """
    Description
    -----------
    Example of the function to perform in each file. 
    Opens each file. 
    """
    f = open(INDIR + "/" + path + fname)
    f.close()

    return intranet

def prefunct(INDIR, FUNCTION, OUTDIR, ARGS):
    """
    Description
    -----------
    Function executed before processing any file. 
    Current working directory is "dat".
    example "check if all files inside 'directory' are .mid"
    """
    return #intranet

def postfunct(INDIR, FUNCTION, OUTDIR, ARGS, intranet):
    """
    Description
    -----------
    Function executed after processing all files. 
    Current working directory is "dat".
    example "collects all data from all files and summarizes it in one file"
    """
    #if intranet = [], postfunct does not write the report 
    return intranet
   
        
###############################################################################
#                                 FUNCTIONS                                   #
###############################################################################

def check(INDIR, FUNCTION, OUTDIR, ARGS):
    """
    Description
    -----------
    Performs the following checks before any operation:
    - INDIR is a string
    - FUNCTION is a function
    - ARGUMENTS is a list
    - "ouput" is in the current working directory
    - OUTDIR is already in "dat"
    - a report already exists
    
    //!\\ Attention: after this function is executed, the current working directory is "ouput". 
    """
    # CHECK INPUT TYPES AND NAMES
    if type(INDIR) != str:
        print("ERROR: The INDIR argument is not a string: {0}".format(INDIR))
        sys.exit(0)
    if not callable(FUNCTION):
        print("ERROR: The FUNCTION argument is not callable: {0}".format(FUNCTION))
        sys.exit(0)
    if type(ARGS) != list:
        print("ERROR: The ARGUMENTS argument is not a list: {0}".format(type(ARGS)))
        sys.exit(0)
    
    # CHECK "dat" DIRECTORY
    pardir = os.getcwd()
    lstdir = os.listdir(pardir)
    if "dat" not in lstdir:
        print("ERROR: The 'dat' directory is not in the current working directory: {0}\n".format(pardir))
        sys.exit(0)
        
    # CHECK "INDIR" in "dat"
    os.chdir("dat") # changes working directory to "dat"
    
    pardir = os.getcwd()
    lstdir = os.listdir(pardir)
    if "/" not in INDIR:
        if INDIR not in lstdir:
            print("ERROR: The INDIR directory is not in the 'dat' directory: {0}\n".format(INDIR))
            os.chdir("..") # sets cwd to folder outside "dat"
            sys.exit(0)
    else:
        INDIR_folders = INDIR.split("/")
        pardir_folders = pardir
        for f in INDIR_folders:
            lstdir = os.listdir(pardir_folders)
            if f not in lstdir:
                print("ERROR: The INDIR directory is not in the 'dat' directory: {0}\n".format(f))
                os.chdir("..") # sets cwd to folder outside "dat"
                sys.exit(0)
            pardir_folders += "/" + f
    
    # CHECK IF DAT DIRECTORY EXISTS
    name = names(FUNCTION = FUNCTION, OUTDIR = OUTDIR)
    outname = name.outdir
    if type(outname)==str and outname in lstdir:
        answer = input("WARNING: There is already an output directory with name: {0}\nDo you want to continue? [Y/n] ".format(outname))
        if answer in ["", "n"]:
            os.chdir("..") # sets cwd to folder outside "dat"
            sys.exit(0)
        elif answer == "Y":
            shutil.rmtree(outname)
        else:
            print("ERROR: The answer is not Y/N/none")
            os.chdir("..") # sets cwd to folder outside "dat"
            sys.exit(0)
    if type(outname)==list:
        for i in outname:
            if i in lstdir:
                answer = input("WARNING: There is already an output directory with name: {0}\nDo you want to continue? [Y/n] ".format(i))
                if answer in ["", "n"]:
                    os.chdir("..") # sets cwd to folder outside "dat"
                    sys.exit(0)
                elif answer == "Y":
                    shutil.rmtree(i)
                else:
                    print("ERROR: The answer is not Y/N/none \n")
                    os.chdir("..") # sets cwd to folder outside "dat"
                    sys.exit(0)
            
    # CHECKS IF REPORT ALREADY EXISTS
    report = name.report
    if type(report)==str and report in lstdir:
        answer = input("WARNING: There is already a report file with name: {0}\nDo you want to continue? [Y/n] ".format(report))
        if answer in ["", "n"]:
            os.chdir("..") # sets cwd to folder outside "dat"
            sys.exit(0)
        elif answer == "Y":
            os.remove(report) 
        else:
            print("ERROR: The answer is not Y/N/none")
            os.chdir("..") # sets cwd to folder outside "dat"
            sys.exit(0)
    if type(report)==list:
        for i in report:
            if i in lstdir:
                answer = input("WARNING: The already is an report file with name: {0}\nDo you want to continue? [Y/n] ".format(i))
                if answer in ["", "n"]:
                    os.chdir("..") # sets cwd to folder outside "dat"
                    sys.exit(0)
                elif answer == "Y":
                    os.remove(i) 
                else:
                    print("ERROR: The answer is not Y/N/none")
                    os.chdir("..") # sets cwd to folder outside "dat"
                    sys.exit(0)

    return

class TREE():
    """
    Description
    -----------
    Class that contains the subfolders of the current working folder, such that
    TREE.directories[i] = all folders in TREE.directories[i-1][0] . 
    
    TREE.path() returns the path from the folder which it was iniciallized. 
    //!\\ It always ends with "/" if there are still folders whose file have not been calculated. 
    
    """
    def __init__(self, inlist=[]):
        self.directories = [inlist]
        self.clean()
    def add(self, inlist):
        self.directories += [inlist]
        self.clean() # if the added list is empty this means there are no more folders inside
    def clean(self):
        while len(self.directories)>0 and self.directories[-1] == []: # if len = 0, it is impossible to access element -1
            del self.directories[-1] # deletes whole line, which is []
            if len(self.directories)>0: # just in case there is no previous element to delete
                del self.directories[-1][0] # in case the resoult is only [] (previous step is done to [[]])
    def path(self):
        s = ""
        for i in self.directories:
            s += i[0] + "/"
        return s # returns path + "/" in the end, if directories is empty returns ""

def get_time(t0 = "0", t1 = "0"):
    """
    Description
    -----------
    If this function is called without arguments, it returns current time and stores it in a temporary file. 
    If this function is called with two arguments, it returns the time interval (in seconds) of both arguments in seconds and deletes temporary file. 
    Time format (str): YYYY-MM-DD HH-MM-SS.6f
    """
    if t0 == "0" and t1 == "0":
        f = open("TEMPORARY.txt", "a")
        f.write(str(datetime.datetime.now()) + "\n")
        f.close()
        return str(datetime.datetime.now())
    else:
        start = str(t0).split(" ")[1].split(":") # ["hours", "minutes", "seconds.miliseconds"]
        start = int(start[0])*3600 + int(start[1])*60 + float(start[2])
        finish = str(t1).split(" ")[1].split(":") # ["hours", "minutes", "seconds.miliseconds"]
        finish = int(finish[0])*3600 + int(finish[1])*60 + float(finish[2])
        duration = finish - start # seconds
        os.remove("TEMPORARY.txt")
        return duration

class names():
    """
    Description
    -----------
    Sets the name for: outdir and report.
    """
    def __init__(self, FUNCTION = functionexample, OUTDIR = ""):
        if OUTDIR == "":
            self.outdir = False
            self.report = "report_" + FUNCTION.__name__ + ".txt"
        elif type(OUTDIR) == str:
            self.outdir = OUTDIR
            self.report = "report_" + OUTDIR + ".txt"
        elif type(OUTDIR) == list:
            self.outdir = OUTDIR
            s = ""
            for i in OUTDIR:
                s += i + "-"
            s = s[:-1] #deletes last "-"
            self.report = "report_" + s + ".txt"
        else:
            print("ERROR: The OUTDIR is not a str nor a list of str: {0}".format(str(OUTDIR)))
            sys.exit(0)

def makeDIR(directories, OUTDIR, FUNCTION, path=""):
    """
    Description
    -----------
    Creates list of directories in names.outdir/path (see class 'names')
    """
    name = names(FUNCTION=FUNCTION, OUTDIR=OUTDIR)
    if name.outdir == False:
        return
    elif type(name.outdir) == str:
        for diri in directories:
            os.mkdir(name.outdir + "/" + path + diri)
    else:
        for outdir in name.outdir:
            for diri in directories:
                os.mkdir(outdir + "/" + path + diri)
    
    return
    
def countINDIR(INDIR):
    """
    Description
    -----------
    Returns list = [0, total number of files in INDIR]. 
    """
    n_files = sum([len(files) for r, d, files in os.walk(INDIR)])
    counting = [0, n_files] # [number of processed files, total number of files]    

    return counting
   
def get_elements(INDIR, path):
    """
    Description
    -----------
    Returns list of fiels and directories in INDIR/path. 
    """  
    files = [f for f in os.listdir(INDIR + "/" + path) if os.path.isfile(os.path.join(INDIR + "/" + path, f))]
    directories = [f for f in os.listdir(INDIR + "/" + path) if os.path.isdir(os.path.join(INDIR + "/" + path, f))]
    
    return sorted(files), sorted(directories)
    
def write_report(INDIR, FUNCTION, OUTDIR, ARGS, intranet, GET_ELEMENTS, duration):
    """
    Description
    -----------
    Writes the report of the execution of FUNCTION in a file.
    If intranet is:
    * empty list : does not create a report file
    * str : writes in report this string
    * list : saves the values of this list in report file      
    """
    if type(intranet) == str:
        report = intranet
    elif len(intranet) == 0:
        return
    else:
        report = "Intranet      : \n"
        for i in intranet:
            report += str(i) + "\n"
        report += "\nArguments    : "
        for i in ARGS:
            report += str(i) + " "
        report += "\nDuration (s) : {0:0.2f}".format(duration)
    
    name = names(FUNCTION = FUNCTION, OUTDIR = OUTDIR).report
    f = open(name, "w")
    f.write(report)
    f.close()
        
    return
    
def write_HISTORY(INDIR, FUNCTION, OUTDIR, ARGS, PREFUNCT, POSTFUNCT, GET_ELEMENTS, duration):
    """
    Description
    -----------
    Writes in "HISTORY.txt" the report of the execution of FUNCTION. 
    """
    report = "INDIR        : " + INDIR
    report += "\nFUNCTION     : " + FUNCTION.__name__
    if OUTDIR == "":
        report += "\nOUTDIR       : -"
    elif type(OUTDIR)==str:
        report += "\nOUTDIR       : " + OUTDIR
    else:
        report += "\nOUTDIR       : "
        for i in OUTDIR:
            report += i + ", "
        report[:-2]
    report += "\nARGUMENTS    : "
    for i in ARGS:
        report += str(i) + " "
    if PREFUNCT.__name__ != "prefunct":
        report += "\nPREFUNCTION  : " + PREFUNCT.__name__
    if POSTFUNCT.__name__ != "postfunct":
        report += "\nPOSTFUNCTION : " + POSTFUNCT.__name__
    if GET_ELEMENTS.__name__ != "get_elements":
        report += "\nGET_ELEMENTS : " + GET_ELEMENTS.__name__
    report += "\nDuration (s) : {0:0.2f}\n \n".format(duration)
        
    f = open("HISTORY.txt", "a")
    f.write(report)
    f.close()
    
    return 
    
###############################################################################
#                               MAIN FUNCTION                                 #
###############################################################################

def database(INDIR, FUNCTION, OUTDIR="", ARGS = [], 
             PREFUNCT = prefunct, POSTFUNCT = postfunct, 
             GET_ELEMENTS = get_elements, WRITE_REPORT = write_report):
    """
    Description
    -----------
    Given an input directory (INDIR):
    1) performs 'PREFUNCT'
    2) performs 'FUNCTION' to the files given by 'GET_ELEMENTS'. 
    3) performs 'POSTFUNCT'
    4) writes the report of the results with 'WRITE_REPORT'
    5) writes the report of this execution in HISTORY.txt
    """

    # PREVIOUS CHECKS
    # ---------------
    check(INDIR, FUNCTION, OUTDIR, ARGS) 
    # /!\ changes current directory to "dat" /!\
    
    # PREVIOUS OPERATIONS
    # -------------------
    # timer
    t0 = get_time()
    # OUTDIR
    name = names(FUNCTION=FUNCTION, OUTDIR=OUTDIR)
    if type(name.outdir) == str:
        os.mkdir(name.outdir)
    if type(name.outdir) == list:
        for i in name.outdir:
            os.mkdir(i)
    
    # PREFUNCT and intranet
    intranet = PREFUNCT(INDIR, FUNCTION, OUTDIR, ARGS)
    if intranet is None:
        intranet = []
        
    # counting
    counting = countINDIR(INDIR)

    # tree
    tree = TREE()

    # CALCULATE ALL FILES
    # -------------------
    while True:  
    # do
        # path
        path = tree.path()
        print("----------------------------- " + path + "\r", end="")
        files, directories = GET_ELEMENTS(INDIR, path)
        
        # files
        for fname in files:
            counting[0] += 1
            print("[{0:{2}}/{1:{2}}] ".format(*counting, int(np.log10(counting[1])) + 1) + fname + " "*20 + "\r", end="")
            intranet = FUNCTION(INDIR, path, fname, OUTDIR, ARGS, intranet)
            
        # directories
        makeDIR(directories, OUTDIR, FUNCTION, path)
        tree.add(directories)
        
    # while
        if tree.path() == "":
            break

    # AFTER OPERATIONS
    # ----------------
    intranet = POSTFUNCT(INDIR, FUNCTION, OUTDIR, ARGS, intranet)
    
    # DURATION
    # --------
    t1 = get_time()
    duration = get_time(t0, t1) # seconds
    print("Duration (s) = {0:0.2f}".format(duration) + " "*50)  

    # REPORT
    # ------
    WRITE_REPORT(INDIR, FUNCTION, OUTDIR, ARGS, intranet, GET_ELEMENTS, duration)
    write_HISTORY(INDIR, FUNCTION, OUTDIR, ARGS, PREFUNCT, POSTFUNCT, GET_ELEMENTS, duration)
    
    os.chdir("..") # sets cwd to original directory
    
    return