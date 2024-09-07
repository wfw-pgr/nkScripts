import os, sys, json5, re
import numpy                      as np
import nkUtilities.plot1D         as pl1
import nkUtilities.load__config   as lcf
import nkUtilities.configSettings as cfs

time_, unit_ = 0, 1

# ========================================================= #
# ===  acquire__irradiatedAmount                        === #
# ========================================================= #
# -- calculate amount of [A], parent nuclei              -- #

def acquire__irradiatedAmount( A0=0.0, tH_A=None, Y0=0.0, t0=0.0, t1=0.0, unit=None ):
    
    # ------------------------------------------------- #
    # --- [1] Arguments                             --- #
    # ------------------------------------------------- #
    if ( tH_A is None ): sys.exit( "[acquire__irradiatedAmount] tH_A is None")
    if ( t1   <  t0   ): sys.exit( "[acquire__irradiatedAmount] t1   <= t0 " )
    if ( unit is None ): sys.exit( "[acquire__irradiatedAmount] unit is not designated...." )

    ld_A = convert__tHalf2lambda( tH=tH_A[time_], unit=tH_A[unit_] )
    conv = exchange__timeUnit   ( time=1., unit=unit, direction="convert" )
        
    # ------------------------------------------------- #
    # --- [2] calculate time evolution              --- #
    # ------------------------------------------------- #
    func = lambda t: A0*np.exp( -ld_A*conv*(t-t0) ) \
        + (Y0/ld_A)*( 1.0-np.exp( -ld_A*conv*(t-t0) ) )
    Arad = func( t1 )
    return( Arad, func )


# ========================================================= #
# ===  acquire__decayedAmount                           === #
# ========================================================= #
# -- calculate amount of [B], daughter nuclei            -- #

def acquire__decayedAmount( A0=0.0, B0=0.0, tH_A=None, tH_B=None, Y0=0.0, \
                            t0=0.0, t1=0.0, unit=None ):

    # ------------------------------------------------- #
    # --- [1] Arguments                             --- #
    # ------------------------------------------------- #
    if ( tH_A is None ): sys.exit( "[acquire__irradiatedAmount] tH_A is None")
    if ( tH_B is None ): sys.exit( "[acquire__irradiatedAmount] tH_B is None")
    if ( t1   <  t0   ): sys.exit( "[acquire__irradiatedAmount] t1   <= t0 " )
    if ( unit is None ): sys.exit( "[acquire__irradiatedAmount] unit is not designated...." )
    ld_A = convert__tHalf2lambda( tH=tH_A[time_], unit=tH_A[unit_] )
    ld_B = convert__tHalf2lambda( tH=tH_B[time_], unit=tH_B[unit_] )
    conv = exchange__timeUnit   ( time=1., unit=unit, direction="convert" )

    # ------------------------------------------------- #
    # --- [2] calculate time evolution              --- #
    # ------------------------------------------------- #
    coef1   = B0
    coef2   = ( ld_A*A0 - Y0 ) / ( ld_B - ld_A )
    coef3   = Y0 / ld_B
    func    = lambda t: coef1*np.exp( - ld_B*conv*(t-t0) ) \
        + coef2*( np.exp( - ld_A*conv*(t-t0) ) - np.exp( - ld_B*conv*(t-t0) ) ) \
        + coef3*( 1.0-np.exp( - ld_B*conv*(t-t0) ) )
    Brad    = func( t1 )
    return( Brad, func )


# ========================================================= #
# ===  unit_in_sec                                      === #
# ========================================================= #

def exchange__timeUnit( time=0.0, unit=None, direction="convert" ):

    if ( unit is None ): sys.exit( "[exchange__timeUnit] unit is not designated...." )

    # -- convert :: unit -> [s]   -- #
    # --  invert :: [s]  -> unit  -- #
    
    cdict = { "y":365.0*24*60*60, "d":24*60*60.0, "h":60*60.0, "m":60.0, "s":1.0 }
    coeff = cdict[ unit.lower() ]
    if   ( direction=="convert" ):
        return( time * coeff )
    elif ( direction=="invert"  ):
        return( time / coeff )
    

# ========================================================= #
# ===  convert__tHalf2lambda                            === #
# ========================================================= #

def convert__tHalf2lambda( tH=0.0, unit=None ):
    
    if ( unit is None ): sys.exit( "[convert__tHalf2lambda] unit is not designated...." )
    tH_ = exchange__timeUnit( time=tH, unit=unit, direction="convert" )
    ld  = np.log(2.0) / ( tH_ )   # unit :: [s^-1]
    return( ld )


# ========================================================= #
# ===  acquire__timeSeries                              === #
# ========================================================= #

