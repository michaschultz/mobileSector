""" BlueSky plugin template. The text you put here will be visible
    in BlueSky as the description of your plugin. """
from random import randint
import numpy as np
# Import the global bluesky objects. Uncomment the ones you need
import bluesky as bs
from bluesky import core, stack, traf  #, settings, navdb, sim, scr, tools

### Initialization function of your plugin. Do not change the name of this
### function, as it is the way BlueSky recognises this file as a plugin.
def init_plugin():
    ''' Plugin initialisation function. '''

    # Configuration parameters
    config = {
        # The name of your plugin
        'plugin_name':     'DYNAMICPOLY',

        # The type of this plugin. For now, only simulation plugins are possible.
        'plugin_type':     'sim',
        }

    # init_plugin() should always return a configuration dict.
    return config

mypolys = dict()

@core.timed_function
def myfun():
    # code to update polys
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
  
    # Code to send updated polys
    values =  [Clat1,Clon1,Clat2,Clon2,Clat3,Clon3,Clat4,Clon4]
   
    
    data = [
        poly.raw for poly in mypolys.values()
    ]
    bs.net.send_stream(b'DYNPOLYS', data)