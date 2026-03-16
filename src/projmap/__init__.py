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
