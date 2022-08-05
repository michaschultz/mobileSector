""" BlueSky deletion area plugin. This plugin can use an area definition to
    delete aircraft that exit the area. Statistics on these flights can be
    logged with the FLSTLOG logger. """
import numpy as np
import json
import os

# Import the global bluesky objects. Uncomment the ones you need
from bluesky import traf, sim  #, settings, navdb, traf, sim, scr, tools
from bluesky.tools import datalog, areafilter
from bluesky.core import Entity, timed_function
from bluesky.tools.aero import ft,kts,nm,fpm

# Log parameters for the flight statistics log
flstheader = \
    '#######################################################\n' + \
    'FLST LOG\n' + \
    'Flight Statistics\n' + \
    '#######################################################\n\n' + \
    'Parameters [Units]:\n' + \
    'Deletion Time [s], ' + \
    'Call sign [-], ' + \
    'Spawn Time [s], ' + \
    'Flight time [s], ' + \
    'Actual Distance 2D [nm], ' + \
    'Actual Distance 3D [nm], ' + \
    'Work Done [MJ], ' + \
    'Latitude [deg], ' + \
    'Longitude [deg], ' + \
    'Altitude [ft], ' + \
    'TAS [kts], ' + \
    'Vertical Speed [fpm], ' + \
    'Heading [deg], ' + \
    'Origin Lat [deg], ' + \
    'Origin Lon [deg], ' + \
    'Destination Lat [deg], ' + \
    'Destination Lon [deg], ' + \
    'ASAS Active [bool], ' + \
    'Pilot ALT [ft], ' + \
    'Pilot SPD (TAS) [kts], ' + \
    'Pilot HDG [deg], ' + \
    'Pilot VS [fpm]'  + '\n'

confheader = \
    '#######################################################\n' + \
    'CONF LOG\n' + \
    'Conflict Statistics\n' + \
    '#######################################################\n\n' + \
    'Parameters [Units]:\n' + \
    'Simulation time [s], ' + \
    'Total number of conflicts in exp area [-]\n'

# Global data
ara = None

### Initialization function of your plugin. Do not change the name of this
### function, as it is the way BlueSky recognises this file as a plugin.
def init_plugin():

    # Addtional initilisation code
    global ara
    ara = Ara()

    # Configuration parameters
    config = {
        # The name of your plugin
        'plugin_name':     'ARA',

        # The type of this plugin. For now, only simulation plugins are possible.
        'plugin_type':     'sim'
        }

    stackfunctions = {
        'MMOV': [
            'ARA Shapename/OFF or AREA lat,lon,lat,lon,[top,bottom]',
            '[float/txt,float,float,float,alt,alt]',
            ara.set_area,
            'Create sector'
        ],
        'MSEC': [
            'MSEC',
            '',
            ara.load_firs,
            'Start mobile sector'
        ],
    }
    # init_plugin() should always return these two dicts.
    return config, stackfunctions



class Ara(Entity):
    ''' Traffic area: delete traffic when it leaves this area (so not when outside)'''
    def __init__(self):
        super().__init__()
        # Parameters of area
        self.active = False

        # The FLST logger
        self.flst = datalog.crelog('FLSTLOG', None, flstheader)
        self.conflog = datalog.crelog('CONFLOG', None, confheader)


    def reset(self):
        ''' Reset area state when simulation is reset. '''
        super().reset()
        self.active = False


    def create(self, n=1):
        ''' Create is called when new aircraft are created. '''
        super().create(n)


    @timed_function(name='ARA', dt=1.0)
    def update(self, dt):
        ''' Update flight efficiency metrics
            2D and 3D distance [m], and work done (force*distance) [J] '''
        name   = "SINF"
        if areafilter.hasArea(name):
            coords = areafilter.basic_shapes[name].coordinates
            for i in range(len(coords)):
                coords[i] += 0.1
            areafilter.defineArea(name, "POLY", coords)
        	
     

    def set_area(self, *args):
        ''' Set Experiment Area. Aircraft leaving the experiment area are deleted.
        Input can be existing shape name, or a box with optional altitude constraints.'''
        coords = [1, 100, 1, 101, 2, 101, 2, 100]
        name   = "SINF"
        areafilter.defineArea(name, "POLY", coords)
        print(coords)		




    def load_firs(self, *args):
        firs = ""
        print("--------------")
        print(os.getcwd())
        print("--------------")
        with open('plugins\\ms_data\\fir.json', 'r') as f:
            firs = json.load(f)

        # for every entry check NAME and coordinates of FIR
        for fir in firs['features']:
            name = "FIR"+fir['properties']['name']
            # extract all coordinates for
            coords = fir['geometry']['coordinates'][0]

            #transfer to array structure
            arr = np.array(coords)

            # switch columns from json file lat|lon to lon|lat
            arr.T[[0,1]] = arr.T[[1,0]]

            # create aera for each FIR            
            areafilter.defineArea(name, "POLY", arr.flatten().tolist())
	

    # def set_taxi(self, flag,alt=1500*ft):
    #     ''' Taxi ON/OFF to autodelete below a certain altitude if taxi is off'''
