import numpy  as np
import pandas as pd
import os, sys, json

# ========================================================= #
# ===  materials__fromCSV                               === #
# ========================================================= #

def materials__fromCSV( inpFile=None ):

    # ------------------------------------------------- #
    # --- [1] arguments                             --- #
    # ------------------------------------------------- #
    if ( inpFile is None ): sys.exit( "[materials__fromCSV.py] inpFile == ???" )

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
    jsonFile = "dat/material.json"
    with open( jsonFile, "w" ) as f:
        json.dump( materials, f, indent=2 )
    
    # ------------------------------------------------- #
    # --- [5] format as a material_phits.inp        --- #
    # ------------------------------------------------- #
    outFile = "dat/material_phits.inp"
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
    pageTitle = show__section( section="material_phits.inp (PHITS)", \
                               bar_mark="=", comment_mark="$$" )
    matTitle  = show__section( section="material section (PHITS)", \
                               bar_mark="-", comment_mark="$$" )
    block1    = pageTitle + matTitle
    for key in keys:
        item    = materials[key]
        title   = "matNum[{0}] :: {1}".format( item["MaterialNumber"], item["Name"] )
        section = show__section( section=title, bar_mark="-", comment_mark="$$" )
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
                              bar_mark="-", comment_mark="$$" )
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
# ===  show__section                                    === #
# ========================================================= #

def show__section( section=None, length=71, bar_mark="-", comment_mark="#", \
                   sidebarLen=3, sideSpaceLen=1, newLine=True ):

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
    return( lines )

        

# ========================================================= #
# ===   Execution of Pragram                            === #
# ========================================================= #

if ( __name__=="__main__" ):
    inpFile = "dat/materials.csv"
    materials__fromCSV( inpFile=inpFile )
