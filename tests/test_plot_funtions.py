from __future__ import absolute_import, division, print_function
import importlib

import pytest

import numpy as np

import projmap

"""
def grid_attributes(obj):
    assert obj.landmask.dtype == bool
    for attr in ["latvec","lonvec","llon","llat"]:
        assert hasattr(obj, attr)
    assert obj.shape == obj.landmask.shape
    assert obj.shape == obj.llon.shape
    assert obj.shape == obj.llat.shape
    if not hasattr(obj, "_partial_grid"):
        assert obj.landmask[0,0] == True
        assert obj.landmask[obj.jmt//2, obj.imt//2] == False
    
    assert obj.llon.shape[1] == obj.i2 - obj.i1
    assert obj.llat.shape[0] == obj.j2 - obj.j1

def config_attributes(obj):
    for attr in ["defaultjd", "minjd","maxjd","fieldlist","map_region"]:
        assert hasattr(obj, attr)

def setup_object(modulename, classname, **kwargs):
    clss = getattr(importlib.import_module("njord.%s" % modulename), classname)
    obj = clss(**kwargs)
    obj.datadir = "/tmp/njord/tests/"
    config_attributes(obj)
    grid_attributes(obj)
    for fieldname in obj.fieldlist:
        fld = obj.get_field(fieldname)
        assert fld.shape == obj.shape
    return obj
"""

"""    
def test_nasa_9km():
    for instrument in ["MODIS", "VIIRS", "SeaWiFS", "OCTS", "CZCS"]:
        ns = setup_object("nasa", instrument)
        ns = setup_object("nasa", instrument, **llbox)
        assert ns.shape == (242, 242)

def test_nasa_4km():
    for instrument in ["MODIS", "VIIRS"]:
        ns =  setup_object("nasa", instrument, res="4km")
        ns =  setup_object("nasa", instrument, res="4km", **llbox)
        assert ns.shape == (482, 482)
"""

def test_map_skeleton():
        mp = projmap.Map("glob")
        mp.nice()

def test_pcolor():
    latvec = np.arange( -90,  90)
    lonvec = np.arange(-180, 180)
    mp = projmap.Map("glob", )
    fld = np.random.randn(len(latvec), len(lonvec))
    mp.pcolor(lonvec, latvec, fld)

def test_pcolor_preset_latlon():
    latvec = np.arange( -90,  90)
    lonvec = np.arange(-180, 180)
    llon,llat = np.meshgrid(lonvec,latvec)

    mp = projmap.Map("glob", lonobj=llon, latobj=llat)
    fld = np.random.randn(len(latvec), len(lonvec))
    mp.pcolor(fld)

def test_pcolor_preset_latlon_colorbar():
    latvec = np.arange( -90,  90)
    lonvec = np.arange(-180, 180)
    llon,llat = np.meshgrid(lonvec,latvec)

    mp = projmap.Map("glob", lonobj=llon, latobj=llat)
    fld = np.random.randn(len(latvec), len(lonvec))
    mp.pcolor(fld, colorbar=True)

def test_contourf():
    latvec = np.arange( -90,  90)
    lonvec = np.arange(-180, 180)
    llon,llat = np.meshgrid(lonvec,latvec)
    mp = projmap.Map("glob", )
    fld = llat
    mp.contourf(lonvec, latvec, fld)

def test_contourf_preset_latlon():
    latvec = np.arange( -90,  90)
    lonvec = np.arange(-180, 180)
    llon,llat = np.meshgrid(lonvec,latvec)

    mp = projmap.Map("glob", lonobj=llon, latobj=llat)
    fld = llon
    mp.contourf(fld, 100)

def test_contourf_preset_latlon_colorbar():
    latvec = np.arange( -90,  90)
    lonvec = np.arange(-180, 180)
    llon,llat = np.meshgrid(lonvec,latvec)

    mp = projmap.Map("glob", lonobj=llon, latobj=llat)
    fld = llat
    mp.contourf(fld, np.arange(-1,1,0.1), colorbar=True)

def test_rectangle():
    mp = projmap.Map("glob")
    mp.nice()
    mp.rectangle(45, 65, -45,0, step=100, shade="b")

def test_text():
    mp = projmap.Map("glob")
    mp.nice()
    mp.text("testing text")
