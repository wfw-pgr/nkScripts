#!/usr/bin/env python3

import os, sys, subprocess, re, time, json
import datetime as dt
import pandas   as pd

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
                        print( "hname :: ", hname )
                        print( "value :: ", value )
                        sys.exit( "[replace__variableDefinition.py] variables of evaluation must be (int,float,bool). [ERROR] " )
            # ------------------------------------------------- #
            # --- [3-3] evaluation and store                --- #
            # ------------------------------------------------- #
            try:
                value    = "{0}".format( eval( value ) )
            except:
                value    = "{0}".format(       value   )
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
# ===  include__dividedFile.py                          === #
# ========================================================= #

def include__dividedFile( inpFile=None, outFile=None, lines=None, \
                          comment_mark="#", include_mark="<include>", \
                          escapeType ="UseEscapeSequence" ):

    # ------------------------------------------------- #
    # --- [1] Arguments                             --- #
    # ------------------------------------------------- #
    if ( lines is None ):
        if ( inpFile is None ):
            sys.exit( "[include__dividedFile.py] lines, inpFile == ???? [ERROR] " )
        else:
            with open( inpFile, "r" ) as f:
                lines = f.readlines()
    if ( type( lines ) is str ):
        lines = [ lines ]
        
    # ------------------------------------------------- #
    # --- [2] expression of definition              --- #
    # ------------------------------------------------- #
    vdict               = {}
    Flag__changeComment = False
    
    if ( comment_mark in [ "$", "*" ] ):  # --:: Need - Escape-Sequence ... ::-- #
        if   ( escapeType == "UseEscapeSequence" ):
            cmt      = "\\" + comment_mark
            expr_def = "{0}\s*{1}\s*filepath\s*=\s*(.*)".format( cmt, include_mark )
            
        elif ( escapeType == "ReplaceCommentMark" ):
            original     = comment_mark
            comment_mark = "#"
            Flag__changeComment = True
            expr_def     = "{0}\s*{1}\s*filepath\s*=\s*(.*)".format( comment_mark, include_mark )
            for ik,line in enumerate( lines ):
                lines[ik] = ( lines[ik] ).replace( original, comment_mark )

    else:
        expr_def     = "{0}\s*{1}\s*filepath\s*=\s*(.*)".format( comment_mark, include_mark )

        
    # ------------------------------------------------- #
    # --- [3] parse variables                       --- #
    # ------------------------------------------------- #

    stack = []
    while( True ):    # infinite loop

        # ------------------------------------------------- #
        # ---  check the contents of the lines          --- #
        # ------------------------------------------------- #
        if ( len(lines) == 0 ):
            break
        else:
            line   = lines.pop(0)
        stack += [line]
        
        # ------------------------------------------------- #
        # ---     search variable notation              --- #
        # ------------------------------------------------- #
        ret = re.search( expr_def, line )
        if ( ret ):      # Found.

            # ------------------------------------------------- #
            # --- [3-1] get file path                       --- #
            # ------------------------------------------------- #
            if ( comment_mark in ret.group(1) ):
                filepath = ( ( ( ret.group(1) ).split(comment_mark) )[0] ).strip()
            else:
                filepath = ( ret.group(1) ).strip()

            # ------------------------------------------------- #
            # --- [3-2] file existing check & load          --- #
            # ------------------------------------------------- #
            if ( os.path.exists( filepath ) ):
                with open( filepath, "r" ) as g:
                    inc = g.readlines()
                lines = inc + lines
            else:
                print( "[include__dividedFile.py] Cannot Find such a file.... [ERROR] " )
                print( "[include__dividedFile.py] filepath :: {} ".format( filepath   ) )

    # ------------------------------------------------- #
    # --- [4] return                                --- #
    # ------------------------------------------------- #
    if ( outFile is not None ):
        text = "".join( stack )
        with open( outFile, "w" ) as f:
            f.write( text )
        print( "[include__dividedFile.py] output :: {}".format( outFile ) )
    print( "[include__dividedFile.py] inserted lines is returned." + "\n" )
    return( stack )



# ========================================================= #
# ===  command__postProcess.py                          === #
# ========================================================= #

