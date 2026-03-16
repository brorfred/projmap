"""Module to simplify the use of cartopy"""

# pylint: disable=bad-indentation
# pylint: disable=no-member
import json
import os

import cartopy.crs as ccrs
import cartopy.feature
import cartopy.io.img_tiles as cimgt
import matplotlib.path as mpath
import matplotlib.pyplot as plt
import numpy as np

from projmap import config
from projmap.config import settings


class Projmap(object):
    def __init__(self, region="default", latarr=None, lonarr=None, clf=True, **proj_kw):
        """Initialize a Projmap instance for the given region.

        Parameters
        ----------
        region : str, optional
            Region name as defined in the settings file. Defaults to "default".
        latarr : array_like, optional
            Latitude array used by plotting methods that omit explicit coordinates.
        lonarr : array_like, optional
            Longitude array used by plotting methods that omit explicit coordinates.
        clf : bool, optional
            Clear the current figure on initialization. Defaults to True.
        **proj_kw : dict
            Additional projection keywords. Recognized keys include lat1, lat2,
            lat0, lon1, lon2, lon0, and projection, plus coordinate aliases
            (lon, lonvec, lonmat, llon, lons, lat, latvec, latmat, llat, lats).
            All extra keys are set as instance attributes.
        """
        config.change_env(region)
        self.region = region
        self.proj_kw = proj_kw

        self.lonarr = lonarr
        for key in ["lon", "lonvec", "lonmat", "llon", "lons"]:
            if key in proj_kw:
                self.lonarr = proj_kw.get(key)
        self.latarr = latarr
        for key in ["lat", "latvec", "latmat", "llat", "lats"]:
            if key in proj_kw:
                self.latarr = proj_kw.get(key)
        for key in ["lat1", "lat2", "lat0", "lon1", "lon2", "lon0", "projection"]:
            setattr(self, key, proj_kw.get(key, settings[key]))
        if self.lon0 is None:
            self.lon0 = self.lon1 + (self.lon2 - self.lon1) / 2
        self.style = settings.style
        for key, val in self.proj_kw.items():
            setattr(self, key, val)
        if (len(plt.gcf().get_axes()) > 0) and clf:
            plt.clf()

    def set_style(self, landfill="0.7", landedge="0.5"):
        """Override the default map style.

        Updates ``self.style`` with the given land fill and edge colors.

        Parameters
        ----------
        landfill : str, optional
            Face color of land masses. Defaults to "0.7".
        landedge : str, optional
            Edge color of land mass outlines. Defaults to "0.5".
        """
        self.style = dict(
            landedge=landedge,
            landface=landfill,
            landwidth=0.2,
            landresolution=self.style.get("landresolution", "10m"),
            rivercolor="dodgerblue",
            statecolor="olivedrab",
            oceancolor="0.2",
            landzorder=None,
        )

    @property
    def proj(self):
        """Create main projection object.

        Returns
        -------
        proj : cartopy.crs.Projection
            The Cartopy projection corresponding to ``self.projection``.
            Supported values: ``"lcc"``, ``"eckert4"``, ``"merc"``,
            ``"north_stereo"``, ``"south_stereo"``. Any other value returns a
            Robinson projection.
        """
        self.llproj = ccrs.Geodetic()
        if self.projection == "lcc":
            if not hasattr(self, "lat0"):
                self.lat0 = self.lat1 + (self.lat2 - self.lat1) / 2
            return ccrs.LambertConformal(
                central_latitude=self.lat0, central_longitude=self.lon0
            )
        elif self.projection == "eckert4":
            return ccrs.EckertIV(central_longitude=self.lon0)
        elif self.projection == "merc":
            return ccrs.Mercator()
        elif self.projection == "north_stereo":
            self.llproj = ccrs.PlateCarree()
            return ccrs.NorthPolarStereo()
        elif self.projection == "south_stereo":
            self.llproj = ccrs.PlateCarree()
            return ccrs.SouthPolarStereo()
        else:
            central_longitude = settings.get("lon0", 0)
            return ccrs.Robinson(central_longitude=central_longitude)

    def _add_projection_to_dict(self, axes_kw=None):
        """Inject the current projection into an axes keyword dictionary.

        Parameters
        ----------
        axes_kw : dict, optional
            Existing keyword arguments for axes creation. A ``projection`` key
            is added if not already present. Defaults to an empty dict.

        Returns
        -------
        axes_kw : dict
            Updated keyword arguments with ``projection`` set.
        """
        if axes_kw is None:
            axes_kw = {}
        axes_kw["projection"] = axes_kw.get("projection", self.proj)
        return axes_kw

    def new_map(self, axes_kw=None, **proj_kw):
        """Create a new map axes on the current figure.

        Parameters
        ----------
        axes_kw : dict, optional
            Keyword arguments passed to ``plt.axes``. The projection is added
            automatically if not specified.
        **proj_kw : dict
            Currently unused; reserved for future use.
        """
        self.fig = plt.gcf()
        axes_kw = self._add_projection_to_dict(axes_kw)
        self.ax = plt.axes(**axes_kw)
        self.set_extent()
        self.fig.canvas.draw()

    def set_extent(self, **kwargs):
        """Set the geographic extent of the map.

        Parameters
        ----------
        lat1 : float, optional
            Southern-most latitude.
        lat2 : float, optional
            Northern-most latitude.
        lon1 : float, optional
            Western-most longitude.
        lon2 : float, optional
            Eastern-most longitude.
        ax : int or matplotlib.axes.Axes, optional
            Subplot index or axis object. Normally only used with subplots.
        """
        ax = self._get_or_create_axis(ax=kwargs.pop("ax", None))
        for attr in ["lon1", "lon2", "lat1", "lat2"]:
            setattr(self, attr, kwargs.get(attr, getattr(self, attr)))
        ax.set_extent([self.lon1, self.lon2, self.lat1, self.lat2], ccrs.PlateCarree())

    def set_circle_boundary(self, **kwargs):
        """Apply a circular boundary to the current map axes.

        Useful for polar stereographic projections where a round frame
        is more natural than a rectangular one.

        Parameters
        ----------
        **kwargs : dict
            ax : int or matplotlib.axes.Axes, optional
                Subplot index or axis object.
        """
        ax = self._get_or_create_axis(ax=kwargs.pop("ax", None))
        theta = np.linspace(0, 2 * np.pi, 100)
        center, radius = [0.5, 0.5], 0.5
        verts = np.vstack([np.sin(theta), np.cos(theta)]).T
        circle = mpath.Path(verts * radius + center)
        ax.set_boundary(circle, transform=ax.transAxes)

    def add_land(self, **kwargs):
        """Draw land on map.

        Parameters
        ----------
        scale : str, optional
            Resolution of coastline. For NaturalEarth one of ``'10m'``,
            ``'50m'``, or ``'110m'``. For GSHHG one of ``'crude'``,
            ``'low'``, ``'intermediate'``, ``'high'``, ``'full'``, or
            single-letter equivalents.
        facecolor : str, optional
            Color of land.
        edgecolor : str, optional
            Color of land outline.
        ax : int or matplotlib.axes.Axes, optional
            Subplot index or axis object. Normally only used with subplots.
        """
        stylekeys = [
            "landface",
            "landedge",
            "landwidth",
            "landresolution",
            "landzorder",
        ]
        landkeys = ["facecolor", "edgecolor", "linewidth", "scale", "zorder"]
        for lkey, skey in zip(landkeys, stylekeys):
            kwargs[lkey] = kwargs.get(lkey, self.style.get(skey, None))
        ax = self._get_or_create_axis(**kwargs)

        if settings["landresolution"] in [
            "c",
            "crude",
            "l",
            "low",
            "i",
            "intermediate",
            "h",
            "high",
            "f",
            "full",
            "auto",
        ]:
            land = cartopy.feature.GSHHSFeature(
                scale=settings["landresolution"],
                levels=[1],
                linewidth=settings["style"]["landwidth"],
                facecolor=settings["style"]["landface"],
                edgecolor=settings["style"]["landedge"],
            )

        else:
            land = cartopy.feature.NaturalEarthFeature("physical", "land", **kwargs)
        ax.add_feature(land)

    def add_locations(self, **kwargs):
        """Add location markers and labels to the map.

        Locations are read from ``settings.locations``. Each entry must have
        ``lon``, ``lat``, ``color``, and ``name`` attributes, and optionally
        ``ha`` (horizontal alignment) and ``va`` (vertical alignment).

        Parameters
        ----------
        zorder : int, optional
            Drawing order for markers and labels. Defaults to 10.
        **kwargs : dict
            Additional keyword arguments (only ``zorder`` is used).
        """
        for loc in settings.get("locations", []):
            self.scatter(
                loc.lon,
                loc.lat,
                c=loc.color,
                zorder=kwargs.get("zorder", 10),
            )
            self.text(
                loc.lon,
                loc.lat,
                loc.name,
                zorder=kwargs.get("zorder", 10),
                horizontalalignment=loc.get("ha", "right"),
                verticalalignment=loc.get("va", "bottom"),
            )

    def nice(
        self,
        linewidth=0.1,
        facecolor=None,
        borders=True,
        rivers=False,
        states=False,
        **proj_kw,
    ):
        """Draw a complete base map with land, borders, and optional features.

        Parameters
        ----------
        linewidth : float, optional
            Line width for borders, rivers, and states. Defaults to 0.1.
        facecolor : str, optional
            Ocean/background color. Defaults to ``self.style["oceancolor"]``.
        borders : bool, optional
            Draw country borders. Defaults to True.
        rivers : bool, optional
            Draw major rivers. Defaults to False.
        states : bool, optional
            Draw state/province boundaries. Defaults to False.
        **proj_kw : dict
            Additional keyword arguments forwarded to ``add_land`` and
            ``_get_or_create_axis``.
        """
        ax = self._get_or_create_axis(**proj_kw)
        self.add_land(**proj_kw)
        self.add_locations(**proj_kw)
        if borders:
            ax.add_feature(
                cartopy.feature.BORDERS, linewidth=linewidth, edgecolor="0.8"
            )
        if rivers:
            river_feature = cartopy.feature.NaturalEarthFeature(
                category="physical",
                name="rivers_lake_centerlines",
                scale="10m",
                facecolor="none",
                edgecolor=self.style["rivercolor"],
            )
            ax.add_feature(river_feature, linewidth=linewidth * 3)
        if states:
            ax.add_feature(
                cartopy.feature.STATES,
                linewidth=linewidth,
                edgecolor=self.style["statecolor"],
            )

        facecolor = self.style["oceancolor"] if facecolor is None else facecolor
        if facecolor is not None:
            ax.set_facecolor(facecolor)

    def subplots(
        self,
        nrows=1,
        ncols=1,
        sharex=True,
        sharey=True,
        squeeze=True,
        subplot_kw=None,
        gridspec_kw=None,
        fig_kw=None,
        **proj_kw,
    ):
        """Create a figure with multiple map subplots sharing the same projection.

        Parameters
        ----------
        nrows : int, optional
            Number of subplot rows. Defaults to 1.
        ncols : int, optional
            Number of subplot columns. Defaults to 1.
        sharex : bool, optional
            Share x-axis between subplots. Defaults to True.
        sharey : bool, optional
            Share y-axis between subplots. Defaults to True.
        squeeze : bool, optional
            Squeeze extra dimensions from the axes array. Defaults to True.
        subplot_kw : dict, optional
            Extra keyword arguments for each subplot.
        gridspec_kw : dict, optional
            Keyword arguments for the GridSpec. Defaults to {}.
        fig_kw : dict, optional
            Keyword arguments for the figure. Defaults to {}.
        **proj_kw : dict
            Additional projection keywords.

        Returns
        -------
        fig : matplotlib.figure.Figure
            The created figure.
        axes : numpy.ndarray or matplotlib.axes.Axes
            Array of axes (or a single Axes if squeeze is True and only one
            subplot is created).
        """
        if gridspec_kw is None:
            gridspec_kw = {}
        if fig_kw is None:
            fig_kw = {}
        plt.clf()
        fig_kw["num"] = fig_kw.get("num", plt.gcf().number)
        subplot_kw = self._add_projection_to_dict(subplot_kw)
        self.fig, self.axes = plt.subplots(
            nrows=nrows,
            ncols=ncols,
            sharex=sharex,
            sharey=sharey,
            squeeze=squeeze,
            subplot_kw=subplot_kw,
            gridspec_kw=gridspec_kw,
            **fig_kw,
        )
        for ax in self.fig.axes:
            ax.set_extent([self.lon1, self.lon2, self.lat1, self.lat2], self.llproj)
        return self.fig, self.axes

    def _get_or_create_axis(self, **kwargs):
        """Return the current map axes, creating a new one if necessary.

        Parameters
        ----------
        ax : int or matplotlib.axes.Axes, optional
            If an integer, returns ``self.axes.flat[ax]`` (requires a prior
            call to ``subplots``). If an Axes object, sets it as the current
            axis. If None, returns the existing axis or creates a new map.
        **kwargs : dict
            Additional keyword arguments (only ``ax`` is used).

        Returns
        -------
        ax : matplotlib.axes.Axes
            The current map axes.
        """
        if type(kwargs.get("ax")) == int:
            if not hasattr(self, "axes"):
                raise RuntimeError("Call subplots before referencing axis by number")
            if hasattr(self.axes, "flat"):
                setattr(self, "ax", self.axes.flat[kwargs["ax"]])
            else:
                setattr(self, "ax", self.axes)
        elif not getattr(self, "ax", None) in plt.gcf().get_axes():
            self.new_map()
        elif kwargs.get("ax", None) is not None:
            setattr(self, "ax", kwargs.pop("ax"))
        return getattr(self, "ax")

    def pcolor(self, *arg, **kwargs):
        """Create a pseudocolor plot in the current projection.

        Uses ``pcolormesh`` in the backend.

        Parameters
        ----------
        *arg :
            ``pcolor([lon, lat,] C, **kwargs)``. ``lon`` and ``lat`` can be
            omitted if they were set when creating the instance.
        C : array_like
            A scalar 2-D array. The values will be color-mapped.
        lon, lat : array_like, optional
            Longitude and latitude positions for the C array. Required if not
            set on the instance.
        transform : cartopy.crs.CRS, optional
            Coordinate reference system. Defaults to ``ccrs.PlateCarree()``.
        colorbar : bool or str, optional
            If not None, add a colorbar below the plot.
        **kwargs : dict
            Additional keyword arguments passed to ``ax.pcolormesh``.
        """
        ax = self._get_or_create_axis(ax=kwargs.pop("ax", None))
        if (len(arg) == 1) and (self.lonarr is not None):
            arg = (self.lonarr, self.latarr) + arg
        kwargs["transform"] = kwargs.get("transform", ccrs.PlateCarree())
        colorbar = kwargs.pop("colorbar", None)
        kwargs.pop("fieldname", None)
        self._im = ax.pcolormesh(*arg, **kwargs)
        if colorbar is not None:
            self.colorbar(colorbar)

    def hatch(self, *arg, **kwargs):
        """Create a hatched plot in the current projection.

        Masked/False values are hatched; unmasked/True values are left empty.

        Parameters
        ----------
        *arg :
            ``hatch([lon, lat,] C, **kwargs)``. ``lon`` and ``lat`` can be
            omitted if they were set when creating the instance.
        C : array_like
            A masked 2-D array. Unmasked values will be hatched.
        lon, lat : array_like, optional
            Longitude and latitude positions for the C array.
        marker : str, optional
            Hatch pattern. Any combination of ``'/', '\\', '|', '-', '+',
            'x', 'o', 'O', '.', '*'``. Repeated letters increase density.
            Defaults to ``"xxxxx"``.
        color : str, optional
            Hatch color. Defaults to ``"0.5"``.
        border_lw : float, optional
            Line width of a border around the hatch. Defaults to 0 (no border).
        transform : cartopy.crs.CRS, optional
            Coordinate reference system. Defaults to ``ccrs.PlateCarree()``.
        **kwargs : dict
            Additional keyword arguments passed to ``ax.contourf``.
        """
        ax = self._get_or_create_axis(ax=kwargs.pop("ax", None))
        if (len(arg) == 1) and (self.lonarr is not None):
            arg = (self.lonarr, self.latarr) + arg
        kwargs["transform"] = kwargs.get("transform", ccrs.PlateCarree())
        marker = kwargs.pop("marker", "xxxxx")
        marker_color = kwargs.pop("color", "0.5")
        border_lw = kwargs.pop("border_lw", 0)

        cs = ax.contourf(
            *arg, [-1, 0, 1], hatches=[None, marker], colors="none", **kwargs
        )
        for collection in cs.collections:
            collection.set_edgecolor(marker_color)
            collection.set_linewidth(border_lw)

    def contourf(self, *arg, **kwargs):
        """Create a filled contour plot on the map.

        Parameters
        ----------
        *arg :
            Passed to ``ax.contourf``. If fewer than 3 positional args are
            given and ``self.lonarr`` is set, lon/lat arrays are prepended.
        transform : cartopy.crs.CRS, optional
            Coordinate reference system. Defaults to ``ccrs.PlateCarree()``.
        colorbar : bool or str, optional
            If not None, add a colorbar below the plot.
        **kwargs : dict
            Additional keyword arguments passed to ``ax.contourf``.
        """
        ax = self._get_or_create_axis(ax=kwargs.pop("ax", None))
        if (len(arg) < 3) and (self.lonarr is not None):
            arg = (self.lonarr, self.latarr) + arg
        kwargs["transform"] = kwargs.get("transform", ccrs.PlateCarree())
        colorbar = kwargs.pop("colorbar", None)
        kwargs.pop("fieldname", None)
        self._im = ax.contourf(*arg, **kwargs)
        if colorbar is not None:
            self.colorbar(colorbar)

    def contour(self, *arg, **kwargs):
        """Create a contour line plot on the map.

        Parameters
        ----------
        *arg :
            Passed to ``ax.contour``. If fewer than 3 positional args are
            given and ``self.lonarr`` is set, lon/lat arrays are prepended.
            If exactly 4 positional args are given, the fourth is used as
            contour levels.
        transform : cartopy.crs.CRS, optional
            Coordinate reference system. Defaults to ``ccrs.PlateCarree()``.
        colorbar : bool or str, optional
            If not None, add a colorbar below the plot.
        clabel : bool or dict, optional
            If True or a dict, add contour labels. A dict is passed as keyword
            arguments to ``ax.clabel``. Defaults to None.
        **kwargs : dict
            Additional keyword arguments passed to ``ax.contour``.
        """
        ax = self._get_or_create_axis(ax=kwargs.pop("ax", None))
        if (len(arg) < 3) and (self.lonarr is not None):
            arg = (self.lonarr, self.latarr) + arg
        if len(arg) == 4:
            kwargs["levels"] = arg[-1]
            arg = arg[:3]
        transform = kwargs.pop("transform", ccrs.PlateCarree())
        colorbar = kwargs.pop("colorbar", None)
        clabel = kwargs.pop("clabel", None)
        kwargs.pop("fieldname", None)
        if clabel is not None:
            # Clip to map extent then reproject to native CRS.  A global
            # dataset (e.g. GEBCO) produces NaN/inf for most grid points after
            # transform_points, which breaks contour lines for every level that
            # spans the full map width.  Clipping first keeps only the relevant
            # portion so contour paths are continuous.
            lon_arr = np.asarray(arg[0])
            lat_arr = np.asarray(arg[1])
            data_arr = np.asarray(arg[2])
            lon_min, lon_max, lat_min, lat_max = ax.get_extent(crs=transform)
            pad_lon = (lon_max - lon_min) * 0.05
            pad_lat = (lat_max - lat_min) * 0.05
            if lon_arr.ndim == 1:
                ilon = np.where(
                    (lon_arr >= lon_min - pad_lon) & (lon_arr <= lon_max + pad_lon)
                )[0]
                ilat = np.where(
                    (lat_arr >= lat_min - pad_lat) & (lat_arr <= lat_max + pad_lat)
                )[0]
                lon_arr = lon_arr[ilon]
                lat_arr = lat_arr[ilat]
                data_arr = data_arr[np.ix_(ilat, ilon)]
                lon_arr, lat_arr = np.meshgrid(lon_arr, lat_arr)
            proj_xyz = ax.projection.transform_points(transform, lon_arr, lat_arr)
            self._im = ax.contour(
                proj_xyz[..., 0], proj_xyz[..., 1], data_arr, **kwargs
            )
            clabel_kw = clabel if isinstance(clabel, dict) else {}
            clabel_kw.setdefault("inline", True)
            clabel_kw.setdefault("fmt", " {:.0f} ".format)
            clabel_kw.setdefault("fontsize", 4)
            ax.clabel(self._im, **clabel_kw)
        else:
            kwargs["transform"] = transform
            self._im = ax.contour(*arg, **kwargs)
        if colorbar is not None:
            self.colorbar(colorbar)

    def streamplot(self, uvel=None, vvel=None, lon=None, lat=None, **kwargs):
        """Create a streamline plot of a vector field on the map.

        Parameters
        ----------
        uvel : array_like
            Zonal (east-west) velocity component.
        vvel : array_like
            Meridional (north-south) velocity component.
        lon : array_like, optional
            Longitude coordinates. Defaults to ``self.lonarr``.
        lat : array_like, optional
            Latitude coordinates. Defaults to ``self.latarr``.
        transform : cartopy.crs.CRS, optional
            Coordinate reference system. Defaults to ``ccrs.PlateCarree()``.
        colorbar : bool or str, optional
            If not None, add a colorbar below the plot.
        **kwargs : dict
            Additional keyword arguments passed to ``ax.streamplot``.
        """
        ax = self._get_or_create_axis(ax=kwargs.pop("ax", None))
        lon = self.lonarr if lon is None else lon
        lat = self.latarr if lat is None else lat
        kwargs["transform"] = kwargs.get("transform", ccrs.PlateCarree())
        colorbar = kwargs.pop("colorbar", None)
        kwargs.pop("fieldname", None)
        self._im = ax.streamplot(lon, lat, uvel, vvel, **kwargs)
        if colorbar is not None:
            self.colorbar(colorbar)

    def colorbar(self, *args, **kwargs):
        """Add a horizontal colorbar below the current map axes.

        The colorbar position is updated automatically on figure resize events.

        Parameters
        ----------
        *args :
            Currently unused.
        ax : int or matplotlib.axes.Axes, optional
            Subplot index or axis object.
        **kwargs : dict
            Additional keyword arguments forwarded to the resize event callback.
        """
        ax = self._get_or_create_axis(ax=kwargs.pop("ax", None))
        self.cax = self.fig.add_axes([0, 0, 0.1, 0.1])
        self._cb = plt.colorbar(
            self._im,
            cax=self.cax,
            orientation="horizontal",
            ticklocation="auto",
            fraction=40,
        )
        posn = ax.get_position()
        self.cax.set_position([posn.x0, posn.y0 - 0.045, posn.width, 0.035])

        def resize_colorbar(event):
            plt.draw()
            ax = self._get_or_create_axis(**kwargs)
            posn = ax.get_position()
            self.cax.set_position([posn.x0, posn.y0 - 0.045, posn.width, 0.035])

        self.fig.canvas.mpl_connect("resize_event", resize_colorbar)

    def scatter(self, lonvec, latvec, *args, **kwargs):
        """Plot scattered points on the map.

        Parameters
        ----------
        lonvec : array_like
            Longitude coordinates of the points.
        latvec : array_like
            Latitude coordinates of the points.
        *args :
            Positional args: first is ``s`` (marker size), second is ``c``
            (color array).
        transform : cartopy.crs.CRS, optional
            Coordinate reference system. Defaults to ``ccrs.PlateCarree()``.
        colorbar : bool or str, optional
            If not None, add a colorbar below the plot.
        **kwargs : dict
            Additional keyword arguments passed to ``ax.scatter``.
        """
        ax = self._get_or_create_axis(ax=kwargs.pop("ax", None))
        if len(args) > 0:
            kwargs["s"] = args[0]
        if len(args) > 1:
            kwargs["c"] = args[1]
        kwargs["transform"] = kwargs.get("transform", ccrs.PlateCarree())
        colorbar = kwargs.pop("colorbar", None)
        kwargs.pop("fieldname", None)
        self._im = ax.scatter(lonvec, latvec, **kwargs)
        if colorbar is not None:
            self.colorbar(colorbar)
        """if colorbar is not None:
            self.cax = self.fig.add_axes([0, 0, 0.1, 0.1])
            plt.colorbar(
                cb,
                cax=self.cax,
                orientation="horizontal",
                ticklocation="auto",
                fraction=40,
            )
            posn = ax.get_position()
            self.cax.set_position([posn.x0, posn.y0 - 0.045, posn.width, 0.04])
        """

    def text(self, *args, **kwargs):
        """Add a text annotation to the map.

        Parameters
        ----------
        *args :
            Either a single string (placed in the top-right corner of the map
            extent) or three values ``(lon, lat, text)``.
        transform : cartopy.crs.CRS, optional
            Coordinate reference system. Defaults to ``ccrs.Geodetic()``.
        **kwargs : dict
            Additional keyword arguments passed to ``ax.text``.
        """
        ax = self._get_or_create_axis(ax=kwargs.pop("ax", None))
        kwargs["transform"] = kwargs.get("transform", ccrs.Geodetic())
        fontsize = kwargs.pop("fontsize", settings.get("fontsize", None))

        if len(args) == 1:
            lat = self.lat1 + (self.lat2 - self.lat1) * 0.9
            lon = self.lon1 + (self.lon2 - self.lon1) * 0.99
            text = args[0]
            kwargs["ha"] = kwargs.get("horizontalalignment", "right")
        elif len(args) == 3:
            lon, lat, text = args
        ax.text(lon, lat, text, fontsize=fontsize, **kwargs)

    def rectangle(self, lon1, lat1, lon2, lat2, step=100, shade=None, **kwargs):
        """Draw a projection-correct rectangle on the map.

        Parameters
        ----------
        lon1 : float
            Western longitude of the rectangle.
        lat1 : float
            Southern latitude of the rectangle.
        lon2 : float
            Eastern longitude of the rectangle.
        lat2 : float
            Northern latitude of the rectangle.
        step : int, optional
            Number of points used to approximate each edge. Defaults to 100.
        shade : str or None, optional
            If provided, fill the rectangle interior with this color at
            50% opacity.
        transform : cartopy.crs.CRS, optional
            Coordinate reference system. Defaults to ``ccrs.Geodetic()``.
        c : str, optional
            Line color. Defaults to ``"0.5"``.
        **kwargs : dict
            Additional keyword arguments passed to ``ax.plot``.
        """
        ax = self._get_or_create_axis(**kwargs)
        kwargs["transform"] = kwargs.get("transform", ccrs.Geodetic())
        kwargs["c"] = kwargs.get("c", "0.5")
        latlist = []
        lonlist = []

        def line(lons, lats):
            ax.plot(lons, lats, **kwargs)
            latlist.append(lats)
            lonlist.append(lons)

        line([lon1] * step, np.linspace(lat1, lat2, step))
        line(np.linspace(lon1, lon2, step), [lat1] * step)
        line([lon2] * step, np.linspace(lat2, lat1, step))
        line(np.linspace(lon2, lon1, step), [lat2] * step)
        if shade is not None:
            lonlats = np.vstack((np.hstack(lonlist), np.hstack(latlist))).T
            p = plt.Polygon(
                lonlats,
                facecolor=shade,
                edgecolor=kwargs["c"],
                alpha=0.5,
                linewidth=1,
                transform=kwargs["transform"],
            )
            ax.add_patch(p)

    def add_tiles(self, zoom=8, tile_source=None, **kwargs):
        """Add a tile image (default OSM) to the map.

        Parameters
        ----------
        zoom : int, optional
            Tile zoom level. Higher values give more detail but are slower.
            Typical ranges: 5-9 for large regions, 10-15 for small regions.
            Defaults to 8.
        tile_source : cartopy img_tiles object, optional
            Tile source to use. Defaults to ``cimgt.OSM(cache=True)``.
            Examples: ``cimgt.GoogleTiles()``, ``cimgt.Stamen('terrain')``.
        **kwargs : dict
            Additional keyword arguments forwarded to ``_get_or_create_axis``.
        """
        ax = self._get_or_create_axis(**kwargs)
        if tile_source is None:
            tile_source = cimgt.OSM(cache=True)
        ax.add_image(tile_source, zoom)

    def plot(self, lons, lats, **kwargs):
        """Draw a projection-correct line on the map.

        Parameters
        ----------
        lons : array_like
            Longitude coordinates of the line.
        lats : array_like
            Latitude coordinates of the line.
        transform : cartopy.crs.CRS, optional
            Coordinate reference system. Defaults to ``ccrs.Geodetic()``.
        c : str, optional
            Line color. Defaults to ``"0.5"``.
        **kwargs : dict
            Additional keyword arguments passed to ``ax.plot``.
        """
        ax = self._get_or_create_axis(**kwargs)
        kwargs["transform"] = kwargs.get("transform", ccrs.Geodetic())
        kwargs["c"] = kwargs.get("c", "0.5")
        ax.plot(lons, lats, **kwargs)
