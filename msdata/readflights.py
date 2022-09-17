import rdp as RDP

import lzma
import pandas as pd
import numpy as np
from io import StringIO
from tqdm import tqdm
from pyproj import Transformer
import geopandas as gp
import seaborn as sns
from matplotlib import pyplot as plt
from os.path import exists

class ReadFlights():

    # constructor
    def __init__(self):
        # initializing instance variable
        self.df =[]


    def test():
        from readflights import ReadFlights
        rf = ReadFlights()
        rf.open()

    
    def openPKL(self, fileName : str = "flights.pkl", nMax : int = 1):

        if exists(fileName):
            df = pd.read_pickle(fileName)
        else:
            print("file not exists.")

        # create unique flight ids
        list = []
        c = 0
        for a, b in zip (df['id'].shift(), df['id']):
            if a is not b:
                c = c + 1
            list.append(c)
        df['id_'] = list
        self.df = df


    def openXZ(self, fileName : str = "c:\\Users\\mschultz\\Downloads\\t_future_flas_360_ats_01.csv.xz", nMax : int = 1):

        pklFileName = fileName.replace("csv.xz","pkl")

        if exists(pklFileName):
            self.df = pd.read_pickle(pklFileName)
            return

        # return
        n = 0
        header = ""
        oldId = ""
        csv = ""

        dfList = []

        with lzma.open(fileName, mode='rt', encoding='utf-8') as file:
            for line in file:
                id = line.split(sep=",")[0]
                if oldId != id:
                    if(n > 1):  # ignore header
                        # print(header.split(sep=","))
                        csvStringIO = StringIO(csv)
                        df = pd.read_csv(csvStringIO, sep=",", header=None, names=header.split(sep=","))
                        print("import flight", df['id'].values[0])
                        # simplify altitudes first, 25ft
                        pos = df[['time','altitude']].to_numpy()
                        anchors = RDP.simplify(pos, 25, [0, len(pos)-1])  

                        # next step is simplify for distances, 200m
                        # 0°: 1° => 111,13 km
                        # 60°: 1° => 55,57 km
                        # 0.003° set as equivalent for 200m
                        # using lat and lon (degrees) by purpose, may be changed to mercator later
                        pos = df[['latitude','longitude']].to_numpy()
                        anchors = RDP.simplify(pos, .003 , anchors) # .003
                        dfList.append(df.loc[anchors].copy())

                        if n > nMax:
                            break
                    elif(n == 0):
                        # add header without \\\ at the end
                        header = str(line[:-1])
                    csv = ""
                    n += 1
                csv += str(line)

                oldId = id
            

        for df in dfList:
            # enrich dataset by distance and directions

            df['dist'], df['dir'] = self.distAndBear(df['latitude'], df['longitude'])

            # set speed as value to achieve the distance before. Thus speed now contains the speed needed for the next leg.
            df['speed'] = (df['dist']/df['time'].diff()*1000).shift(-1).fillna(0)

            # set a give date to transform seconds to timestamp
            ddt = 248054400   # 11.11.77 just for fun

            # create a new column to store time (s) as date
            df['date'] = pd.to_datetime(df['time']+ddt, unit='s', utc=True)

            # set date as index to allow for interpolation
            df.set_index('date', inplace=True)

            # be careful loses focus of "df" object
            # df = df.set_index('date') 

            # self.dfList.append(df)

        self.df = pd.concat(dfList)

        # print(self.df['id'].unique())

        self.df.to_pickle(pklFileName)
        



    # vectorized haversine function
    def distAndBear(self, lat1: list, lon1: list, lat2 : list = None, lon2 : list = None) -> list:

        if lat2 is None:
            # lat = lat1.shift()
            # lon = lon1.shift()
            # lat2 = lat1[1:]
            # lon2 = lon1[1:]
            # lat1 = lat
            # lon1 = lon
            lat2 = lat1
            lon2 = lon1
            lat1 = lat1.shift()
            lon1 = lon1.shift()

        # for a,b,c,d in zip(lat1, lon1, lat2, lon2):
        #     print(str(a) + "\t" + str(b) + "\t" + str(c) + "\t" + str(d))

        # to radians
        lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

        # pre calculation
        dLat = lat2-lat1
        dLon = lon2-lon1

        # normalized distance
        a = np.sin(dLat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dLon/2.0)**2

        # first value form NAN to 0
        a[0] = 0
        earth_radius = 6371

        # calculate distance
        dist = earth_radius * 2 * np.arcsin(np.sqrt(a))

        # calculate bearing 
        x = np.sin(dLon) * np.cos(lat2)
        y = np.cos(lat1) * np.sin(lat2) - (np.sin(lat1) * np.cos(lat2) * np.cos(dLon))
        brng = np.arctan2(x, y)
        brng = np.rad2deg(brng)

        # compass_bearing
        brng = ((brng) + 360) % 360  

        # set as course, fill NAN with 0 -- last row
        brng = brng.shift(-1).fillna(0)

        return dist, brng



    def sec2time(self, sec):
        sec = sec % (24 * 3600)
        hour = sec // 3600
        sec %= 3600
        min = sec // 60
        sec %= 60
        #    print("seconds value in hours:",hour)
        #    print("seconds value in minutes:",min)
        return "%02d:%02d:%02d" % (hour, min, sec) 



    def getResampledFlights(self, flightIDs_, sampleTime : str = "60s", df = None):
        print("resample flights")
        dfs = []
        for flightID_ in tqdm(flightIDs_):
            dfs.append(self.resample(flightID_, sampleTime))
        return pd.concat(dfs)
        


    def resample(self, flightID_ : str = None, sampleTime : str = "60s"):

        dr = self.df[self.df['id_'] == flightID_]
        # if len(dr.index) == 0:
        #     print("flight " + str(flightID) + " not found.")
        

        # 4326 is WGS 84: https://epsg.io/4326
        # 4326 is WGS 84 / Pseudo-Mercator: https://epsg.io/3857
        wgs2merc = Transformer.from_crs("epsg:4326", "epsg:3857")
        merc2wgs = Transformer.from_crs("epsg:3857", "epsg:4326")

        

        # resample the original dataframe

        # column ['id'] was deleted: --> non-numerical columns are removed in resample.
        # insert NAN values for the resampled fram
        dr_ = dr.resample(sampleTime).mean()[1:]   # first value is before first occurance
        dr_.loc[:] = np.nan # set all to nan prevent shifting of values 

        # now the data set contains all intermediate points and core points
        # combine both data sets to allow for interpolation
        dr_ = dr.combine_first(dr_)

        # it makes no sence for interpolation of these values
        dr_ = dr_.drop(['speed','dir','id_'], axis = 1)

        # consider shortest way is via pacific by checking longitudinal distance
        isLeft = abs(dr_['longitude'].max() - dr_['longitude'].min()) > 180

        # change longitudinal coordinates ensuring correct interpolation
        if isLeft:
            # the idea is that one can easily turn the earth by 180° 
            # important! bring the left hemisphere to the right side
            dr_['longitude'] = [ 360 + x if x < 0 else x for x in dr_['longitude']]
            # turn hemisphere by 180°
            dr_['longitude'] = dr_['longitude'] - 180
            
            # do the transformation to get meters
            dr_['latitude'], dr_['longitude'] = wgs2merc.transform(dr_['latitude'], dr_['longitude'])
            dr_ = dr_.interpolate('time')
            dr_['latitude'], dr_['longitude'] = merc2wgs.transform(dr_['latitude'], dr_['longitude'])
            
            # turn earth back 
            dr_['longitude'] = dr_['longitude'] + 180
            # bring the left hemisphere back to its position
            dr_['longitude'] = [ x - 360 if x > 180 else x for x in dr_['longitude']]
        else:
            dr_['latitude'], dr_['longitude'] = wgs2merc.transform(dr_['latitude'], dr_['longitude'])
            dr_ = dr_.interpolate('time')
            dr_['latitude'], dr_['longitude'] = merc2wgs.transform(dr_['latitude'], dr_['longitude'])

        # TODO: bring in correct interpolation for lat/lon
        # from pyproj import Geod

        # lon0, lat0 = 170, 10
        # lon1, lat1 = -170, 20
        # n_extra_points = 5    

        # geoid = Geod(ellps="WGS84")
        # extra_points = geoid.npts(lon0, lat0, lon1, lat1, n_extra_points)

        # print(extra_points)


        # add speed and go back to the data set and fill up with these values
        dr = dr.combine_first(dr_)


        # fillup with values from the row above
        dr = dr.ffill()

        return dr




    ''' create bluesky flight'''
    def createBSFlight(self):
        # find row which meets the criteria
        f = dff[dff['time'] > 0].index[0]
        # store all index in a list
        indexList = dff.index.values.tolist()
        # find row before -- take row 1 as minimum, since row 0 has no speed
        i = max(1, indexList.index(f) - 1)
        # access row and store at single list

        d = dff.iloc[[i]].values.flatten().tolist()

        # print(d)

        # CRE acid type lat lon hdg alt spe
        # CRE SIA37A A350 1.196620 105.570520 268.3 29798 247.4
        dt = d[1]
        print( str(sec2time(0))+">CRE", d[0], "A350 %5.6f %5.6f %5.1f %5.0f %5.1f" % (d[4], d[3], d[6], d[2], d[7]))

        # https://github.com/TUDelft-CNS-ATM/bluesky/wiki/addwpt
        # The speed at each waypoint is the speed for the leg towards this waypoint.
        # 00:00:01.11>ADDWPT,AC0001,-3.24887465,-2.77108288,0.0,450.00000000

        # all other postions are taken as waypoints
        for c in range(i+1, len(indexList)):
            d = dff.iloc[[c]].values.flatten().tolist()
            print(str(sec2time(0))+">ADDWPT", d[0], "%5.6f %5.6f %5.1f %5.1f" % (d[4], d[3], d[2], d[7]))

        # dff



    def getFlightList(self) -> list:
        return self.df['id'].unique().tolist()

    def getFlight(self, flightID : str) -> list:
        return self.df[self.df['id'] == flightID]


    def plotFlight(self, flight, flightResample = None):
        # initialize an axis
        fig, ax = plt.subplots(figsize=(20,10))

        ax.set(xlim=(70,150), ylim=(-20, 30))
        # ax.set(xlim=(90,130), ylim=(-15, 25))

        countries = gp.read_file(gp.datasets.get_path("naturalearth_lowres"))
        countries.plot(color="lightgrey", ax=ax)

        flight.plot(x="longitude", y="latitude", kind="scatter", c="altitude", colormap= "YlOrRd", ax=ax)
        if flightResample is not None:
            flightResample.plot(x="longitude", y="latitude", kind="scatter", c = "green", s=.1, ax=ax)
        

        # return fig




    def plotFlights(self, flightIDs : list, flightResample :list = None, time : list = None, df = None):
        # initialize an axis
        fig, ax = plt.subplots(figsize=(20,10))

        ax.set(xlim=(70,150), ylim=(-20, 30))
        # ax.set(xlim=(90,130), ylim=(-15, 25))

        countries = gp.read_file(gp.datasets.get_path("naturalearth_lowres"))
        countries.plot(color="lightgrey", ax=ax)

        flights = []

        if df is None:
            if time == None:
                flights = self.df[self.df['id'].isin(flightIDs)]
            else:
                flights = self.df[
                    self.df['id'].isin(flightIDs) 
                    & self.df['time'].between(time[0], time[1])
                ]
        else:
            flights = df
        

        for id_ in flights['id_'].unique():
            flights[flights['id_'] == id_].plot(x="longitude", y="latitude", c="altitude", kind="scatter", colormap= "YlOrRd", s=.1, ax=ax)


        # return fig
