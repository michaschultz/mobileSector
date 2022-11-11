""" BlueSky plugin template. The text you put here will be visible
    in BlueSky as the description of your plugin. """
import numpy as np
# Import the global bluesky objects. Uncomment the ones you need
import bluesky as bs
from bluesky.core import Signal
from bluesky import stack, ui  #, settings, navdb, sim, scr, tools
from bluesky.ui.qtgl.glhelpers import gl, RenderObject, VertexArrayObject
from bluesky.ui.qtgl.glpoly import Poly


### Initialization function of your plugin. Do not change the name of this
### function, as it is the way BlueSky recognises this file as a plugin.
def init_plugin():
    ''' Plugin initialisation function. '''
    # Configuration parameters
    config = {
        # The name of your plugin
        'plugin_name':     'DYNAMICPOLYUI',

        # The type of this plugin.
        'plugin_type':     'gui',
        }

    # init_plugin() should always return a configuration dict.
    return config


class DynamicPoly(Poly):
    def __init__(self, parent=None):
        super().__init__(parent)
        bs.net.subscribe(self, b'DYNPOLYS', actonly=True)
        Signal('stream_received').connect(self.on_stream_recvd)

    def on_stream_recvd(self, name, data, sender_id):
        if name == b'DYNPOLYS':
            actdata = bs.net.get_nodedata()
            print (poly)
            print (data)
            for poly in data:
                actdata.update_poly_data(**poly)
        return self.actdata_changed(sender_id, actdata, ['SHAPE'])