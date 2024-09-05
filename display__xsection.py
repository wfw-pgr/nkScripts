import os,sys,re,json5,glob
import numpy                      as np
import nkUtilities.load__config   as lcf
import nkUtilities.plot1D         as pl1
import nkUtilities.configSettings as cfs

# ========================================================= #
# ===  display__xsection                                === #
# ========================================================= #
def display__xsection( jsonFile="dat/xs_list.json", labels=None ):

    en_, xs_   = 0, 1
    eV2MeV     = 1.0e-6
    b2mb       = 1.0e+3
    JENDL_expr = "JENDL.*"

    # ------------------------------------------------- #
    # --- [1] load configuration file               --- #
    # ------------------------------------------------- #
    with open( jsonFile, "r" ) as f:
        params = json5.load( f )

    # ------------------------------------------------- #
    # --- [2] ( glob mode ) search files            --- #
    # ------------------------------------------------- #
    if ( params["general.fileMode"].lower() == "glob" ):
        
        if ( not( os.path.exists( params["general.xsdir"] ) ) ):
            print( "[display__xsection.py] xsdir does NOT exist.. :: {}"\
                   .format( params["general.xsdir"] ) )
            sys.exit()
        query    = os.path.join( params["general.xsdir"], params["general.basename"] )
        xsFiles  = glob.glob( query )
        if ( len( xsFiles ) == 0 ):
            print( "[display__xsection.py] No File exists...  ( query == {} )".format( query ) )
            sys.exit()

        if ( labels is None ):
            labels   = [ ( os.path.splitext( os.path.basename( xsFile ) )[0] )\
                         .replace( "xs__", "" ) for xsFile in xsFiles ]
            sources  = [ label.split( "_" )[0]                  for label  in labels  ]
            JENDL_TF = [ bool( re.match( JENDL_expr, source ) ) for source in sources ]

    # ------------------------------------------------- #
    # --- [3] ( json mode ) given in json file      --- #
    # ------------------------------------------------- #
    if ( params["general.fileMode"].lower() == "json" ):

        if ( params["general.usekeys"] is not None ):
            xsKeys   = params["general.usekeys"]
        else:
            xsExpr   = "xs\..+"
            xsKeys   = [ key for key in params.keys() if re.match( xsExpr, key ) ]
        xsFiles  = [ params[key]["filename"] for key in xsKeys ]
        labels   = [ params[key]["label"]    for key in xsKeys ]
        JENDL_TF = [ bool( re.match( JENDL_expr, params[key]["source"] ) ) for key in xsKeys ]

    # ------------------------------------------------- #
    # --- [4] Fetch Data                            --- #
    # ------------------------------------------------- #
    import nkUtilities.load__pointFile as lpf
    xsList = [ lpf.load__pointFile( inpFile=xsFile, returnType="point" ) for xsFile in xsFiles ]
    for ik,xsD in enumerate(xsList):
        if ( JENDL_TF[ik] ):
            xsD[:,en_] = xsD[:,en_] * eV2MeV
            xsD[:,xs_] = xsD[:,xs_] * b2mb
                
    # ------------------------------------------------- #
    # --- [5] config Settings                       --- #
    # ------------------------------------------------- #
    config                   = lcf.load__config()
    config                   = cfs.configSettings( configType="plot.def", config=config )
    config["FigSize"]        = (4.5,4.5)
    config["plt_position"]   = [ 0.16, 0.16, 0.94, 0.94 ]
    config["plt_marker"]     = "o"
    config["plt_markersize"] = 3.0
    config["plt_linestyle"]  = "-"
    config["plt_linewidth"]  = 2.0
    config["xTitle"]         = "Energy (MeV)"
    config["yTitle"]         = "Cross-section (mb)"
    config["plt_xAutoRange"] = params["plot.xAutoRange"]
    config["plt_yAutoRange"] = params["plot.yAutoRange"]
    config["plt_xRange"]     = params["plot.xRange"]
    config["plt_yRange"]     = params["plot.yRange"]
    config["leg_FontSize"]   = params["plot.legend.fontsize"]
    config["xMajor_Nticks"]  = params["plot.xMajor_Nticks"]
    config["yMajor_Nticks"]  = params["plot.yMajor_Nticks"]

    
    # ------------------------------------------------- #
    # --- [6] plot Figure                           --- #
    # ------------------------------------------------- #
    fig     = pl1.plot1D( config=config, pngFile=params["general.pngFile"] )
    for ik,xsD in enumerate(xsList):
        # fig.add__plot( xAxis=xsD[:,en_], yAxis=xsD[:,xs_], label=labels[ik] )
        fig.add__plot( xAxis=xsD[:,en_], yAxis=xsD[:,xs_], label=labels[ik], linestyle="--" )


    fig.add__legend()
    fig.set__axis()
    fig.save__figure()


# ======================================== #
# ===  実行部                          === #
# ======================================== #
if ( __name__=="__main__" ):
    display__xsection()

