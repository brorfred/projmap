
 === projmap ===
A wrapper to matplotlib's Basemap module to make the usage of a map
for a specific project or region simpler and more dependable. Projmap
allows you to define all the parameters necessary to initiate Basemap
in a config file. The package also has functions to nice looking maps
with only one command.

 == Installation ==
pip install --user -e git+https://github.com/brorfred/projmap.git#egg=projmap

 == Usage ==

 = Define a project in one of the following files: =

./region_maps.cfg
~/.region_maps.cfg

An example project can look like this:

[safr]     #The handle the project
proj.description: Southern Ocean south of South Africa #Long description
base.projection:  stere    # Settings for the basemap class
base.llcrnrlon:   -70      # All keywords can be used
base.llcrnrlat:   -60      # Read more at
base.urcrnrlat:   -20      # http://matplotlib.org/basemap/users/mapsetup.html
base.urcrnrlon:    30      #
base.lat_0:       -40      # Remember to begin all keyworrds with 'base.'
base.lon_0:         0      #
base.resolution:    i      # 
proj.merid:        [-60, -40, -20, 0, 20, 40]   # Where to draw meridians
proj.paral:        [-60, -50, -40, -30]         # Where to drar parallels


Example of usage:

>>> import projmap 
>>>
>>> #list all available regions
>>> projmap.list()  
>>> #lists all settings for a region
>>> projmap.list('  #handle') 
>>>
>>> #Create a map instance
>>> mp = projmap.Projmap('handle')
>>>
>>> #Make a nice looking map
>>> mp.nice()