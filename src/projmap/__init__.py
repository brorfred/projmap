from __future__ import print_function

import tomllib

from . import config
from .cartomap import Projmap
from .cartomap import Projmap as Map

__version__ = "2.0.0"

"""A wrapper for the mpl_toolkit Basemap class

Projmap helps with setting up projections and domains for areas
often used in a project. These project regions are defined in
config files where both parameters for the Basemap class and
for helper functions are defined.

The package is oriented towards oceanography but can of courese
be used in other areas as well.



Usage:
------
>>> # create Basemap instance for the North American Westcoast.
>>> mp = projmap.Projmap('westcoast')
>>> # Make a nice plot with land and meridionals/paralells
>>> mp.nice()


Config files
------------
Regions can be defined in one of three config files:

./map_regions.cfg
~/.map_regions.cfg
/path/to/where/package/is/installed/map_regions.cfg

projmap.list() lists all available regions.
projmap.list('handle') lists all settings for a region.

An example of a region is the earlier mentioned westcoast handle:

[westcoast]
proj.description: West Coast of US from x to x
base.projection:  lcc
base.llcrnrlon:  -160
base.llcrnrlat:    20
base.urcrnrlat:    60
base.urcrnrlon:  -100
base.lat_0:        40
base.lon_0:      -130
base.resolution:    i
proj.merid:        [-60, -45, -30, -15, 0, 15, 30, 45]
proj.paral:        [-80, -60, -40, -20]


Options prefixed with base. will be sent directly to the initialization
of Basemap (more information at http://matplotlib.github.com/basemap/ )

Options prefixed with proj. are used by functions in projmap.
Some examples are:

proj.description   Description string
proj.merid         List with positions for meridians
proj.paral         List with positions for parallels
proj.merid_offset  East-west offset of the map from -180 - 180 deg.

"""
# from .basemap import Projmap


settings = config.settings


# from config import list as listregions


def _load_toml_regions():
    """Return a dict mapping region name -> (description, source Path)."""
    regions = {}
    for cfg_file in config.settings_files:
        if not cfg_file.exists():
            continue
        with open(cfg_file, "rb") as f:
            data = tomllib.load(f)
        for key, val in data.items():
            if key not in regions:
                desc = val.get("description", "") if isinstance(val, dict) else ""
                regions[key] = (desc, cfg_file)
    return regions


_SKELETON_SETTINGS = """\
[default]
description = "Global Robinson projection"
projection = "robinson"
lon1 = -180
lon2 = 179
lat1 = -80
lat2 = 80
lat0 = 0
lon0 = 0
merid = []
paral = []
fontsize = "small"
[default.style]
    landedge = "0.4"
    landface = "0.6"
    landwidth = 0.2
    landresolution = "50m"
    rivercolor = "dodgerblue"
    statecolor = "olivedrab"
    oceancolor = "0.8"

[nwa]
description = "North West Atlantic"
projection = "lcc"
lon1 = -95
lon2 = -50
lat1 = 10
lat2 = 50
lat0 = 44
lon0 = -68
merid = [-90, -80, -70, -60]
paral = [20, 30, 40, 50, 60]

[korea]
description = "Korean Peninsula and surrounding waters"
projection = "lcc"
lon1 = 118
lon2 = 130
lat1 = 28
lat2 = 41
lat0 = 30
lon0 = 124
merid = [120, 125, 130]
paral = [30, 35, 40]

[antarctic]
description = "Antarctic region"
projection = "south_stereo"
lon1 = -180
lon2 = 180
lat1 = -90
lat2 = -40
merid = []
paral = []
"""


def init(path="settings.toml", overwrite=False):
    """Create a skeleton settings.toml in the current directory.

    Parameters
    ----------
    path : str, optional
        Output file path. Defaults to ``"settings.toml"``.
    overwrite : bool, optional
        Overwrite an existing file. Defaults to False.
    """
    import pathlib

    target = pathlib.Path(path)
    if target.exists() and not overwrite:
        print(f"{target} already exists. Use overwrite=True to replace it.")
        return
    target.write_text(_SKELETON_SETTINGS)
    print(f"Created {target.resolve()}")


def show_regions():
    """Print all available regions and their descriptions.

    Settings files are searched in this order:

    1. ``/etc/projmap/settings.toml``
    2. ``~/.config/projmap/settings.toml``
    3. ``./settings.toml``
    4. Path in ``PROJMAP_SETTINGS_FILE_FOR_DYNACONF``
    """
    regions = _load_toml_regions()
    by_file = {}
    for region, (desc, src) in regions.items():
        by_file.setdefault(src, []).append((region, desc))
    for src, items in by_file.items():
        print(f"\nRegions in {src}:")
        for region, desc in items:
            print(f"   {region:<20} {desc}")


def show_region(region):
    """Print all settings for a specific region.

    Parameters
    ----------
    region : str
        Region name as defined in a settings.toml file.
    """
    regions = _load_toml_regions()
    if region not in regions:
        print(f"Region '{region}' not found.")
        return
    _, src = regions[region]
    with open(src, "rb") as f:
        data = tomllib.load(f)
    print(f"\nSettings for region '{region}' (from {src}):\n")
    for key, val in data[region].items():
        print(f"   {key:<20} {val}")
