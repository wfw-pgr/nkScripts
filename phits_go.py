#!/usr/bin/env python3

import os, sys, subprocess, re

# ------------------------------------------------------------------- #
# --    start-driver command for PHTIS simulation code ( JAEA )    -- #
# --    assume WSL environment in windows system.                  -- #
# ------------------------------------------------------------------- #

# ========================================================= #
# ===  phits_go.py                                      === #
# ========================================================= #

def phits_go():

    phits_core = r"C:\phits\bin\phitsSend2.bat" # install path of PHITS code. ( Windows-path )
    
    # ------------------------------------------------- #
    # --- [1] parameters to input                   --- #
    # ------------------------------------------------- #
    if ( not( len( sys.argv ) == 2 ) ):
        print( "\n" + "[phits_go.py] [USAGE]  phits_go.py < input file name (*_phits.inp) > " + "\n" )
        sys.exit( "[STOP]" )
    else:
        refFile = sys.argv[1]

    # ------------------------------------------------- #
    # --- [2] file existence check                  --- #
    # ------------------------------------------------- #
    if ( os.path.exists( refFile ) ):
        pass
    else:
        print( "\n" + "[phits_go.py] Can't Find input file... :: {}".format( refFile ) + "\n" )
        sys.exit( "[STOP]" )

    # ------------------------------------------------- #
    # --- [3] replace variable expressions          --- #
    # ------------------------------------------------- #
    inpFile = refFile.replace( "_phits.inp", "_phits_exec.inp" )
    replace__variableDefinition( inpFile=refFile, outFile=inpFile, replace_expression=True, \
                                 comment_mark="$", define_mark="<define>", variable_mark="@" )
    
    # ------------------------------------------------- #
    # --- [4] interpret file path into Windows one  --- #
    # ------------------------------------------------- #
    cmd      = "wslpath -w {}".format( inpFile )
    ret      = subprocess.run( cmd.split(), stdout=subprocess.PIPE )
    inpFile  = ( ret.stdout.decode() ).strip()

    # ------------------------------------------------- #
    # --- [5] execute PHITS command                 --- #
    # ------------------------------------------------- #
    phits_cmd = 'cmd.exe /c "{0} {1}"'.format( phits_core, inpFile )
    subprocess.run( phits_cmd, shell=True )


# ========================================================= #
# ===   Execution of Pragram                            === #
# ========================================================= #

if ( __name__=="__main__" ):
    phits_go()





# ========================================================= #
# ========================================================= #
# ===
# ===  utility functions                                === #
# ===
# ========================================================= #
# ========================================================= #


# ========================================================= #
# ===  resolve__typeOfString.py                         === #
# ========================================================= #

def resolve__typeOfString( word=None, priority=["None","int","float","logical",\
                                                "intarr","fltarr","strarr", "string"] ):

    # ------------------------------------------------- #
    # --- [1] arguments check                       --- #
    # ------------------------------------------------- #
    if ( word is None ):
        sys.exit( "[resolve__typeOfString.py] word == ??? :: word is None [ERROR] " )
    if ( len( priority ) == 0 ):
        sys.exit( "[resolve__typeOfString.py] priority == ??? [ERROR] " )

    # ------------------------------------------------- #
    # --- [2] for each priority word                --- #
    # ------------------------------------------------- #
    ret = None
    for prior in priority:

        # ------------------------------------------------- #
        # --- [2-1] None type                           --- #
        # ------------------------------------------------- #
        if ( prior == "None" ):
            if ( word.lower() == "none" ):
                ret = None
                break
        # ------------------------------------------------- #
        # --- [2-2] integer type                        --- #
        # ------------------------------------------------- #
        if ( prior == "int" ):
            if ( word.isdecimal() ):
                ret = int( word )
                break
        # ------------------------------------------------- #
        # --- [2-3] float type                          --- #
        # ------------------------------------------------- #
        if ( prior == "float" ):
            flag = False
            try:
                ret  = float( word )
                flag = True
            except ValueError:
                pass
            if ( flag ): break
        # ------------------------------------------------- #
        # --- [2-4] logical type                        --- #
        # ------------------------------------------------- #
        if ( prior == "logical" ):
            if ( word.lower() in [ "true", "t" ] ):
                ret  = True
                break
            if ( word.lower() in [ "false", "f" ] ):
                ret  = False
                break
        # ------------------------------------------------- #
        # --- [2-5] fltarr type                         --- #
        # ------------------------------------------------- #
        if ( prior == "fltarr" ):
            pattern      = r"\[(.*)\]"
            ret          = re.search( pattern, word )
            failed       = False
            if ( ret is not None ):
                arrcontent   = ( ret.group(1) ).split(",")
                lst          = []
                for s in arrcontent:
                    try:
                        lst   += [ float( s ) ]
                    except ValueError:
                        failed = True
                        break
            else:
                failed = True
            if ( failed ):
                pass
            else:
                ret = lst
                break
        # ------------------------------------------------- #
        # --- [2-6] intarr type                         --- #
        # ------------------------------------------------- #
        if ( prior == "intarr" ):
            pattern      = r"\[(.*)\]"
            ret          = re.search( pattern, word )
            failed       = False
            if ( ret is not None ):
                arrcontent   = ( ret.group(1) ).split(",")
                lst          = []
                for s in arrcontent:
                    try:
                        lst   += [ int( s ) ]
                    except ValueError:
                        failed = True
                        break
            else:
                failed = True
            if ( failed ):
                pass
            else:
                ret = lst
                break
        # ------------------------------------------------- #
        # --- [2-7] strarr type                         --- #
        # ------------------------------------------------- #
        if ( prior == "strarr" ):
            pattern      = r"\[(.*)\]"
            ret          = re.search( pattern, word )
            if ( ret is not None ):
                arrcontent   = ( ret.group(1) ).split(",")
                ret          = [ ( s.strip('"') ).strip( "'" ).strip() for s in arrcontent ]
                break
        # ------------------------------------------------- #
        # --- [2-7] string type                         --- #
        # ------------------------------------------------- #
        if ( prior == "string" ):
            ret = word.strip()
            break

    # ------------------------------------------------- #
    # --- [3] return value                          --- #
    # ------------------------------------------------- #
    return( ret )


