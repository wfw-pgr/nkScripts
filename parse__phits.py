import os, sys, re
import numpy as np

# ========================================================= #
# ===  parse__phits.py                                  === #
# ========================================================= #

def parse__phits( inpFile=None, \
                  searchList=[ "xmin","xmax","ymin","ymax","zmin","zmax","nx","ny","nz","hc"] ):

    # ------------------------------------------------- #
    # --- [1] preparation                           --- #
    # ------------------------------------------------- #
    ret      = {}
    with open( inpFile, 'r' ) as f:
        contents = f.readlines()
    
    # ------------------------------------------------- #
    # --- [2] search query                          --- #
    # ------------------------------------------------- #
    for word in searchList:
        query = r"\s*{0}\s*=\s*(.*?)\s*(#.*)?$".format( word )
        for line in contents:
            match = re.match( query, line )
            if ( match ):
                ret[word] = match.group(1)
                break

    # ------------------------------------------------- #
    # --- [3] histogram color                       --- #
    # ------------------------------------------------- #
    if ( "hc" in searchList ):
        pack  = []
        query = r"\s*hc:\s*y\s*=.*to.*by.*;.*x\s*=.*to.*by.*;\s*"
        for ik,line in enumerate(contents):
            match = re.match( query, line )
            if ( match ):
                istart = ik + 1
                break
        lines = contents[istart:]
        stack = []
        for ik,line in enumerate(lines):
            if ( len( line.strip() ) == 0 ):
                break
            else:
                stack += [ float(val) for val in ( line.strip() ).split() ]
        hc_values = np.array( stack )
        ret["hc"] = hc_values
    return( ret )


# ========================================================= #
# ===   Execution of Pragram                            === #
# ========================================================= #

if ( __name__=="__main__" ):

    inpFile    = "dat/tally.dat"
    searchList = [ "xmin", "ymin", "hc" ]
    
    ret        = parse__phits( inpFile=inpFile )
    print( ret )