def command__postProcess( inpFile=None, lines=None, comment_mark="#", execute=True, \
                          postProcess_mark="<postProcess>", escapeType ="UseEscapeSequence" ):

    # ------------------------------------------------- #
    # --- [1] Arguments                             --- #
    # ------------------------------------------------- #
    if ( lines is None ):
        if ( inpFile is None ):
            sys.exit( "[command__postProcess.py] lines, inpFile == ???? [ERROR] " )
        else:
            with open( inpFile, "r" ) as f:
                lines = f.readlines()
    if ( type( lines ) is str ):
        lines = [ lines ]
        
    # ------------------------------------------------- #
    # --- [2] expression of definition              --- #
    # ------------------------------------------------- #
    vdict               = {}
    Flag__changeComment = False
    
    if ( comment_mark in [ "$", "*" ] ):  # --:: Need - Escape-Sequence ... ::-- #
        if   ( escapeType == "UseEscapeSequence" ):
            cmt      = "\\" + comment_mark
            expr_def = "{0}\s*{1}\s*(.*)".format( cmt, postProcess_mark )
            
        elif ( escapeType == "ReplaceCommentMark" ):
            original     = comment_mark
            comment_mark = "#"
            Flag__changeComment = True
            expr_def     = "{0}\s*{1}\s*(.*)".format( comment_mark, postProcess_mark )
            for ik,line in enumerate( lines ):
                lines[ik] = ( lines[ik] ).replace( original, comment_mark )

    else:
        expr_def     = "{0}\s*{1}\s*(.*)".format( comment_mark, postProcess_mark )

        
    # ------------------------------------------------- #
    # --- [3] parse variables                       --- #
    # ------------------------------------------------- #

    stack = []
    for ik,line in enumerate(lines):   # 1-line, 1-argument.

        # ------------------------------------------------- #
        # ---     search variable notation              --- #
        # ------------------------------------------------- #
        ret = re.search( expr_def, line )
        if ( ret ):      # Found.
            
            # ------------------------------------------------- #
            # --- [3-1] get file path                       --- #
            # ------------------------------------------------- #
            if ( comment_mark in ret.group(1) ):
                command = ( ( ( ret.group(1) ).split(comment_mark) )[0] ).strip()
            else:
                command = ( ret.group(1) ).strip()

            # ------------------------------------------------- #
            # --- [3-2] stack commands                      --- #
            # ------------------------------------------------- #
            stack += [command]

    # ------------------------------------------------- #
    # --- [4] execute & return                      --- #
    # ------------------------------------------------- #
    for command in stack:
        print( command )
        subprocess.run( command, shell=True )
    print( "[command__postProcess.py] command list is returned." + "\n" )
    return( stack )




# ========================================================= #
# ===  show__section                                    === #
# ========================================================= #

def show__section( section=None, length=71, bar_mark="-", comment_mark="#", sidebarLen=3, sideSpaceLen=1, \
                   newLine=True, silent=False ):

    # ------------------------------------------------- #
    # --- [1] arguments                             --- #
    # ------------------------------------------------- #
    if ( section is None ): sys.exit( "[show__section.py] section == ???" )

    # ------------------------------------------------- #
    # --- [2] Length determination                  --- #
    # ------------------------------------------------- #
    sectLen        = len(section)
    uprlwrbar_Len  = length - ( len( comment_mark ) + sideSpaceLen )*2
    space_t_Len    = ( length - len(section) - 2*( len( comment_mark ) + sideSpaceLen*2 + sidebarLen ) )
    space_f_Len    = space_t_Len // 2
    space_r_Len    = space_t_Len - space_f_Len

    # ------------------------------------------------- #
    # --- [3] preparation                           --- #
    # ------------------------------------------------- #
    space_f        = " "*space_f_Len
    space_r        = " "*space_r_Len
    side1          = comment_mark + " "*sideSpaceLen
    side2          = comment_mark + " "*sideSpaceLen + bar_mark*sidebarLen + " "*sideSpaceLen

    # ------------------------------------------------- #
    # --- [4] section contents                      --- #
    # ------------------------------------------------- #
    line1          = side1 + bar_mark*uprlwrbar_Len + side1[::-1] + "\n"
    line2          = side2 + space_f + section + space_r + side2[::-1] + "\n"
    if ( newLine ):
        lines = "\n" + line1 + line2 + line1 + "\n"
    if ( silent ):
        pass
    else:
        print( lines )
    return( lines )



# ========================================================= #
# ===  materials__fromCSV                               === #
# ========================================================= #