# ========================================================= #
# ===  replace__variableDefinition.py                   === #
# ========================================================= #

def replace__variableDefinition( inpFile=None, lines=None, priority=None, \
                                 replace_expression=True, comment_mark="#", outFile=None, \
                                 define_mark="<define>", variable_mark="@", \
                                 escapeType ="UseEscapeSequence" ):

    # ------------------------------------------------- #
    # --- [1] Arguments                             --- #
    # ------------------------------------------------- #
    if ( lines is None ):
        if ( inpFile is None ):
            sys.exit( "[replace__variableDefinition.py] lines, inpFile == ???? [ERROR] " )
        else:
            with open( inpFile, "r" ) as f:
                lines = f.readlines()
    if ( type( lines ) is str ):
        lines = [ lines ]
    if ( priority is None ):
        priority = ["None","int","float","logical","intarr","fltarr","strarr","string"]
        
    # ------------------------------------------------- #
    # --- [2] expression of definition              --- #
    # ------------------------------------------------- #
    vdict      = {}
    Flag__changeComment = False
    
    if ( comment_mark in [ "$", "*" ] ):  # --:: Need - Escape-Sequence ... ::-- #
        if   ( escapeType == "UseEscapeSequence" ):
            cmt      = "\\" + comment_mark
            expr_def = "{0}\s*{1}\s*{2}(\S*)\s*=\s*(.*)".format( cmt, define_mark, variable_mark )
            
        elif ( escapeType == "ReplaceCommentMark" ):
            original     = comment_mark
            comment_mark = "#"
            Flag__changeComment = True
            expr_def     = "{0}\s*{1}\s*{2}(\S*)\s*=\s*(.*)".format( comment_mark, define_mark,\
                                                                     variable_mark )
            for ik,line in enumerate( lines ):
                lines[ik] = ( lines[ik] ).replace( original, comment_mark )

    else:
        expr_def     = "{0}\s*{1}\s*{2}(\S*)\s*=\s*(.*)".format( comment_mark, define_mark, \
                                                                 variable_mark ) 

        
    # ------------------------------------------------- #
    # --- [3] parse variables                       --- #
    # ------------------------------------------------- #
    
    for line in lines:   # 1-line, 1-argument.

        # ------------------------------------------------- #
        # ---     search variable notation              --- #
        # ------------------------------------------------- #
        ret = re.search( expr_def, line )
        if ( ret ):      # Found.

            # ------------------------------------------------- #
            # --- [3-1] Definition of the variable          --- #
            # ------------------------------------------------- #
            vname        = "@"+ret.group(1)
            if ( comment_mark in ret.group(2) ):
                value = ( ( ( ret.group(2) ).split(comment_mark) )[0] ).strip()
            else:
                value = ( ret.group(2) ).strip()
            # ------------------------------------------------- #
            # --- [3-2] replace variables in value          --- #
            # ------------------------------------------------- #
            for hname in list( vdict.keys() ):
                ret = re.search( hname, value )
                if ( ret ):
                    if   ( type( vdict[hname] ) in [int,float,bool] ):
                        hvalue = "{0}".format( vdict[hname] )
                        value  = value.replace( hname, hvalue )
                    else:
                        sys.exit( "[replace__variableDefinition.py] variables of evaluation must be (int,float,bool). [ERROR] " )
            # ------------------------------------------------- #
            # --- [3-3] evaluation and store                --- #
            # ------------------------------------------------- #
            value        = "{0}".format( eval( value ) )
            value        = resolve__typeOfString( word=value, priority=priority )
            vdict[vname] = value

    # ------------------------------------------------- #
    # --- [4] replace expression                    --- #
    # ------------------------------------------------- #
    if ( replace_expression ):
        replaced  = []
        vnames    = list( vdict.keys() )
        for line in lines:
            hline = ( line )
            if ( len( hline.strip() ) == 0 ):
                replaced.append( hline )
                continue
            if ( ( hline.strip() )[0] == comment_mark ):
                replaced.append( hline )
                continue
            for vname in vnames:
                ret = re.search( vname, hline )
                if ( ret ):
                    if   ( type( vdict[vname] ) in [None,int,float,bool,str] ):
                        value = "{0}".format( vdict[vname] )
                    elif ( type( vdict[vname] ) in [list] ):
                        value = "[" + ",".join( vdict[vname] ) + "]"
                    hline = hline.replace( vname, value.strip() )
            replaced.append( hline )
            
        if ( Flag__changeComment ):
            for ik,line in enumerate( replaced ):
                replaced[ik] = ( line.replace( comment_mark, original ) )
            
    # ------------------------------------------------- #
    # --- [5] return                                --- #
    # ------------------------------------------------- #
    if ( replace_expression ):
        if ( outFile is not None ):
            text = "".join( replaced )
            with open( outFile, "w" ) as f:
                f.write( text )
            print( "[replace__variableDefinition.py] output :: {}".format( outFile ) )
        print( "[replace__variableDefinition.py] replaced lines is returned." + "\n" )
        return( replaced )
    else:
        print( "[replace__variableDefinition.py] variables dictionary is returned. " )
        return( vdict    )