def acquire__timeSeries( settingFile=None ):
    
    # ------------------------------------------------- #
    # --- [1] load config                           --- #
    # ------------------------------------------------- #
    with open( settingFile, "r" ) as f:
        settings = json5.load( f )
        
    # ------------------------------------------------- #
    # --- [2] iterate according to beam schedule    --- #
    # ------------------------------------------------- #
    A0_loc     = settings["A0.init"]
    B0_loc     = settings["B0.init"]
    tH_A       = settings["tHalf.A"]
    tH_B       = settings["tHalf.B"]
    tunit      = settings["series.time.unit"]
    ld_A       = convert__tHalf2lambda( tH=tH_A[time_], unit=tH_A[unit_] )
    ld_B       = convert__tHalf2lambda( tH=tH_B[time_], unit=tH_B[unit_] )
    
    # ------------------------------------------------- #
    # --- [3] calculate Y0 ( Yieldrate (atoms/s) )  --- #
    # ------------------------------------------------- #
    Ytype = settings["Y.efficiency.type"].lower()
    Y0    = settings["Y.efficiency.value"]
    
    # -- if normalized,    ( Bq/(mg uA s) ) => ( Bq/s )  -- #
    if ( Ytype in [ "yn_product_wt", "yn_decayed_wt" ] ):
        Y0 = Y0 * settings["Y.normalize.uA"] * settings["Y.normalize.mg"]
        
    # -- if normalized,    ( Bq/(Bq uA s) ) => ( Bq/s )  -- #
    if ( Ytype in [ "yn_product_bq", "yn_decayed_bq" ] ):
        Y0 = Y0 * settings["Y.normalize.uA"] * settings["Y.normalize.Bq"]

    # -- if decayed nuclei,  x A/B   =>   ( Bq/s of A )  -- #
    if ( Ytype in [ "y_decayed", "yn_decayed_wt", "yn_decayed_bq" ] ):
        Y0 = Y0 / ( settings["Y.ratio.B/A"] )

    # -- if not YieldRate, ( Bq/s )  =>   ( atoms/s )    -- #
    if ( Ytype in [ "y_product", "yn_product_wt", "yn_product_bq",
                    "y_decayed", "yn_decayed_wt", "yn_decayed_bq" ] ):
        Y0 = Y0 / ( ld_A )

    # ------------------------------------------------- #
    # --- [4] integrate atoms                       --- #
    # ------------------------------------------------- #
    stack      = []
    obtained   = 0.0
    t0h, t1h   = 0.0, 0.0
    tinv       = exchange__timeUnit( time=1., unit=tunit, direction="invert" )
    for ik,key in enumerate( settings["series"] ):
        
        # ------------------------------------------------- #
        # --- [4-1] preparation                         --- #
        # ------------------------------------------------- #
        sched  = settings[key]
        dt     = tinv * exchange__timeUnit( time=sched["dt"][time_], \
                                            unit=sched["dt"][unit_] )  # (?) -> (s) -> (tunit)
        t0h    = t1h          # (tunit)
        t1h    = t1h + dt     # (tunit)
        Y0h    = sched["beam.relint"] * Y0
        
        # ------------------------------------------------- #
        # --- [4-2] separation ( milking : [B]->0.0 )   --- #
        # ------------------------------------------------- #
        if ( "separation" in sched ):
            if ( sched["separation"] ):
                obtained += B0_loc
                B0_loc    = 0.0

        # ------------------------------------------------- #
        # --- [4-3] update [A]                          --- #
        # ------------------------------------------------- #
        A0_loc_, func_A = acquire__irradiatedAmount( A0=A0_loc, tH_A=tH_A, \
                                                     unit=tunit, Y0=Y0h, t0=t0h, t1=t1h )

        # ------------------------------------------------- #
        # --- [4-4] update [B]                          --- #
        # ------------------------------------------------- #
        B0_loc_, func_B = acquire__decayedAmount( A0=A0_loc, B0=B0_loc, tH_A=tH_A, tH_B=tH_B,\
                                                  unit=tunit, Y0=Y0h, t0=t0h, t1=t1h )
        
        # ------------------------------------------------- #
        # --- [4-5] Data sampling                       --- #
        # ------------------------------------------------- #
        t_loc          = np.linspace( t0h, t1h, sched["nPoints"] )
        Anum, Bnum     = func_A( t_loc ), func_B( t_loc )
        Aact, Bact     = ld_A*Anum, ld_B*Bnum
        A0_loc, B0_loc = A0_loc_, B0_loc_
        stack         += [ np.concatenate( [ t_loc[:,np.newaxis], \
                                             Anum [:,np.newaxis], Bnum[:,np.newaxis],
                                             Aact [:,np.newaxis], Bact[:,np.newaxis]], axis=1) ]
        
    # ------------------------------------------------- #
    # --- [5] concatenate data                      --- #
    # ------------------------------------------------- #
    tEvo  = np.concatenate( stack, axis=0 )
    
    # ------------------------------------------------- #
    # --- [6] save and return                       --- #
    # ------------------------------------------------- #
    if ( settings["result.outFile"] is not None ):
        import nkUtilities.save__pointFile as spf
        names = [ "time", "Anum", "Bnum", "Aact", "Bact" ]
        spf.save__pointFile( outFile=settings["result.outFile"], Data=tEvo, names=names )
    return( tEvo )


# ========================================================= #
# ===  draw__figure                                     === #
# ========================================================= #

