from __future__ import print_function
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
#from .basemap import Projmap
try:
    from .basemap import Projmap as Basemap
    HAS_BASEMAP = True
except:
    HAS_BASEMAP = False

try:
    from .cartomap import Projmap
    from .cartomap import Projmap as Map
    HAS_CARTOPY = True
except:
    HAS_CARTOPY = False
    
import six

import os
from six.moves import configparser

def list(region=""):
    """List region information
          List options associated with a handle or
          all available regions if handle is not set."""
    cfg = configparser.ConfigParser()

    basedir =  os.path.dirname(os.path.abspath(__file__))
    cfg_file_list = [os.curdir + "/map_regions.cfg",
                     os.path.expanduser("~") + "/.map_regions.cfg",
                     basedir + "/map_regions.cfg"]
    if region:
        for cfg_file in cfg_file_list:
            cfg.read(cfg_file)
            if region in cfg.sections(): break
        print ("\n\nThe region -%s- was found in \n \n   %s:\n " %
               (region,cfg_file))
        print ("and has the following options:\n")
        for key,val in cfg.items(region):
            print ("   %s:   %s" % (key,val))
    else:
        for cfg_file in cfg_file_list:
            cfg.read(cfg_file)
            if cfg.sections():
                print ("\nRegions in \n" + cfg_file + ":")
                for sect in cfg.sections():
                    desc = ""
                    if "proj.description" in cfg.options(sect):
                        desc = cfg.get(sect,'proj.description')
                    print ("   %s:   %s" % (sect,desc))

