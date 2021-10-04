import sys, os, subprocess

targets = ["nkBasicAlgs", "nkFilterRoutines", "nkInterpolator", "nkPhysicsRoutines", "phys" ]
srcDir  = "{0}/src/"
bckDir  = "../../"

for target in targets:
    os.chdir( srcDir.format( target ) )
    subprocess.call( "make all".split() )
    os.chdir( bckDir )
