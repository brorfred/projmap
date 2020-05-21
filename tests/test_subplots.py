
import numpy as np
import projmap

def test_nice_noax():
    lon = np.linspace(-180,180,50)
    lat = np.linspace(45,85,50)
    mp = projmap.Map("arctic")
    mp.subplots(1,3)
    for ax,kind in enumerate(["first","number","last"]): 
        sarr = np.random.rand(50,50)*5 - 2.5
        mp.set_extent(lat1=45, ax=ax)
        mp.set_circle_boundary(ax=ax)
        mp.pcolor(lon, lat, sarr, ax=ax)
        mp.nice()

def test_nice_ax():
    lon = np.linspace(-180,180,50)
    lat = np.linspace(45,85,50)
    mp = projmap.Map("arctic")
    mp.subplots(1,3)
    for ax,kind in enumerate(["first","number","last"]):
        sarr = np.random.rand(50,50)*5 - 2.5
        mp.set_extent(lat1=45, ax=ax)
        mp.set_circle_boundary(ax=ax)
        mp.pcolor(lon, lat, sarr, ax=ax)
        mp.nice(ax=ax)

def test_bling():

    cmap = cm.RdBu_r
    vmin = -2.5
    vmax = 2.5

    lon = np.linspace(-180,180,50)
    lat = np.linspace(45,85,50)
    mp = projmap.Map("arctic")
    mp.subplots(1,3)
    pl.subplots_adjust(wspace=0.05,hspace=0.5)
    titles = ["A", "B", "C"]
    for ax,kind in enumerate(["first","number","last"]):
        sarr = np.random.rand(50,50)*5 - 2.5
        mp.set_extent(lat1=45, ax=ax)
        mp.set_circle_boundary(ax=ax)
        mp.pcolor(lon, lat, sarr, cmap=cmap, vmin=vmin, vmax=vmax,
                  ax=ax, rasterized=True)
        mp.nice()
        mp.text(225, 40, titles[ax], ax=ax)
    mp.fig.colorbar(mp._im, ax=mp.axes.ravel().tolist(),
                    shrink=0.5, orientation="horizontal", pad=0.05)
