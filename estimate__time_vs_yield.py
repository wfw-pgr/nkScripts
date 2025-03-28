import os, sys, json5, re
import numpy                      as np
import nkUtilities.gplot1D        as gpl
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

    settings_base = { "series.iterate":1,
                      "refill.regular":False,
                      "refill.regular.interval":1, "refill.regular.factor":1.0 }
    
    # ------------------------------------------------- #
    # --- [1] load config                           --- #
    # ------------------------------------------------- #
    with open( settingFile, "r" ) as f:
        settings = json5.load( f )
    settings = { **settings_base, **settings }
        
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

    # -- if not YieldRate (atoms/s), then ( Bq/s )  =>   ( atoms/s )    -- #
    if ( Ytype in [ "y_product", "yn_product_wt", "yn_product_bq",
                    "y_decayed", "yn_decayed_wt", "yn_decayed_bq" ] ):
        Y0 = Y0 / ( ld_A )

    # ------------------------------------------------- #
    # --- [4] integrate atoms                       --- #
    # ------------------------------------------------- #
    stack      = []
    obtained   = 0.0
    t0h, t1h   = 0.0, 0.0
    remaining  = 1.0
    tinv       = exchange__timeUnit( time=1., unit=tunit, direction="invert" )
    sched_base = { "dt"                : [ 1.0, "s" ],
                   "beam.relint"       :   0.0,
                   "nPoints"           :     1,
                   "separation"        : False,
                   "separation.timing" : "end",
                   "separation.reserve":  True,
                   "refill"            : False,
                   "refill.timing"     : "end",
                   "refill.factor"     :   1.0,
    }
    series     = settings["series"] * settings["series.iterate"]
    if ( "series.preprocess" in settings ):
        series = settings["series.preprocess"] + series 

    nRefill    = len( settings["series"] ) * settings["refill.regular.interval"]
    for ik,key in enumerate( series ):
        
        # ------------------------------------------------- #
        # --- [4-1] preparation                         --- #
        # ------------------------------------------------- #
        sched  = { **sched_base, **settings[key] }
        dt     = tinv * exchange__timeUnit( time=sched["dt"][time_], \
                                            unit=sched["dt"][unit_] )  # (?) -> (s) -> (tunit)
        t0h    = t1h          # (tunit)
        t1h    = t1h + dt     # (tunit)
        Y0h    = sched["beam.relint"] * Y0 * remaining
        
        # ------------------------------------------------- #
        # --- [4-2] separation ( [B] -> 0.0 )           --- #
        # ------------------------------------------------- #
        if ( sched["separation"] ):
            if ( sched["separation.timing"].lower() == "beggining" ):
                if ( sched["separation.reserve"] ):
                    obtained += ld_B * B0_loc_
                B0_loc    = 0.0
                remaining = remaining * settings["Y.recycle.factor"]
        #  -- refill -- # 
        if ( sched["refill"] ):
            if ( sched["refill.timing"].lower() == "beggining" ):
                remaining = sched["refill.factor"]
                
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
        # --- [4-5] separation ( [B] -> 0.0 )           --- #
        # ------------------------------------------------- #
        if ( sched["separation"] ):
            if ( sched["separation.timing"].lower() == "end" ):
                if ( sched["separation.reserve"] ):
                    obtained += ld_B * B0_loc_
                B0_loc_   = 0.0
                remaining = remaining * settings["Y.recycle.factor"]
        #  -- refill -- # 
        if ( sched["refill"] ):
            if ( sched["refill.timing"].lower() == "end" ):
                remaining = sched["refill.factor"]

        # ------------------------------------------------- #
        # --- [4-6] regular refill                      --- #
        # ------------------------------------------------- #
        if ( settings["refill.regular"] ):
            if ( ( (ik+1) % nRefill ) == 0 ):
                remaining = settings["refill.regular.factor"]
        
                
        # ------------------------------------------------- #
        # --- [4-7] Data sampling                       --- #
        # ------------------------------------------------- #
        t_loc          = np.linspace( t0h, t1h, sched["nPoints"] )
        Anum, Bnum     = func_A( t_loc ), func_B( t_loc )
        Aact, Bact     = ld_A*Anum, ld_B*Bnum
        Bcum           = np.repeat(                             obtained, sched["nPoints"] )
        tgtE           = np.repeat( remaining*settings["Y.normalize.Bq"], sched["nPoints"] )
        A0_loc, B0_loc = A0_loc_, B0_loc_
        stack         += [ np.concatenate( [ t_loc[:,np.newaxis], \
                                             Anum [:,np.newaxis], Bnum[:,np.newaxis],\
                                             Aact [:,np.newaxis], Bact[:,np.newaxis],\
                                             Bcum [:,np.newaxis], tgtE[:,np.newaxis] ], axis=1) ]
        
    # ------------------------------------------------- #
    # --- [5] concatenate data                      --- #
    # ------------------------------------------------- #
    tEvo  = np.concatenate( stack, axis=0 )
    
    # ------------------------------------------------- #
    # --- [6] save and return                       --- #
    # ------------------------------------------------- #
    if ( settings["result.outFile"] is not None ):
        import nkUtilities.save__pointFile as spf
        names = [ "time", "Anum", "Bnum", "Aact", "Bact", "Bcum", "inventory" ]
        spf.save__pointFile( outFile=settings["result.outFile"], Data=tEvo, names=names )
    return( tEvo )


