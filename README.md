# projmap

A Python package that simplifies the creation of geographic maps using [Cartopy](https://scitools.org.uk/cartopy/). Projmap handles projection setup, map styling, and common plotting tasks so you can focus on your data. Originally developed for oceanography but applicable to any domain.

## Installation

```bash
pip install projmap
```

## Quick start

```python
import projmap

mp = projmap.Map("westcoast")
mp.nice()
```

`nice()` draws land, ocean background, and country borders in one call.

## Configuration and regions

### Getting started with a settings file

Run this once in your project directory to create a skeleton `settings.toml`:

```python
projmap.init()
```

This creates a `settings.toml` with the `default`, `nwa`, `korea`, and `antarctic` regions as a starting point. To overwrite an existing file, pass `overwrite=True`.

### Settings file format

Maps are defined by *regions* stored in TOML configuration files. Projmap searches for settings in this order:

1. `/etc/projmap/settings.toml`
2. `~/.config/projmap/settings.toml`
3. `./settings.toml` (current directory)
4. Path in the environment variable `PROJMAP_SETTINGS_FILE_FOR_DYNACONF`

Each region is a top-level TOML table with projection parameters and optional styling:

```toml
[myregion]
description = "My custom region"
lat1 = 48.0
lat2 = 62.0
lon1 = -10.0
lon2 = 20.0
projection = "lcc"      # Lambert Conformal Conic

[myregion.style]
oceancolor = "0.15"
landface = "0.6"
landresolution = "10m"  # Natural Earth resolution: 10m, 50m, 110m
```

**Supported projections:** `lcc` (Lambert Conformal), `merc` (Mercator), `eckert4` (Eckert IV), `north_stereo`, `south_stereo`, and Robinson (default).

### Listing and inspecting regions

```python
projmap.show_regions()       # list all available regions across all settings files
projmap.show_region("nwa")   # show all settings for a specific region
```

Projection parameters can also be passed directly to the constructor to override or extend a region:

```python
mp = projmap.Map("default", lat1=48, lat2=62, lon1=-10, lon2=20)
```

## Usage

### Basic map

```python
import projmap

mp = projmap.Map("myregion")
mp.nice()                          # land + ocean + borders
mp.nice(rivers=True, states=True)  # optionally add rivers and state borders
```

### Plotting data

All plotting methods accept lon/lat arrays and pass extra keyword arguments through to the underlying Matplotlib/Cartopy call. A `colorbar` keyword can be added to any of them.

```python
import numpy as np

# Filled contours
mp.contourf(lon, lat, data, levels=20, cmap="RdBu_r", colorbar=True)

# Contour lines with automatic labels on all levels
mp.contour(lon, lat, data, levels=[-1000, -500, -200, -100],
           colors="0.5", linewidths=0.5, clabel=True)

# Contour labels with custom options
mp.contour(lon, lat, data, levels=[-1000, -500, -200, -100],
           colors="0.4", clabel=dict(fontsize=6, fmt=" {:.0f} ".format))

# Pseudocolor
mp.pcolor(lon, lat, data, cmap="viridis", colorbar=True)

# Scatter plot
mp.scatter(lons, lats, c=values, s=10, cmap="plasma", colorbar=True)

# Line / track
mp.plot(lons, lats, color="red", linewidth=1)

# Vector field
mp.streamplot(u, v, lon=lon, lat=lat, color="white", density=1.5)
```

### Multiple subplots

```python
mp = projmap.Map("myregion")
axes = mp.subplots(nrows=1, ncols=2)

mp.pcolor(lon, lat, sst, ax=axes[0], cmap="RdYlBu_r")
mp.contourf(lon, lat, ssh, ax=axes[1], levels=20, cmap="viridis")
```

### Annotations

```python
mp.text(lon, lat, "Label", fontsize=8, color="white")
mp.rectangle(lon1=-5, lat1=50, lon2=10, lat2=58, edgecolor="red", linewidth=1)
```

### Colorbars

```python
mp.contourf(lon, lat, data, cmap="RdBu_r")
mp.colorbar()   # add colorbar after the fact
```

### Tile imagery

```python
import cartopy.io.img_tiles as cimgt

mp = projmap.Map("myregion")
mp.add_tiles(zoom=8)                                       # OpenStreetMap (default)
mp.add_tiles(zoom=10, tile_source=cimgt.Stamen("terrain"))
```

### Styling

```python
mp = projmap.Map("myregion")
mp.set_style(landfill="0.65", landedge="0.4")
mp.nice()
```

Style values can also be set permanently in your `settings.toml`:

```toml
[myregion.style]
landface = "0.65"
landedge = "0.4"
oceancolor = "0.15"
landresolution = "10m"   # Natural Earth resolution: 10m, 50m, 110m
```

### Named locations

Add labelled point markers to a region by defining them in `settings.toml`:

```toml
[[myregion.locations]]
name = "Oslo"
lon = 10.75
lat = 59.91
color = "white"
ha = "left"    # horizontal alignment
va = "bottom"  # vertical alignment
```

They are drawn automatically by `mp.nice()` / `mp.add_locations()`.

## API reference

| Method | Description |
|--------|-------------|
| `Map(region, **proj_kw)` | Create a map for the given region |
| `nice(borders, rivers, states)` | Draw a complete base map |
| `pcolor(lon, lat, data, **kw)` | Pseudocolor plot |
| `contourf(lon, lat, data, **kw)` | Filled contour plot |
| `contour(lon, lat, data, **kw)` | Contour lines (supports `clabel=True`) |
| `scatter(lons, lats, **kw)` | Scatter plot |
| `plot(lons, lats, **kw)` | Line plot |
| `streamplot(u, v, lon, lat, **kw)` | Vector streamlines |
| `hatch(lon, lat, mask, **kw)` | Hatching over masked regions |
| `text(lon, lat, s, **kw)` | Text annotation |
| `rectangle(lon1, lat1, lon2, lat2, **kw)` | Projection-correct rectangle |
| `colorbar(**kw)` | Add horizontal colorbar |
| `add_tiles(zoom, tile_source)` | Add tile imagery |
| `add_land(**kw)` | Draw land features |
| `subplots(nrows, ncols, **kw)` | Create multi-panel figure |
| `set_style(landfill, landedge)` | Override map style |
| `set_extent(**kw)` | Set geographic extent |
| `set_circle_boundary()` | Circular boundary (polar projections) |
| `init(path, overwrite)` | Create a skeleton `settings.toml` in the current directory |
| `show_regions()` | List all available regions |
| `show_region(region)` | Print all settings for a specific region |

All plotting methods accept a `colorbar=True` keyword to add a colorbar, and pass remaining keyword arguments to the underlying Matplotlib/Cartopy function.

## Dependencies

- [Cartopy](https://scitools.org.uk/cartopy/) >= 0.25
- [Matplotlib](https://matplotlib.org/) >= 3.10
- [NumPy](https://numpy.org/) >= 2.4
- [Dynaconf](https://www.dynaconf.com/) >= 3.2
- [matplotlib-scalebar](https://github.com/ppinard/matplotlib-scalebar) >= 0.9
- [xarray](https://xarray.pydata.org/) >= 2026.2
- [netCDF4](https://unidata.github.io/netcdf4-python/) >= 1.7

## License

See [LICENSE](LICENSE) for details.
