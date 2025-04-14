import invoke
import os, sys, subprocess, time
import datetime                              as dt
import nkUtilities.show__section             as sct
import nkUtilities.precompile__parameterFile as ppf
import nkUtilities.command__postProcess      as cpp
import nkScripts.materials__fromJSON         as mfj


# ========================================================= #
# ===  build PHITS input files                          === #
# ========================================================= #
@invoke.task
def build( ctx, inpFile="inp/main_phits.inp", materialFile="inp/materials.json", \
           exeFile="inp/execute_phits.inp" ):
    # ------------------------------------------------- #
    # --- [1] file existence check                  --- #
    # ------------------------------------------------- #
    if ( os.path.exists( inpFile ) is False ):
        print( "\n" + "[tasks.py] Can't Find input file... :: {}\n".format( inpFile ) )
        sys.exit( "[ ERROR -- stop ]" )
    if ( os.path.exists( materialFile ) is False ):
        print( "\n[tasks.py] Can't Find material file... :: {}\n".format(materialFile) )
        sys.exit( "[ ERROR -- stop ]" )
    # ------------------------------------------------- #
    # --- [2] precompile PHITS input files          --- #
    # ------------------------------------------------- #
    sct.show__section( "Conversion :: _phits.inp >> .inp File", length=71 )
    material_dn = mfj.materials__fromJSON( inpFile=materialFile )
    precomp = ppf.precompile__parameterFile( inpFile=inpFile, outFile=exeFile, \
                                             table=material_dn, silent=True, \
                                             comment_mark="$",  variable_mark="@" )

    
# ========================================================= #
# ===  run PHITS calculation                            === #
# ========================================================= #
@invoke.task
def run( ctx, phits_cmd="phits.sh", exeFile="inp/execute_phits.inp" ):
    # ------------------------------------------------- #
    # --- [1] run command                           --- #
    # ------------------------------------------------- #
    phits_cmd = "{0} {1}".format( phits_cmd, exeFile )
    print( "\nrun command :: {}\n".format( phits_cmd ) )
    # ------------------------------------------------- #
    # --- [2] run PHITS calculation                 --- #
    # ------------------------------------------------- #
    sct.show__section( "PHITS calculation Begin", length=71 )
    stime   = time.time()
    ret     = subprocess.run( phits_cmd, shell=True )
    etime   = time.time()
    elapsed = etime - stime
    hms     = dt.datetime.strftime( dt.datetime.utcfromtimestamp( elapsed ),'%H:%M:%S' )
    print( "\n" + "[tasks.py] elapsed time :: {} ".format( hms ) + "\n" )

    
# ========================================================= #
# ===  post-process of the calculation                  === #
# ========================================================= #
@invoke.task
def post( ctx ):
    # ------------------------------------------------- #
    # --- [1] post execution commands               --- #
    # ------------------------------------------------- #
    command1 = "for f in `ls out/*.eps`; do gs -dSAFER -dEPSCrop "\
        "-sDEVICE=pdfwrite -o ${f%.eps}_%d.pdf ${f};done"
    command2 = "mogrify -background white -alpha off -density 400 "\
        "-resize 50%x50% -path png -format png out/*.pdf"
    subprocess.run( command1, shell=True )
    subprocess.run( command2, shell=True )
    return()
    


# ========================================================= #
# ===  build run post-process :: phits calculation      === #
# ========================================================= #
@invoke.task
def all( ctx, inpFile="inp/main_phits.inp", materialFile="inp/materials.json",\
         exeFile="inp/execute_phits.inp", phits_cmd="phits.sh" ):
    build( ctx, inpFile=inpFile, materialFile=materialFile, exeFile=exeFile )
    run  ( ctx, phits_cmd=phits_cmd, exeFile=exeFile )
    post ( ctx )
    return()
