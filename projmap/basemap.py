import ConfigParser
import json
import os

import matplotlib
import numpy as np
import pylab as pl
from mpl_toolkits.basemap import Basemap

from hitta import GBRY
from matplotlib import cm

frontDir = os.path.dirname(os.path.abspath(__file__)) + "/data/"
frontColor = '0.5'
frontwidth = 1 #0.25

basedir =  os.path.dirname(os.path.abspath(__file__))

class Projmap(Basemap):
    def __init__(self,region, **kwargs):

        self.region = region
        self.read_configfile()
        
        if not hasattr(kwargs,'resolution'): resolution = 'i'
        #if not hasattr(kwargs,'clat'):       clat = 0
        #if not hasattr(kwargs,'lat2'):       lat2 = -30

        """
        if region == 'soat':
            mpkwargs = {'projection':'merc',
                      'llcrnrlon':-45, 'urcrnrlon':28,
                      'urcrnrlat':-30, 'llcrnrlat':-75}
        elif region == 'auze':
            mpkwargs = {'projection':'merc',
                      'llcrnrlon': 119, 'urcrnrlon': 200,
                      'urcrnrlat': -30, 'llcrnrlat': -68}
        elif region == 'sose':
            mpkwargs = {'projection':'spaeqd',
                      'lon_0':0,'boundinglat':-30}
        elif region == 'soserect':
            mpkwargs = {'projection':'merc',
                      'llcrnrlon':-180+clat,'llcrnrlat':-75,
                      'urcrnrlat':lat2, 'urcrnrlon':179+clat}
        elif region == 'sglob':
            mpkwargs = {'projection':'gall',
                      'llcrnrlon':-180+clat, 'llcrnrlat':-75,
                      'urcrnrlat':60, 'urcrnrlon':179+clat}
        elif region == 'glob':
            mpkwargs = {'projection':'gall',
                      'llcrnrlon':-180+clat, 'llcrnrlat':-80,
                      'urcrnrlat':80, 'urcrnrlon':179+clat}
            self.merid = []
            self.paral = []
        elif region == 'gom':
            mpkwargs = {'projection':'lcc',
                      'llcrnrlon':-71, 'llcrnrlat':41,
                      'urcrnrlat':46, 'urcrnrlon':-63,
                      'lat_0':44, 'lon_0':-68, 'resolution':'i'}
            self.merid = np.arange(-70,-63,2)
            self.paral = np.arange(41,47,1)
        elif region == 'casco':
            mpkwargs = {'projection':'lcc',
                        'llcrnrlon':-70.6, 'llcrnrlat':43.3,
                        'urcrnrlat':44.15, 'urcrnrlon':-69.3,
                        'lat_0':44, 'lon_0':-68, 'resolution':'f'}
            self.merid = np.arange(-70,-63,2)
            self.paral = np.arange(41,47,1)
            self.scale_lon = -70
            self.scale_lat = 43.3
            self.scale_dst = 50
        elif region == 'nwa':
            mpkwargs = {'projection':'lcc',
                        'llcrnrlon':-95, 'llcrnrlat':10,
                        'urcrnrlat':50, 'urcrnrlon':-50,
                        'lat_0':44, 'lon_0':-68, 'resolution':'i'}
            self.merid = np.arange(-90,-50,10)
            self.paral = np.arange(20,40,5)
            #self.scale_lon = -70
            #self.scale_lat = 43.3
            #self.scale_dst = 50
        elif region == 'nwa_small':
            mpkwargs = {'projection':'lcc',
                        'llcrnrlon':-82, 'llcrnrlat':25,
                        'urcrnrlat':50, 'urcrnrlon':-50,
                        'lat_0':44, 'lon_0':-68, 'resolution':'i'}
            self.merid = np.arange(-90,-50,10)
            self.paral = np.arange(20,40,5)
            #self.scale_lon = -70
            #self.scale_lat = 43.3
            #self.scale_dst = 50
        elif region == 'safr':
            mpkwargs = {'projection':'stere',
                      'llcrnrlon':-70, 'llcrnrlat':-60,
                      'urcrnrlat':-20, 'urcrnrlon': 30,
                      'lat_0':-40, 'lon_0':0, 'resolution':'i'}
            self.merid = np.arange(-60,60,20)
            self.paral = np.arange(-60,-20,10)
        elif region == 'westcoast':
            mpkwargs = {'projection':'lcc',
                      'llcrnrlon':-160, 'llcrnrlat':20,
                      'urcrnrlat':60, 'urcrnrlon':-100,
                      'lat_0':40, 'lon_0':-130, 'resolution':'i'}
            self.merid = np.arange(-60,60,15)
            self.paral = np.arange(-80,0,20)
        elif region == 'scb':
            mpkwargs = {'projection':'lcc',
                        'llcrnrlon':-121.5, 'llcrnrlat':32,
                        'urcrnrlat':35, 'urcrnrlon':-117,
                        'lat_0':31, 'lon_0':-118, 'resolution':'i'}
            self.merid = [-121,-120,-119,-118]
            self.paral = [32,33,34]
        elif region == 'var':
            mpkwargs = {'projection':'lcc',
                        'llcrnrlon':kwargs['lon2'],
                        'llcrnrlat':kwargs['lat2'],
                        'urcrnrlat':kwargs['lat1'],
                        'urcrnrlon':kwargs['lon1'],
                        'lat_0':(kwargs['lat2'] + kwargs['lat1'])/2,
                        'lon_0':(kwargs['lon2'] + kwargs['lon1'])/2,
                        'resolution':'i'}
        elif region == 'keys_fla':
            mpkwargs = {'projection':'lcc',
                        'llcrnrlon':-83.5, 'llcrnrlat':24,
                        'urcrnrlat':26.5, 'urcrnrlon':-80.5,
                        'lat_0':44, 'lon_0':-68, 'resolution':'f'}
            self.merid = np.arange(-70,-63,2)
            self.paral = np.arange(41,47,1)
        if "merid" in kwargs: self.merid=kwargs["merid"]
        if "paral" in kwargs: self.paral=kwargs["paral"]
        """

        Basemap.__init__(self, **self.base_kwargs)
        self.cm_dff = GBRY()
        self.cm_val = cm.gist_ncar
        #self.clat = clat


    def read_configfile(self):
        cfg = ConfigParser.ConfigParser()
        cfg.read(basedir + "/projmapsrc")
        if not self.region in cfg.sections():
            raise NameError('Region not included in config file')
        self.base_kwargs = {}
        def splitkey(key, val):
            if "base" in key:
                self.base_kwargs[key[5:]] = val
            else:
                self.__dict__[key[5:]] = val
        for key,val in cfg.items(self.region):
            try:
                splitkey(key, json.loads(val))
            except ValueError:
                splitkey(key, val)



    def nice(self,latlabels=True,lonlabels=True):
        """ Draw land, parallells and meridians on a map"""
        if latlabels == True:
            latlabels = [1,0,0,0]
        elif latlabels == False:
            latlabels = [0,0,0,0]
            
            
        if not hasattr(self,'merid'):
            self.merid = np.arange(-60,180+70,30)
            self.paral = np.arange(-70,-30,10)
        self.fillcontinents(color=[0.6,0.6,0.6],
                           lake_color=[0.9,0.9,0.9])
        if len(self.merid)>0:
            self.drawmeridians(self.merid,
                               color='k',
                               fontsize=20,linewidth=2,
                               labels=[0,0,0,0],
                               dashes=[1,5],zorder=1)
        if len(self.paral)>0:
            self.drawparallels(self.paral,
                               color='k',
                               fontsize=20,linewidth=2,
                               labels=latlabels,
                               labelstyle="+/-",
                               dashes=[1,5],zorder=1)
        if hasattr(self,'scale_lon'):
            self.drawmapscale(-69.6,43.35,-69.6,43.35,25)

    def rectangle(self,lon1,lat1,lon2,lat2,c='k'):

        def line(lon1,lat1,lon2,lat2):
            x,y = self.gcpoints(lon1,lat1,lon2,lat2,100)
            self.plot(x,y,c=c)
        line(lon1,lat1,lon1,lat2)
        line(lon1,lat2,lon2,lat2)
        line(lon2,lat2,lon2,lat1)
        line(lon2,lat1,lon1,lat1)

    def fronts(self,lglon=36, dlon=5, ax=None):
        def plotfront(frontFile,fname, lon):
            frmat = np.genfromtxt(frontFile)
            mask = frmat[:,0] < -180 + self.clat  
            frmat[mask, 0] = frmat[mask, 0] + 360 
            mask = ~(frmat[:,0] < np.nanmax(frmat[:,0]))
            x,y = self(frmat[:,0],frmat[:,1])
            x[mask] = np.nan
            y[mask] = np.nan
            self.plot(x, y, color=frontColor,lw=frontwidth,zorder=2)

            latpos = np.nonzero(frmat[:,0] > lon)[0].min()
            xp,yp = self(lon,frmat[latpos,1])
            if ax:
                ax.text(xp,yp,fname,va='top',size='medium',
                        bbox=dict(facecolor='w', alpha=0.7,lw=0))
                ax.text(xp,yp,fname,va='top',size='medium')
            else:
                pl.text(xp,yp,fname,va='top',size='medium',
                        bbox=dict(facecolor='w', alpha=0.7,lw=0))
                pl.text(xp,yp,fname,va='top',size='medium',)
                
        plotfront(frontDir + 'saf.txt','saf', lglon)
        plotfront(frontDir + 'stf.txt','stf', lglon+dlon)
        #plotfront(frontDir + 'saccf.txt','saccf')
        plotfront(frontDir + 'pf.txt','pf', lglon+2*dlon)
        #plotfront(frontDir + 'sbdy.txt','sbdy')

    def text(self, lon, lat, text, **kwargs):
        x,y = self(lon,lat)
        pl.text(x ,y, text, **kwargs)
  
    def hrzbar(self):
        pl.colorbar(orientation='horizontal',pad=0, aspect=40,
                 fraction=0.0244)
