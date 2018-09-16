import six
from six.moves import configparser

import json
import os


import matplotlib.path as mpath
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import cartopy.crs as ccrs
import cartopy.feature


class Projmap(object):

    def __init__(self, region, latobj=None, lonobj=None, **proj_kw):
        """Initiate class instance"""
        self.basedir = os.path.dirname(os.path.abspath(__file__))
        self.region = region
        self.lonobj = lonobj
        self.latobj = latobj
        self.proj_kw = proj_kw
        
        self.read_configfile()
        for key in ['llcrnrlon', 'urcrnrlon']:
            self.base_kw[key] =  self.base_kw[key] + self.merid_offset
        for key,val in six.iteritems(self.proj_kw):
            setattr(self, key, val)
        base_kw_list = ["llcrnrlat", "llcrnrlon",
                        "urcrnrlat", "urcrnrlon",
                        "lat_0", "lon_0", "projection"]
        proj_kw_list = ["lat1", "lon1", "lat2", "lon2",
                        "lat0", "lon0","projname"]
        for k1, k2 in zip(base_kw_list, proj_kw_list):
            setattr(self, k2, self.base_kw.get(k1))
        setattr(self, "landresolution", self.ccrs_kw["landresolution"])
        if  len(plt.gcf().get_axes()) > 0:
            plt.clf()

    @property
    def proj(self):
        """Create main  projection object"""
        if (self.projname=="lcc"):
            if not hasattr(self, "lat0"):
                self.lat0 = self.lat1 + (self.lat2-self.lat1)/2
            if not hasattr(self, "lon0"):
                self.lon0 = self.lon1 + (self.lon2-self.lon1)/2
            return ccrs.LambertConformal(
                central_latitude=self.lat0, central_longitude=self.lon0)       
        else:
            return ccrs.Robinson()       
        
    def read_configfile(self):
        """Read and parse the config file"""
        cfg = configparser.ConfigParser()

        def openfile(fname):
            self.map_regions_file = fname
            cfg.read(fname)
        openfile(os.curdir + "/map_regions.cfg")
        if not self.region in cfg.sections():
            openfile(os.path.expanduser("~") + "/.map_regions.cfg")
            if not self.region in cfg.sections():
                openfile(self.basedir + "/map_regions.cfg")
                if not self.region in cfg.sections():
                    raise NameError('Region not included in config file')
        self.base_kw = {}
        self.ccrs_kw = {}
        def splitkey(key, val):
            if "base." in key:
                self.base_kw[key[5:]] = self.proj_kw.pop(key[5:], val)
            elif "ccrs." in key:
                self.ccrs_kw[key[5:]] = self.proj_kw.pop(key[5:], val)
            elif "proj." in key:
                setattr(self, key[5:], self.proj_kw.pop(key[5:], val))
            else:
                print ("Unknown option: " + key)
                print ("Remember to prefix options with base or self")

        for key,val in cfg.items(self.region):
            try:
                splitkey(key, json.loads(val))
            except ValueError:
                splitkey(key, val)
    
    def new_map(self, axes_kw={}, **proj_kw):
        """Create a map axes based on info from config file"""
        axes_kw["projection"] = axes_kw.get("projection", self.proj)
        self.ax = plt.axes(**axes_kw)
        self.ax.set_extent([self.lon1, self.lon2, self.lat1, self.lat2],
                      ccrs.Geodetic())

    def nice(self, **proj_kw):
        if ((not getattr(self, "ax", None) in plt.gcf().get_axes()) and
            (not hasattr(self, "axes"))):
            self.new_map()
        arglist = ["landresolution",]
        for key in arglist:
             proj_kw[key] = proj_kw.get(key, getattr(self, key))
        land = cartopy.feature.NaturalEarthFeature('physical', 'land',
                   proj_kw["landresolution"], edgecolor="0.5", facecolor="0.7")
        self.ax.add_feature(land)
        self.ax.add_feature(cartopy.feature.BORDERS,
                            linewidth=1, edgecolor="0.8")
        self.ax.gridlines(linewidth=0.4, alpha=0.5, color="k",linestyle='--')

    def subplots(self, nrows=1, ncols=1, sharex=False, sharey=False,
                       squeeze=True, subplot_kw={}, gridspec_kw=None,
                       fig_kw=None, **proj_kw):
        fig_kw["num"] = fig_kw.get("num", gcf().number)
        subplot_kw["projection"] = subplot_kw.get("projection", self.proj)
        self.fig, self.axes = plt.subplots(nrows=nrows, ncols=ncols,
                                           sharex=sharex, sharey=sharey,
                                           squeeze=True, subplot_kw={},
                                           gridspec_kw=None, fig_kw=None,
                                           **proj_kw)
        return self.fig, self.axes


    def _get_or_create_axis(self, kwargs):
        if ((not getattr(self, "ax", None) in plt.gcf().get_axes()) and
            (not hasattr(self, "axes"))):
            self.new_map()
        return kwargs.pop("ax", self.ax)

    
    def pcolor(self, *arg, **kwargs):
        """Create a pcolor plot in mapaxes"""
        ax = self._get_or_create_axis(kwargs)
        if (len(arg) == 1) & (self.lonobj is not None):
            arg = (self.lonobj, self.latobj) + arg
        kwargs["transform"] = kwargs.get("transform", ccrs.PlateCarree())
        fieldname = kwargs.pop("fieldname", None)
        ax.pcolormesh(*arg, **kwargs)

    def contourf(self, *arg, **kwargs):
        """Create a contourf plot in mapaxes"""
        ax = self._get_or_create_axis(kwargs)
        if (len(arg) < 3) & (self.lonobj is not None):
            arg = (self.lonobj, self.latobj) + arg
        kwargs["transform"] = kwargs.get("transform", ccrs.PlateCarree())
        ax.contourf(*arg, **kwargs)

    def scatter(self, lonvec, latvec, *args, **kwargs):
        ax = self._get_or_create_axis(kwargs)
        kwargs["transform"] = kwargs.get("transform", ccrs.Geodetic())
        if len(args) > 0:
            kwargs["s"] = args[0]
        if len(args) > 1:
            kwargs["c"] = args[1]
        ax.scatter(lonvec, latvec, **kwargs)
        
    def text(self, *args, **kwargs):
        ax = self._get_or_create_axis(kwargs)
        kwargs["transform"] = kwargs.get("transform", ccrs.Geodetic())
        if len(args) == 1:
            lat = self.lat1 + (self.lat2-self.lat1) * 0.9
            lon = self.lon1 + (self.lon2-self.lon1) * 0.99
            text = args[0]
            kwargs["ha"] = kwargs.get("horizontalalignment", 'right')
        elif len(args) == 3:
            lon,lat,text = args
        ax.text(lon, lat, text, **kwargs)


    def rectangle(self, lon1,lat1, lon2,lat2, step=100, shade=None, **kwargs):
        """Draw a projection correct rectangle on the map."""
        ax = self._get_or_create_axis(kwargs)
        kwargs["transform"] = kwargs.get("transform", ccrs.Geodetic())
        kwargs["c"] = kwargs.get("c", "0.5")
        latlist = []
        lonlist = []
        def line(lons, lats):
            ax.plot(lons, lats, **kwargs)
            latlist.append(lats)
            lonlist.append(lons)

        line([lon1]*step, np.linspace(lat1,lat2,step))
        line(np.linspace(lon1,lon2,step), [lat1]*step)
        line([lon2]*step, np.linspace(lat2,lat1,step))
        line(np.linspace(lon2,lon1,step), [lat2]*step)
        if shade is not None:
            lonlats = np.vstack((np.hstack(lonlist), np.hstack(latlist))).T
            p = plt.Polygon(lonlats, facecolor=patch, edgecolor=kwargs["c"],
                            alpha=0.5, linewidth=1,
                            transform=kwargs["transform"])
            ax.add_patch(p)