# ========================================================= #
# ===  draw__figure                                     === #
# ========================================================= #

def draw__figure( Data=None, settings=None, settingFile=None ):

    t_, NA_, NB_, AA_, AB_, CB_, RM_ = 0, 1, 2, 3, 4, 5, 6
    min_, max_, num_                 = 0, 1, 2

    if ( settings is None ):
        if ( settingFile is None ):
            sys.exit( "[dray__figure] settings & settingFile == None " )
        else:
            with open( settingFile, "r" ) as f:
                settings = json5.load( f )
    
    # ------------------------------------------------- #
    # --- [3] plot ( Number of Atoms )              --- #
    # ------------------------------------------------- #
    config = { **( lcf.load__config() ), **settings["figure.num.config"] }
    fig    = gpl.gplot1D( config=config, pngFile=settings["figure.num.config"]["figure.pngFile"])
    fig.add__plot( xAxis=Data[:,t_], yAxis=Data[:,NA_], \
                   color="C0", label=settings["figure.num.label.A"] )
    fig.add__plot( xAxis=Data[:,t_], yAxis=Data[:,NB_], \
                   color="C1", label=settings["figure.num.label.B"] )
    fig.set__legend()
    fig.set__axis()
    fig.save__figure()

    # ------------------------------------------------- #
    # --- [4] plot ( Activity )                     --- #
    # ------------------------------------------------- #
    config = { **( lcf.load__config() ), **settings["figure.act.config"] }
    fig    = gpl.gplot1D( config=config, pngFile=settings["figure.act.config"]["figure.pngFile"])
    fig.add__plot ( xAxis=Data[:,t_], yAxis=Data[:,AA_],\
                    color="C0", label=settings["figure.act.label.A"] )
    fig.add__plot ( xAxis=Data[:,t_], yAxis=Data[:,AB_],\
                    color="C1", label=settings["figure.act.label.B"] )
    fig.add__plot2( xAxis=Data[:,t_], yAxis=Data[:,CB_],\
                    color="C2", label=settings["figure.act.label.C"] )
    fig.add__cursor( xAxis=365.0, linestyle="--", linewidth=1.2, color="lightgrey" )
    fig.set__legend ()
    fig.set__axis   ()
    fig.set__axis2  ()
    fig.save__figure()
    
    # ------------------------------------------------- #
    # --- [5] plot ( inventory )                    --- #
    # ------------------------------------------------- #
    config = { **( lcf.load__config() ), **settings["figure.inv.config"] }
    fig    = gpl.gplot1D( config=config )
    fig.add__plot ( xAxis=Data[:,t_], yAxis=Data[:,RM_], \
                    color="C3", label=settings["figure.inv.label.I"] )
    fig.add__plot2( xAxis=Data[:,t_], yAxis=Data[:,CB_], \
                    color="C2", label=settings["figure.inv.label.C"] )
    fig.add__cursor( xAxis=365.0, linestyle="--", linewidth=1.2, color="lightgrey" )
    fig.set__legend ()
    fig.set__axis   ()
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
        print( "[estimate__time_vs_yield.py] no --settingFile." )
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
    
