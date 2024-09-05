import os,sys,re,json5,glob
import numpy                      as np
import nkUtilities.load__config   as lcf
import nkUtilities.plot1D         as pl1
import nkUtilities.configSettings as cfs


# ========================================================= #
# ===  display__xsection                                === #
# ========================================================= #
def display__xsection( xsdir="xs/", jsonFile="dat/ri_prod.json", pngFile="png/xsections.png", \
                       labels=None ):

    en_, xs_ = 0, 1
    eV2MeV   = 1.0e-6
    b2mb     = 1.0e+3

    # ------------------------------------------------- #
    # --- [1] Arguments                             --- #
    # ------------------------------------------------- #
    config   = lcf.load__config()
    with open( jsonFile, "r" ) as f:
        params = json5.load( f )
    xsFiles  = glob.glob( os.path.join( xsdir, "*.dat" ) )
    if ( labels is None ):
        labels   = [ ( os.path.splitext( os.path.basename( xsFile ) )[0] ).replace( "xs__", "" )
                     for xsFile in xsFiles ]
        sources  = [ label.split( "_" )[0]              for label in labels ]
        JENDL_TF = [ "JENDL" in source for source in sources ]

    # ------------------------------------------------- #
    # --- [2] Fetch Data                            --- #
    # ------------------------------------------------- #
    import nkUtilities.load__pointFile as lpf
    xsList = [ lpf.load__pointFile( inpFile=xsFile, returnType="point" ) for xsFile in xsFiles ]
    for ik,xsD in enumerate(xsList):
        if ( JENDL_TF[ik] ):
            xsD[:,en_] = xsD[:,en_] * eV2MeV
            xsD[:,xs_] = xsD[:,xs_] * b2mb
            
    # ------------------------------------------------- #
    # --- [3] config Settings                       --- #
    # ------------------------------------------------- #
    config                   = cfs.configSettings( configType="plot.def", config=config )
    config["FigSize"]        = (4.5,4.5)
    config["plt_position"]   = [ 0.16, 0.16, 0.94, 0.94 ]
    config["plt_xAutoRange"] = False
    config["plt_yAutoRange"] = False
    config["plt_xRange"]     = [ 0.0, 20.0 ]
    config["plt_yRange"]     = [ 0.0, 1000.0 ]
    config["leg_FontSize"]   = 10
    config["xMajor_Nticks"]  = 11
    config["yMajor_Nticks"]  = 11
    config["plt_marker"]     = "o"
    config["plt_markersize"] = 3.0
    config["plt_linestyle"]  = "-"
    config["plt_linewidth"]  = 2.0
    config["xTitle"]         = "Energy (MeV)"
    config["yTitle"]         = "Cross-section (mb)"

    # ------------------------------------------------- #
    # --- [4] plot Figure                           --- #
    # ------------------------------------------------- #
    fig     = pl1.plot1D( config=config, pngFile=pngFile )
    for ik,xsD in enumerate(xsList):
        fig.add__plot( xAxis=xsD[:,en_], yAxis=xsD[:,xs_], label=labels[ik] )
    fig.add__legend()
    fig.set__axis()
    fig.save__figure()


# ======================================== #
# ===  実行部                          === #
# ======================================== #
if ( __name__=="__main__" ):
    display__xsection()