def materials__fromCSV( inpFile=None, outFile=None, jsonFile=None ):

    # ------------------------------------------------- #
    # --- [1] arguments                             --- #
    # ------------------------------------------------- #
    if ( inpFile  is None ): sys.exit( "[materials__fromCSV.py] inpFile == ???" )
    if ( outFile  is None ): outFile  = inpFile.replace( ".csv", "_phits.inp" )
    if ( jsonFile is None ): jsonFile = inpFile.replace( ".csv", ".json"      )

    # ------------------------------------------------- #
    # --- [2] read csv file                         --- #
    # ------------------------------------------------- #
    table = pd.read_csv( inpFile )
    table = table.fillna( {"CharacterSize":2.0, "Density":0.0, "Color":"Blue", "Comment":"" } )

    # ------------------------------------------------- #
    # --- [3] convert into dictionary               --- #
    # ------------------------------------------------- #
    materials = {}
    allKeys   = table.keys()
    pkeys     = [ "Name", "MaterialNumber", "Density", "CharacterSize", "Color", "Comment" ]
    nElements = len( list( set(allKeys) - set(pkeys) ) ) // 2
    for index,item in table.iterrows():
        if ( item["MaterialNumber"] > 0 ):
            matElement1 = { key:item[key] for key in pkeys }
            matElement2 = {}
            for ik in list( range( nElements ) ):
                key1 = "Atom{:02}"  .format( ik+1 )
                key2 = "Amount{:02}".format( ik+1 )
                if ( not( pd.isnull( item[key1] ) ) and ( not( pd.isnull( item[key2] ) ) ) ):
                    matElement2[item[key1]]  = item[key2]
            matElement1["Composition"]       = matElement2
            materials[ matElement1["Name"] ] = matElement1

    # ------------------------------------------------- #
    # --- [4] save contents as a .json file         --- #
    # ------------------------------------------------- #
    with open( jsonFile, "w" ) as f:
        json.dump( materials, f, indent=2 )
    
    # ------------------------------------------------- #
    # --- [5] format as a material_phits.inp        --- #
    # ------------------------------------------------- #
    ret     = save__materialFile( materials=materials, outFile=outFile )
    return()


# ========================================================= #
# ===  save__materialFile                               === #
# ========================================================= #

