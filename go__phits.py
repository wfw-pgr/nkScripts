#!/usr/local/bin/python3.10

import os, sys, subprocess, time, argparse
import datetime                              as dt
import nkScripts.materials__fromJSON         as mfj
import nkUtilities.show__section             as sct
import nkUtilities.precompile__parameterFile as ppf
import nkUtilities.command__postProcess      as cpp

# ========================================================= #
# ===  go__phits.py                                     === #
# ========================================================= #

def go__phits():

    default_settings = {
        "phits_win":r"C:\phits\bin\phitsSend2.bat", # install path of PHITS code. ( Windows )
        "phits_lin":r"phits.sh",                    # install path of PHITS code. ( Linux, mac )
    }
    
    # ------------------------------------------------- #
    # --- [1] arguments                             --- #
    # ------------------------------------------------- #
    parser = argparse.ArgumentParser(description="PHITS driver program.")
    parser.add_argument( "inpFile"             , help="PHITS's input file path." )
    parser.add_argument( "--phits_win"         , help="PHITS's path in windows." )
    parser.add_argument( "--phits_lin"         , help="PHITS's path in linux."   )
    parser.add_argument( "--materialFile"         , help="materials database file." )
    parser.add_argument( "-c", "--compile_mode", help="pre-compile input file, no execution", \
                         action="store_true" )
    args          = parser.parse_args()
    inpFile       = args.inpFile
    materialFile  = args.materialFile
    sct.show__section( "Conversion :: _phits.inp >> .inp File", length=71 )
    
    # ------------------------------------------------- #
    # --- [2] configure settings                    --- #
    # ------------------------------------------------- #
    #  -- [2-1]  path designation                   --  #
    if ( args.phits_win is not None ):
        default_settings["phits_win"] = args.phits_win
    if ( args.phits_lin is not None ):
        default_settings["phits_lin"] = args.phits_lin

    #  -- [2-2]  directory & execution File path    --  #
    dirpath = os.path.dirname( os.path.abspath( inpFile ) )
    exeFile = os.path.join( dirpath, "execute_phits.inp"  )
        
    #  -- [2-3]  PHITS execute command              --  #
    if   ( os.name == "nt"     ):            # nt    => windows
        touch_cmd = "touch {}".format( exeFile )
        ret       = subprocess.run( cmd.split(), shell=True )
        wpath_cmd = "wslpath -w {}".format( exeFile )
        ret       = subprocess.run( cmd.split(), stdout=subprocess.PIPE )
        exeFile_  = ( ret.stdout.decode() ).strip()
        phits_cmd = 'cmd.exe /c "{0} {1}"'.format( default_settings["phits_win"], exeFile_ )
    elif ( os.name == "posix"  ):            # posix => linux, mac
        phits_cmd = "{0} {1}".format( default_settings["phits_lin"], exeFile )
        
    # ------------------------------------------------- #
    # --- [3] file existence check                  --- #
    # ------------------------------------------------- #
    if ( os.path.exists( inpFile ) is False ):
        print( "\n" + "[go__phits.py] Can't Find input file... :: {}\n".format( inpFile ) )
        sys.exit( "[ ERROR -- stop ]" )
    if ( materialFile is not None ):
        if ( os.path.exists( materialFile ) is False ):
            print( "\n[go__phits.py] Can't Find material file... :: {}\n".format(materialFile) )
            sys.exit( "[ ERROR -- stop ]" )

    # ------------------------------------------------- #
    # --- [4] convert material database File        --- #
    # ------------------------------------------------- #
    if ( materialFile is not None ):
        mfj.materials__fromJSON( inpFile=materialFile )
        
    # ------------------------------------------------- #
    # --- [5] precompile parameterFile              --- #
    # ------------------------------------------------- #
    precomp = ppf.precompile__parameterFile( inpFile=inpFile, outFile=exeFile, silent=True, \
                                             comment_mark="$", variable_mark="@" )
    if ( args.compile_mode ):
        return( precomp )

    # ------------------------------------------------- #
    # --- [6] execute PHITS command                 --- #
    # ------------------------------------------------- #
    sct.show__section( "PHITS calculation Begin", length=71 )
    stime   = time.time()
    ret     = subprocess.run( phits_cmd, shell=True )
    etime   = time.time()
    elapsed = etime - stime
    hms     = dt.datetime.strftime( dt.datetime.utcfromtimestamp( elapsed ),'%H:%M:%S' )
    print( "\n" + "[go__phits.py] elapsed time :: {} ".format( hms ) + "\n" )
    
    # ------------------------------------------------- #
    # --- [7] execute postProcess command           --- #
    # ------------------------------------------------- #
    ret     = cpp.command__postProcess( inpFile=exeFile, comment_mark="$" )
    return()


# ========================================================= #
# ===   Execution of Pragram                            === #
# ========================================================= #

if ( __name__=="__main__" ):
    go__phits()
