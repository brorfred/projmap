"""Module to simplify the use of cartopy"""
# pylint: disable=bad-indentation
# pylint: disable=no-member
import json
import os

import six
from six.moves import configparser

import matplotlib.path as mpath
import matplotlib.pyplot as plt
import numpy as np

import cartopy.crs as ccrs
import cartopy.feature


class Projmap(object):

    def __init__(self, region, latarr=None, lonarr=None, clf=True, **proj_kw):
        """Initiate class instance"""
        self.basedir = os.path.dirname(os.path.abspath(__file__))
        self.region = region
        self.proj_kw = proj_kw

        self.lonarr = lonarr
        for key in ["lon", "lonvec", "lonmat", "llon"]:
            if key in proj_kw:
                self.lonarr = proj_kw.get(key)
        self.latarr = latarr
        for key in ["lat", "latvec", "latmat", "llat"]:
            if key in proj_kw:
                self.latarr = proj_kw.get(key)
        
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
        self.set_style()
        if  (len(plt.gcf().get_axes()) > 0) & (clf==True):
            plt.clf()
        

    def set_style(self, landfill="0.7", landedge="0.5"):
        """Set map style"""
        self.style = dict(landedge="0.4", landface="0.6", landwidth=0.2,
                          landresolution=self.ccrs_kw["landresolution"],
                          oceancolor="0.2"
                         )

    @property
    def proj(self):
        """Create main projection object"""
        self.llproj = ccrs.Geodetic()
        if self.projname=="lcc":
            if not hasattr(self, "lat0"):
                self.lat0 = self.lat1 + (self.lat2-self.lat1)/2
            if not hasattr(self, "lon0"):
                self.lon0 = self.lon1 + (self.lon2-self.lon1)/2
            return ccrs.LambertConformal(
                central_latitude=self.lat0, central_longitude=self.lon0)
        elif self.projname=="north_stereo":
            self.llproj = ccrs.PlateCarree()
            return ccrs.NorthPolarStereo()
        elif self.projname=="south_stereo":
            self.llproj = ccrs.PlateCarree()
            return ccrs.SouthPolarStereo()
        else:
            central_longitude = self.base_kw.get('central_longitude', 0)
            #self.llproj = ccrs.PlateCarree(central_longitude=central_longitude)
            return ccrs.Robinson(central_longitude=central_longitude)

    def _add_projection_to_dict(self, axes_kw=None):
        """Return either default of chosen projection object"""
        if axes_kw is None:
            axes_kw = {}
        axes_kw["projection"] = axes_kw.get("projection", self.proj)
        return axes_kw

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
    
    def new_map(self, axes_kw=None, **proj_kw):
        """Create a map axes based on info from config file"""
        self.fig = plt.gcf()
        axes_kw = self._add_projection_to_dict(axes_kw)
        self.ax = plt.axes(**axes_kw)
        self.set_extent()
        self.fig.canvas.draw()


    #def add_subplot(self, *args, axes_kw=None, **proj_kw):
    #    """Create a map axes based on info from config file"""
    #    axes_kw = self._add_projection_to_dict(axes_kw)
    #    self.ax = plt.gcf().add_subplot(*args, **axes_kw)
    #    self.set_extent()
    #    #self.fig.canvas.draw()

    def set_extent(self, **kwargs):
        """Set extend of map
        Set a different extent of the map than defined in config. Any value
        can be provided with the current extent as default.

        Parameters
        ----------
        lat1 : float, optional
            Southern-most Latitude
        lat2 : float, optional
            Northern-most Latitude
        lon1 : float, optional
            Western-most Longitude
        lon2 : float, optional
            Eastern-most Longitude

        Proj parameters
        ---------------
        ax : int or Axis object
            Subplot index or axis object. Normally only used with subplots.
        """      
        ax = self._get_or_create_axis(ax=kwargs.pop("ax", None))
        for attr in ["lon1", "lon2", "lat1", "lat2"]:
            setattr(self, attr, kwargs.get(attr, getattr(self, attr)))
        ax.set_extent([self.lon1, self.lon2, self.lat1, self.lat2], ccrs.PlateCarree())

    def set_circle_boundary(self, **kwargs):
        ax = self._get_or_create_axis(ax=kwargs.pop("ax", None))
        theta = np.linspace(0, 2*np.pi, 100)
        center, radius = [0.5, 0.5], 0.5
        verts = np.vstack([np.sin(theta), np.cos(theta)]).T
        circle = mpath.Path(verts * radius + center)
        ax.set_boundary(circle, transform=ax.transAxes)

    def add_land(self, **kwargs):
        """Draw land on map

        Parameters
        ----------
        scale : string
            Resoultion of coastline, one of ‘10m’, ‘50m’, or ‘110m'
        facecolor : str, optional
            Color of land
        edgecolor : str
            Color of land edge, optional

        Proj parameters
        ---------------
        ax : int or Axis object
            Subplot index or axis object. Normally only used with subplots.
        """
        stylekeys = ["landface", "landedge", "landwidth","landresolution"]
        landkeys  = ["facecolor", "edgecolor", "linewidth", "scale"]
        for lkey,skey in zip(landkeys, stylekeys):
            kwargs[lkey] = kwargs.get(lkey, self.style[skey])
        ax = self._get_or_create_axis(**kwargs)
        land = cartopy.feature.NaturalEarthFeature('physical', 'land', **kwargs)
        ax.add_feature(land)

    def nice(self, linewidth=0.1, facecolor=None, **proj_kw):
        """Draw land and lat-lon grid"""
        ax= self._get_or_create_axis(**proj_kw)
        self.add_land(**proj_kw)
        ax.add_feature(cartopy.feature.BORDERS, linewidth=linewidth, edgecolor="0.8")
        ax.gridlines(linewidth=0.4, alpha=0.5, color="k",linestyle='--')
        facecolor = self.style["oceancolor"] if facecolor is None else facecolor
        if facecolor is not None:
            ax.background_patch.set_facecolor(facecolor)

    def subplots(self, nrows=1, ncols=1, sharex=True, sharey=True,
                       squeeze=True, subplot_kw=None, gridspec_kw={},
                       fig_kw={}, **proj_kw):
        plt.clf()
        fig_kw["num"] = fig_kw.get("num", plt.gcf().number)
        subplot_kw = self._add_projection_to_dict(subplot_kw)
        self.fig, self.axes = plt.subplots(nrows=nrows, ncols=ncols,
            sharex=sharex, sharey=sharey, squeeze=squeeze,
            subplot_kw=subplot_kw, gridspec_kw=gridspec_kw, **fig_kw)
        for ax in self.fig.axes:
            ax.set_extent([self.lon1,self.lon2, self.lat1,self.lat2], self.llproj)
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
        """Create a pseudocolor plot in the current projection.

        Uses the matplot method `pcolormesh` in the backend

        Call signature
        --------------
        pcolor([lon, lat,] C, **kwargs)
        *lon* and *lat* can be used to specify lats and lons or the main array.

        Parameters
        ----------
        C : array_like
            A scalar 2-D array. The values will be color-mapped.

        lon, lat : array_like, optional
            Lon and lat positions to locate the C array on the map. See the 
            `pcolormesh`for exact definitions. Lon and lat must be set when initiating
            the class instance to omit lon and lat.

        colorbar : Bool or str, optional
            Add a colorbar to the figure. Use `global`if the figure is divided 
            subplots into subpolots and you want a global colorbar. Each subplot
            pcolor panel should have the same vmin, vmax, and cmap.
        """
        ax = self._get_or_create_axis(ax=kwargs.pop("ax", None))
        if (len(arg) == 1) & (self.lonarr is not None):
            arg = (self.lonarr, self.latarr) + arg
        kwargs["transform"] = kwargs.get("transform", ccrs.PlateCarree())
        colorbar = kwargs.pop("colorbar", None)
        fieldname = kwargs.pop("fieldname", None)
        self._im = ax.pcolormesh(*arg, **kwargs)
        if colorbar is not None:
            self.colorbar(colorbar)

    def contourf(self, *arg, **kwargs):
        """Create a contourf plot in mapaxes"""
        ax = self._get_or_create_axis(ax=kwargs.pop("ax", None))
        if (len(arg) < 3) & (self.lonarr is not None):
            arg = (self.lonarr, self.latarr) + arg
        kwargs["transform"] = kwargs.get("transform", ccrs.PlateCarree())
        colorbar = kwargs.pop("colorbar", None)
        fieldname = kwargs.pop("fieldname", None)
        self._im = ax.contourf(*arg, **kwargs)
        if colorbar is not None:
            self.colorbar(colorbar)

    def contour(self, *arg, **kwargs):
        """Create a contourf plot in mapaxes"""
        ax = self._get_or_create_axis(ax=kwargs.pop("ax", None))
        if (len(arg) < 3) & (self.lonarr is not None):
            arg = (self.lonarr, self.latarr) + arg
        if len(arg) == 4:
            kwargs["levels"] = arg[-1]
        kwargs["transform"] = kwargs.get("transform", ccrs.PlateCarree())
        colorbar = kwargs.pop("colorbar", None)
        fieldname = kwargs.pop("fieldname", None)
        self._im = ax.contour(*arg, **kwargs)
        if colorbar is not None:
            self.colorbar(colorbar)

    def streamplot(self, uvel=None, vvel=None, lon=None, lat=None, **kwargs):
        """Create a contourf plot in mapaxes"""
        ax = self._get_or_create_axis(ax=kwargs.pop("ax", None))
        lon = self.lonarr if lon is None else lon
        lat = self.latarr if lat is None else lat
        kwargs["transform"] = kwargs.get("transform", ccrs.PlateCarree())
        colorbar = kwargs.pop("colorbar", None)
        fieldname = kwargs.pop("fieldname", None)
        self._im = ax.streamplot(lon, lat, uvel, vvel, **kwargs)
        if colorbar is not None:
            self.colorbar(colorbar)

    def colorbar(self, *args, **kwargs):
        ax = self._get_or_create_axis(ax=kwargs.pop("ax", None))
        self.cax = self.fig.add_axes([0, 0, 0.1, 0.1])
        self._cb = plt.colorbar(self._im, cax=self.cax, orientation='horizontal',
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

    def plot(self, lons, lats, **kwargs):
        """Draw a projection correct line on the map."""
        ax = self._get_or_create_axis(**kwargs)
        kwargs["transform"] = kwargs.get("transform", ccrs.Geodetic())
        kwargs["c"] = kwargs.get("c", "0.5")
        ax.plot(lons, lats, **kwargs)
