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
'''
Clat2= 17.405098
Clon2= 97.871728
Clat3= 13.213485
Clon3= 107.705434
Clat4= 0.88282
Clon4= 97.749317
Clat5= -5.424946
Clon5=  105.420423
Clat6=  -8.517786
Clon6=  117.57994
Clat7=  0.10961
Clon7=  113.336353
Clat8=  0.80143
Clon8=  124.516582
Clat9= 11.300808
Clon9= 123.570896
Clat10=  -2.698363
Clon10=  133.370998
Clat11= 7.434758
Clon11= 134.635915
'''
Clat2= 1.4976
Clon2= 103.604
Clat3= 1.49803
Clon3= 103.8088
Clat4= 1.3279
Clon4= 103.60109
Clat5= 1.322818
Clon5=  103.810854
Clat6=  1.4905
Clon6=  104.041235
Clat7=  1.30934
Clon7=  104.04044
Clat8= 1.18725
Clon8=  103.6014
Clat9= 1.18486
Clon9= 103.8148
Clat10= 1.187245
Clon10= 104.0333

### Initialization function of your plugin. Do not change the name of this
### function, as it is the way BlueSky recognises this file as a plugin.
def init_plugin():
    ''' Plugin initialisation function. '''
    # Instantiate our example entity
    voro = Voro()

    # Configuration parameters
    config = {
        # The name of your plugin
        'plugin_name':     'VORO',

        # The type of this plugin. For now, only simulation plugins are possible.
        'plugin_type':     'sim',
        }

    # init_plugin() should always return a configuration dict.
    return config

class Voro(core.Entity):
    ''' Example new entity object for BlueSky. '''
    def __init__(self):
        super().__init__()

    @core.timed_function(name='Voro', dt=0.001)
    def update(self): 
        Clat1 = traf.lat
        Clon1 = traf.lon
        centers = [ [Clat1, Clon1], [Clat2, Clon2], [Clat3, Clon3], [Clat4, Clon4],[Clat5, Clon5], [Clat6, Clon6], [Clat7, Clon7], [Clat8, Clon8], [Clat9, Clon9],[Clat10, Clon10]]
        vor = Voronoi(centers)
        size_vertices = int(np.size(vor.vertices)/2)
        wplat = [0] * size_vertices
        wplon = [0] * size_vertices
        j=0
      
        simplex = 0
        for simplex in vor.ridge_vertices:
            simplex = np.asarray(simplex)
            if np.all(simplex >= 0):
                rand1 = np.random.randint(1, 1000000)
                stack.stack('poly L%s %s,%s,%s,%s' % (rand1, vor.vertices[simplex[0],0],vor.vertices[simplex[0],1],vor.vertices[simplex[1],0],vor.vertices[simplex[1],1] ))
                stack.stack('delay 0.01 DEL L%s' %rand1)
        
        centers= np.asarray(centers)
        center = centers.mean(axis=0)
        for pointidx, simplex in zip(vor.ridge_points, vor.ridge_vertices):
            simplex = np.asarray(simplex)
            if np.any(simplex < 0):
                i = simplex[simplex >= 0][0] # finite end Voronoi vertex
                t = centers[pointidx[1]] - centers[pointidx[0]]  # tangent
                t = t / np.linalg.norm(t)
                n = np.array([-t[1], t[0]]) # normal
                midpoint = centers[pointidx].mean(axis=0)
                far_point = vor.vertices[i] + np.sign(np.dot(midpoint - center, n)) * n * 100
                rand2 = np.random.randint(1, 1000000)
                stack.stack('poly M%s %s,%s,%s,%s' % (rand2,vor.vertices[i,0],vor.vertices[i,1],far_point[0],far_point[1]))
                stack.stack('delay 0.01 DEL M%s' %rand2)
        