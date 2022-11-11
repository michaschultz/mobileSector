""" Halloooo! BlueSky plugin template. The text you put here will be visible
    in BlueSky as the description of your plugin. """
# Import the global bluesky objects. Uncomment the ones you need
from msvcrt import kbhit
import bluesky as bs
from bluesky import core, stack, traf, scr , settings, navdb, sim, tools
from bluesky.simulation import ScreenIO
import numpy as np
from random import randint
from scipy.spatial import Voronoi, voronoi_plot_2d
import matplotlib.pyplot as plt
 

### Initialization function of your plugin. Do not change the name of this
### function, as it is the way BlueSky recognises this file as a plugin.
def init_plugin():
    ''' Plugin initialisation function. '''
    # Instantiate our example entity
    plea = Plea()

    # Configuration parameters
    config = {
        # The name of your plugin
        'plugin_name':     'plea',

        # The type of this plugin. For now, only simulation plugins are possible.
        'plugin_type':     'sim',
        }

    # init_plugin() should always return a configuration dict.
    return config

class Plea(core.Entity):
    ''' Example new entity object for BlueSky. '''
    def __init__(self):
        super().__init__()

    @core.timed_function(name='Plea', dt=0.0001)
    def update(self): 
        
        Clat = np.mean(traf.lat)
        Clon = np.mean(traf.lon)
        
        Clat1 = Clat + 1
        Clon1 = Clon
        Clat2 = Clat - 1
        Clon2 = Clon
        Clat3 = Clat
        Clon3 = Clon + 1
        Clat4 = Clat
        Clon4 = Clon - 1
  
        stack.stack('poly square %s,%s,%s,%s,%s,%s,%s,%s' %(Clat1,Clon1,Clat2,Clon2,Clat3,Clon3,Clat4,Clon4))
        