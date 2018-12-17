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

    def __init__(self, region, latobj=None, lonobj=None, clf=True, **proj_kw):
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
        if  (len(plt.gcf().get_axes()) > 0) & (clf==True):
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
        self.fig = plt.gcf()
        axes_kw["projection"] = axes_kw.get("projection", self.proj)
        self.ax = plt.axes(**axes_kw)
        self.ax.set_extent([self.lon1, self.lon2, self.lat1, self.lat2],
                      ccrs.Geodetic())
        self.fig.canvas.draw()


    def add_subplot(self, *args, axes_kw={}, **proj_kw):
        """Create a map axes based on info from config file"""
        axes_kw["projection"] = axes_kw.get("projection", self.proj)
        self.ax = plt.gcf().add_subplot(*args, **axes_kw)
        self.ax.set_extent([self.lon1, self.lon2, self.lat1, self.lat2],
                      ccrs.Geodetic())
        #self.fig.canvas.draw()

    def add_land(self, edgecolor="0.5", facecolor="0.7", **proj_kw):
        """Draw land and lat-lon grid"""
        ax= self._get_or_create_axis(**proj_kw)
        arglist = ["landresolution",]
        for key in arglist:
            proj_kw[key] = proj_kw.get(key, getattr(self, key))
        land = cartopy.feature.NaturalEarthFeature(
            'physical', 'land', proj_kw["landresolution"],
            edgecolor=edgecolor, facecolor=facecolor)
        ax.add_feature(land)

    def nice(self, **proj_kw):
        """Draw land and lat-lon grid"""
        ax= self._get_or_create_axis(**proj_kw)
        arglist = ["landresolution",]
        for key in arglist:
             proj_kw[key] = proj_kw.get(key, getattr(self, key))
        land = cartopy.feature.NaturalEarthFeature(
            'physical', 'land', proj_kw["landresolution"],
            edgecolor="0.5", facecolor="0.7")
        ax.add_feature(land)
        ax.add_feature(cartopy.feature.BORDERS, linewidth=1, edgecolor="0.8")
        ax.gridlines(linewidth=0.4, alpha=0.5, color="k",linestyle='--')

    def subplots(self, nrows=1, ncols=1, sharex=True, sharey=True,
                       squeeze=True, subplot_kw={}, gridspec_kw={},
                       fig_kw={}, **proj_kw):
        plt.clf()
        fig_kw["num"] = fig_kw.get("num", plt.gcf().number)
        subplot_kw["projection"] = subplot_kw.get("projection", self.proj)
        self.fig, self.axes = plt.subplots(nrows=nrows, ncols=ncols,
            sharex=sharex, sharey=sharey, squeeze=squeeze,
            subplot_kw=subplot_kw, gridspec_kw=gridspec_kw, **fig_kw)
        for ax in self.fig.axes:
            ax.set_extent([self.lon1, self.lon2, self.lat1, self.lat2],
                           ccrs.Geodetic())
        return self.fig, self.axes


    def _get_or_create_axis(self, **kwargs):
        """Return correct map axes or create new if needed"""
        if (type(kwargs.get("ax"))==int):
            if not hasattr(self, "axes"):
                raise RuntimeError(
                    "Call subplots before referencing axis by number")
            if hasattr(self.axes, "flat"):
                setattr(self, "ax", self.axes.flat[kwargs["ax"]])
            else:
                setattr(self, "ax", self.axes)
        elif ((not getattr(self, "ax", None) in plt.gcf().get_axes())):
            self.new_map()
        elif kwargs.get("ax", None) is not None:
             setattr(self, "ax", kwargs.pop("ax"))
        return getattr(self, "ax")

    def pcolor(self, *arg, **kwargs):
        """Create a pcolor plot in mapaxes"""
        ax = self._get_or_create_axis(ax=kwargs.pop("ax", None))
        if (len(arg) == 1) & (self.lonobj is not None):
            arg = (self.lonobj, self.latobj) + arg
        kwargs["transform"] = kwargs.get("transform", ccrs.PlateCarree())
        colorbar = kwargs.pop("colorbar", None)
        fieldname = kwargs.pop("fieldname", None)
        self._cb = ax.pcolormesh(*arg, **kwargs)
        if colorbar is not None:
            self.colorbar()

    def contourf(self, *arg, **kwargs):
        """Create a contourf plot in mapaxes"""
        ax = self._get_or_create_axis(ax=kwargs.pop("ax", None))
        if (len(arg) < 3) & (self.lonobj is not None):
            arg = (self.lonobj, self.latobj) + arg
        kwargs["transform"] = kwargs.get("transform", ccrs.PlateCarree())
        colorbar = kwargs.pop("colorbar", None)
        fieldname = kwargs.pop("fieldname", None)
        self._cb = ax.contourf(*arg, **kwargs)
    
    def contour(self, *arg, **kwargs):
        """Create a contourf plot in mapaxes"""
        ax = self._get_or_create_axis(ax=kwargs.pop("ax", None))
        if (len(arg) < 3) & (self.lonobj is not None):
            arg = (self.lonobj, self.latobj) + arg
        if len(arg) == 4:
            kwargs["levels"] = arg[-1]
        kwargs["transform"] = kwargs.get("transform", ccrs.PlateCarree())
        colorbar = kwargs.pop("colorbar", None)
        fieldname = kwargs.pop("fieldname", None)
        self._cb = ax.contour(*arg, **kwargs)
      
    def colorbar(self, **kwargs):
        ax = self._get_or_create_axis(ax=kwargs.pop("ax", None))
        self.cax = self.fig.add_axes([0, 0, 0.1, 0.1])
        plt.colorbar(self._cb, cax=self.cax, orientation='horizontal',
                         ticklocation='auto', fraction=40)
        posn = ax.get_position()
        self.cax.set_position([posn.x0, posn.y0-0.045, posn.width, 0.035])
        def resize_colorbar(event):
            plt.draw()
            ax = self._get_or_create_axis(**kwargs)
            posn = ax.get_position()
            self.cax.set_position([posn.x0, posn.y0-0.045, posn.width, 0.035])
        self.fig.canvas.mpl_connect('resize_event', resize_colorbar)


        
    def scatter(self, lonvec, latvec, *args, **kwargs):
        ax = self._get_or_create_axis(ax=kwargs.pop("ax", None))
        if len(args) > 0:
            kwargs["s"] = args[0]
        if len(args) > 1:
            kwargs["c"] = args[1]
        kwargs["transform"] = kwargs.get("transform", ccrs.Geodetic())
        colorbar = kwargs.pop("colorbar", None)
        fieldname = kwargs.pop("fieldname", None)
        cb = ax.scatter(lonvec, latvec, **kwargs)
        if colorbar is not None:
            self.cax = self.fig.add_axes([0, 0, 0.1, 0.1])
            plt.colorbar(cb, cax=self.cax, orientation='horizontal',
                             ticklocation='auto', fraction=40)
            posn = ax.get_position()
            self.cax.set_position([posn.x0, posn.y0-0.045,
                                   posn.width, 0.04])
        
    def text(self, *args, **kwargs):
        ax = self._get_or_create_axis(ax=kwargs.pop("ax", None))
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
        ax = self._get_or_create_axis(**kwargs)
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
            p = plt.Polygon(lonlats, facecolor=shade, edgecolor=kwargs["c"],
                            alpha=0.5, linewidth=1,
                            transform=kwargs["transform"])
            ax.add_patch(p)