def save__materialFile( outFile=None, materials=None, keys=None ):

    # ------------------------------------------------- #
    # --- [1] arguments                             --- #
    # ------------------------------------------------- #
    if ( outFile   is None ): sys.exit( "[save__materialFile] outFile     == ???" )
    if ( materials is None ): sys.exit( "[save__materialFile] materials   == ???" )
    if ( keys      is None ): keys = materials.keys()
    
    # ------------------------------------------------- #
    # --- [2] make contents                         --- #
    # ------------------------------------------------- #
    pageTitle  = show__section( section="material_phits.inp (PHITS)", \
                                bar_mark="=", comment_mark="$$", silent=True )
    matTitle   = show__section( section="material section (PHITS)", \
                                bar_mark="-", comment_mark="$$", silent=True )
    matSection = "\n" + "[Material]" + "\n"
    block1     = pageTitle + matTitle + matSection
    for key in keys:
        item    = materials[key]
        title   = "matNum[{0}] :: {1}".format( item["MaterialNumber"], item["Name"] )
        section = show__section( section=title, bar_mark="-", comment_mark="$$", silent=True )
        if ( len( item["Comment"] ) > 0 ):
            comment = "$$ comment :: {}\n".format( item["Comment"] )
        else:
            comment = ""
        matNumSection = "mat[{}]\n".format( item["MaterialNumber"] )
        composition   = item["Composition"]
        composit_note = [ " "*4 + "{0:<10} {1:12.5e}\n".format(key,rate) \
                          for key,rate in composition.items() ]
        matNumDefine  = "$ <define> @{0:<25} = {1:10}\n"\
            .format( item["Name"]+".matNum" , item["MaterialNumber"] )
        DensityDefine = "$ <define> @{0:<25} = {1:10}\n"\
            .format( item["Name"]+".Density", item["Density"] )
        block1       += section + comment + matNumSection + "".join( composit_note ) + "\n"
        block1       += matNumDefine + DensityDefine + "\n"

    # ------------------------------------------------- #
    # --- [3] matNameColor section                  --- #
    # ------------------------------------------------- #
    colTitle = show__section( section="matNameColor section (PHITS)", \
                              bar_mark="-", comment_mark="$$", silent=True )
    block2   = colTitle + "\n" + "[MatNameColor]\n"
    block2  += "    {0:<4} {1:<18} {2:<10} {3:<20}\n".format("mat","name","size","color")
    for key in keys:
        item = materials[key]
        line = "    {0:<4} {1:<18} {2:<10} {3:<20}\n".format( item["MaterialNumber"],item["Name"],\
                                                              item["CharacterSize"] ,item["Color"] )
        block2 += line
    block    = block1 + "\n" + block2
        
    # ------------------------------------------------- #
    # --- [3] save in a file                        --- #
    # ------------------------------------------------- #
    with open( outFile, "w" ) as f:
        f.write( block )
    print( "[materials__fromCSV.py] outFile :: {} ".format( outFile ) )
    return( block )




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

    # ------------------------------------------------- #
    # --- [1] arguments                             --- #
    # ------------------------------------------------- #
    import argparse
    parser = argparse.ArgumentParser(description="PHITS driver program.")
    parser.add_argument("refFile"                 , help="PHITS's input file path." )
    parser.add_argument("--os"                    , help="os selection." )
    parser.add_argument("--phits_win"             , help="PHITS's path in windows." )
    parser.add_argument("--phits_lin"             , help="PHITS's path in linux."   )
    parser.add_argument("-c", "--convert_only"    , help="convert input file only", \
                        action="store_true" )
    parser.add_argument("-m", "--convert_material", help="convert material file"  , \
                        action="store_true" )
    parser.add_argument("--materialFile"          , help="convert materials File" )
    args          = parser.parse_args()
    refFile       = args.refFile
    convert_only  = args.convert_only
    flag_material = args.convert_material
    materialFile  = args.materialFile

    if ( materialFile  is not None ):
        flag_material = True
    if ( flag_material and ( materialFile is None ) ):
        materialFile  = "inp/materials.csv"

    show__section( "Conversion :: _phits.inp >> .inp File", length=71 )
    
    # ------------------------------------------------- #
    # --- [2] optional arguments                    --- #
    # ------------------------------------------------- #
    if   ( args.os is None ):
        os_system = "linux"
    elif ( args.os in ["linux","windows"] ):
        os_system = args.os
    else:
        os_system = "linux"
        
    if   ( args.phits_win is not None ):
        phits_win = args.phits_win
    else:
        phits_win = r"C:\phits\bin\phitsSend2.bat" # install path of PHITS code. ( Windows-path )

    if   ( args.phits_lin is not None ):
        phits_lin = args.phits_lin
    else:
        phits_lin = r"phits.sh"                    # install path of PHITS code. ( Windows-path )
    
    # ------------------------------------------------- #
    # --- [3] file existence check                  --- #
    # ------------------------------------------------- #
    if ( os.path.exists( refFile ) ):
        pass
    else:
        print( "\n" + "[phits_go.py] Can't Find input file... :: {}".format( refFile ) + "\n" )
        sys.exit( "[STOP]" )

    if ( flag_material ):
        if not( os.path.exists( materialFile ) ):
            print( "\n" + "[phits_go.py] Can't Find material file... :: {}"\
                   .format( materialFile ) + "\n" )
            sys.exit( "[STOP]" )

    # ------------------------------------------------- #
    # --- [4] convert material csv File             --- #
    # ------------------------------------------------- #
    if ( materialFile is not None ):
        materials__fromCSV( inpFile=materialFile )
    
    # ------------------------------------------------- #
    # --- [5] include divided files                 --- #
    # ------------------------------------------------- #
    dirpath = os.path.dirname( os.path.abspath( refFile ) )
    inpFile = os.path.join( dirpath, "execute_phits.inp"  )
    include__dividedFile( inpFile=refFile , outFile=inpFile, \
                          comment_mark="$", include_mark="<include>" )
    
    # ------------------------------------------------- #
    # --- [6] replace variable expressions          --- #
    # ------------------------------------------------- #
    replace__variableDefinition( inpFile=inpFile, outFile=inpFile, replace_expression=True, \
                                 comment_mark="$", define_mark="<define>", variable_mark="@" )
    if ( convert_only ):
        return()
    else:
        show__section( "PHITS calculation Begin", length=71 )

    
    # ------------------------------------------------- #
    # --- [6] interpret file path into Windows one  --- #
    # ------------------------------------------------- #
    if ( os_system.lower() == "windows" ):
        cmd      = "wslpath -w {}".format( inpFile )
        ret      = subprocess.run( cmd.split(), stdout=subprocess.PIPE )
        inpFile  = ( ret.stdout.decode() ).strip()

    # ------------------------------------------------- #
    # --- [7] execute PHITS command                 --- #
    # ------------------------------------------------- #
    stime = time.time()
    if   ( os_system.lower() == "windows" ):
        phits_cmd = 'cmd.exe /c "{0} {1}"'.format( phits_win, inpFile )
        subprocess.run( phits_cmd, shell=True )
        
    elif ( os_system.lower() == "linux"   ):
        phits_cmd = "{0} {1}".format( phits_lin, inpFile )
        subprocess.run( phits_cmd, shell=True )
    etime   = time.time()
    elapsed = etime - stime
    hms     = dt.datetime.strftime( dt.datetime.utcfromtimestamp( elapsed ),'%H:%M:%S' )
    print( "\n" + "[phits_go.py] elapsed time :: {} ".format( hms ) + "\n" )
    
    # ------------------------------------------------- #
    # --- [8] execute postProcess command           --- #
    # ------------------------------------------------- #
    command__postProcess( inpFile=inpFile, comment_mark="$", \
                          postProcess_mark="<postProcess>" )
    return()


# ========================================================= #
# ===   Execution of Pragram                            === #
# ========================================================= #

if ( __name__=="__main__" ):
    phits_go()
