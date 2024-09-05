import json5

# inpFile = "test.json"
inpFile = "dat/summary.dat"
with open( inpFile, "r" ) as f:
    ret = json5.load( f )

print( ret )
