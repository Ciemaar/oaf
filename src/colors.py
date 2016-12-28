
RED=(1,0,0)  
YELLOW=(1,1,0)
GREEN=(0,1,0)
CYAN=(0,1,1)
BLUE=(0,0,1)
VIOLET=(1,0,1)
WHITE=(1,1,1)


#RED=0  
#YELLOW=6
#GREEN=12 
#CYAN=18 
#BLUE=24
#VIOLET=30
#WHITE=36



def getWebColor(rgb_tuple):
    #http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/266466
    """ convert an (R, G, B) tuple to #RRGGBB """
    hexcolor = '#%02x%02x%02x' % tuple([255*x for x in rgb_tuple]) 
    # that's it! '%02x' means zero-padded, 2-digit hex values
    return hexcolor
    