def draw__figure( Data=None, settings=None, settingFile=None ):

    t_, NA_, NB_, AA_, AB_ = 0, 1, 2, 3, 4
    min_, max_, num_       = 0, 1, 2

    if ( settings is None ):
        if ( settingFile is None ):
            sys.exit( "[dray__figure] settings & settingFile == None " )
        else:
            with open( settingFile, "r" ) as f:
                settings = json5.load( f )
    
    # ------------------------------------------------- #
    # --- [1] Data                                  --- #
    # ------------------------------------------------- #
    config                   = lcf.load__config()
    config                   = cfs.configSettings( configType="plot.def", config=config )
    config["FigSize"]        = (4.5,4.5)
    config["plt_position"]   = [ 0.16, 0.16, 0.94, 0.94 ]
    config["plt_xAutoRange"] = settings["figure.xAutoRange"]
    config["plt_yAutoRange"] = settings["figure.yAutoRange"]
    config["xMajor_Nticks"]  =  6
    config["yMajor_Nticks"]  = 11
    config["plt_marker"]     = "none"
    config["plt_markersize"] = 0.0
    config["plt_linestyle"]  = "-"
    config["plt_linewidth"]  = 1.6

    # ------------------------------------------------- #
    # --- [3] plot ( Number of Atoms )              --- #
    # ------------------------------------------------- #
    config["xTitle"]         =   settings["figure.num.xTitle"]
    config["yTitle"]         =   settings["figure.num.yTitle"]
    config["plt_xRange"]     = [ settings["figure.num.xMinMaxNum"][min_],
                                 settings["figure.num.xMinMaxNum"][max_] ]
    config["plt_yRange"]     = [ settings["figure.num.yMinMaxNum"][min_],
                                 settings["figure.num.yMinMaxNum"][max_] ]
    config["xMajor_Nticks"]  =   settings["figure.num.xMinMaxNum"][num_]
    config["yMajor_Nticks"]  =   settings["figure.num.yMinMaxNum"][num_]
    fig     = pl1.plot1D( config=config, pngFile=settings["figure.num.pngFile"] )
    fig.add__plot( xAxis=Data[:,t_], yAxis=Data[:,NA_]/settings["figure.num.y.normalize"], \
                   color="C0", label=settings["figure.num.label.A"] )
    fig.add__plot( xAxis=Data[:,t_], yAxis=Data[:,NB_]/settings["figure.num.y.normalize"], \
                   color="C1", label=settings["figure.num.label.B"] )
    fig.add__legend()
    fig.set__axis()
    fig.save__figure()

    # ------------------------------------------------- #
    # --- [4] plot ( Activity )                     --- #
    # ------------------------------------------------- #
    config["xTitle"]         =   settings["figure.act.xTitle"]
    config["yTitle"]         =   settings["figure.act.yTitle"]
    config["plt_xRange"]     = [ settings["figure.act.xMinMaxNum"][min_],
                                 settings["figure.act.xMinMaxNum"][max_] ]
    config["plt_yRange"]     = [ settings["figure.act.yMinMaxNum"][min_],
                                 settings["figure.act.yMinMaxNum"][max_] ]
    config["xMajor_Nticks"]  =   settings["figure.act.xMinMaxNum"][num_]
    config["yMajor_Nticks"]  =   settings["figure.act.yMinMaxNum"][num_]
    fig     = pl1.plot1D( config=config, pngFile=settings["figure.act.pngFile"] )
    fig.add__plot( xAxis=Data[:,t_], yAxis=Data[:,AA_]/settings["figure.act.y.normalize"],\
                   color="C0", label=settings["figure.act.label.A"] )
    fig.add__plot( xAxis=Data[:,t_], yAxis=Data[:,AB_]/settings["figure.act.y.normalize"],\
                   color="C1", label=settings["figure.act.label.B"] )
    fig.add__legend()
    fig.set__axis()
    fig.save__figure()

    
    return()


# ========================================================= #
# ===   Execution of Pragram                            === #
# ========================================================= #

if ( __name__=="__main__" ):

    default_settingFile = "dat/settings.json"

    # ------------------------------------------------- #
    # --- [1] arguments                             --- #
    # ------------------------------------------------- #
    import argparse
    parser      = argparse.ArgumentParser()
    parser.add_argument( "--settingFile"  , help="setting config file name (.json)" )
    args        = parser.parse_args()
    settingFile = args.settingFile
    if ( settingFile is None ):
        print( "[estimate__time_vs_yield.py] no --inpFile." )
        if ( os.path.exists( default_settingFile ) ):
            settingFile = default_settingFile
            print( "[estimate__time_vs_yield.py] default : {} will be used."\
                   .format( default_settingFile ) )
        else:
            print( "[estimate__time_vs_yield.py] specify --settingFile ... [ERROR]" )
            sys.exit()
            
    # ------------------------------------------------- #
    # --- [2] calcualte time series                 --- #
    # ------------------------------------------------- #
    tEvo = acquire__timeSeries( settingFile=settingFile )

    # ------------------------------------------------- #
    # --- [3] draw figure                           --- #
    # ------------------------------------------------- #
    ret  = draw__figure( Data=tEvo, settingFile=settingFile )
    