# ========================================================= #
# ========================================================= #
# ===
# ===  main routines                                    === #
# ===
# ========================================================= #
# ========================================================= #



# ========================================================= #
# ===  phits_go.py                                      === #
# ========================================================= #

def phits_go():

    phits_core = r"C:\phits\bin\phitsSend2.bat" # install path of PHITS code. ( Windows-path )
    
    # ------------------------------------------------- #
    # --- [1] parameters to input                   --- #
    # ------------------------------------------------- #
    if ( not( len( sys.argv ) == 2 ) ):
        print( "\n" + "[phits_go.py] [USAGE]  phits_go.py < input file name (*_phits.inp) > " + "\n" )
        sys.exit( "[STOP]" )
    else:
        refFile = sys.argv[1]

    # ------------------------------------------------- #
    # --- [2] file existence check                  --- #
    # ------------------------------------------------- #
    if ( os.path.exists( refFile ) ):
        pass
    else:
        print( "\n" + "[phits_go.py] Can't Find input file... :: {}".format( refFile ) + "\n" )
        sys.exit( "[STOP]" )

    # ------------------------------------------------- #
    # --- [3] replace variable expressions          --- #
    # ------------------------------------------------- #
    inpFile = refFile.replace( "_phits.inp", "_phits_exec.inp" )
    replace__variableDefinition( inpFile=refFile, outFile=inpFile, replace_expression=True, \
                                 comment_mark="$", define_mark="<define>", variable_mark="@" )
    
    # ------------------------------------------------- #
    # --- [4] interpret file path into Windows one  --- #
    # ------------------------------------------------- #
    cmd      = "wslpath -w {}".format( inpFile )
    ret      = subprocess.run( cmd.split(), stdout=subprocess.PIPE )
    inpFile  = ( ret.stdout.decode() ).strip()

    # ------------------------------------------------- #
    # --- [5] execute PHITS command                 --- #
    # ------------------------------------------------- #
    phits_cmd = 'cmd.exe /c "{0} {1}"'.format( phits_core, inpFile )
    subprocess.run( phits_cmd, shell=True )


# ========================================================= #
# ===   Execution of Pragram                            === #
# ========================================================= #

if ( __name__=="__main__" ):
    phits_go()





