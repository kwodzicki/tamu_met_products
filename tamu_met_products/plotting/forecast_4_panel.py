#!/usr/bin/env python3
import logging;
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
import scipy.ndimage as ndimage
import xarray as xr

from metpy.cbook import get_test_data
from metpy.plots import add_metpy_logo

import color_maps;


cbarOpts = {
  'drawedges'   : True,
  'orientation' : 'horizontal'
}
contOpts = {
  'colors'     : 'k', 
  'linewidths' : 2,
  'transform'  : ccrs.PlateCarree()
}

contfOpts = {
  'extend'    : 'both', 
  'zorder'    : 0,
  'transform' : ccrs.PlateCarree()
}
clabOpts = {
  'fontsize'       : 10, 
  'inline'         : 1, 
  'inline_spacing' : 1, 
  'fmt'            : '%i', 
  'rightside_up'   : True
}

################################################################################
def gfs_4_panel( file ):
  '''
  Smaller helper function for getting data into a 'standard' format.
  Just stolen from the the metPy example and can be deleted in future
  '''
  log = logging.getLogger(__name__);
  log.debug('Processing GFS data for plotting')
  ds = xr.open_dataset(get_test_data(file, False))
  lon_2d, lat_2d = np.meshgrid(ds['lon'], ds['lat'])

  temp_sfc = ds['temp'][0]
  temp_sfc.metpy.convert_units('degC')

  wind_300 = ds['winds_300'][0]
  wind_300.metpy.convert_units('knots')

  prcp_wtr = ds['precip_water'][0]
  prcp_wtr.metpy.convert_units('inches')

  return {'long'     : lon_2d,
          'lat'      : lat_2d,
          'time'     : ds['time'][0].dt.strftime('%d %B %Y %H:%MZ'),
          'vort_500' : ds['vort_500'][0] * 1.0e5,
          'temp_sfc' : temp_sfc,
          'wind_300' : wind_300,
          'hght_300' : ndimage.gaussian_filter(ds['heights_300'][0], sigma=1.5, order=0),
          'hght_500' : ndimage.gaussian_filter(ds['heights_500'][0], sigma=1.5, order=0),
          'prcp_wtr' : prcp_wtr}


################################################################################
def plot_basemap(ax, **kwargs):
  '''
  Name:
    plot_basemap
  Purpose:
    A python function to set up base maps for an axis
  Inputs:
    ax    : Axis to plot on
  Keywords:
    Arguments for set_extent, and cartopy cfeatures
  Outputs:
    Returns the update axis object
  '''  
  log        = logging.getLogger(__name__)
  scale      = kwargs.pop( 'scale',      5.0e5 );
  resloution = kwargs.pop( 'resolution', '50m' );
  linewidth  = kwargs.pop( 'linewidth',  0.5 );

  ax.outline_patch.set_visible(False);                                          # Remove frame from plot
  fig_w,fig_h = ax.figure.get_size_inches() * 2.54;                             # Get size of figure in centimeters
  log.debug( 'Figure size: {:5.2f}x{:5.2f}'.format( fig_w, fig_h) );

  ax_x0,ax_y0,ax_w,ax_h = ax._position.bounds;                                  # Get size of axes relative to figure size
  log.debug( 'Axis size:   {:5.3f}x{:5.3f}, {:5.3f}x{:5.3f}'.format( ax_x0, ax_y0, ax_w,  ax_h) );

  dx = scale * (fig_w * ax_w) / 2.0;                                            # Multiply figure width by axis width, divide by 2 and multiply by scale
  dy = scale * (fig_h * ax_h) / 2.0;                                            # Multiply figure height by axis height, divide by 2 and multiply by scale
 
  log.debug( 'Map Extent:   {:5.3f}, {:5.3f}, {:5.3f}, {:5.3f}'.format( -dx, dx, -dy, dy) );

  log.debug('Setting axis extent')  
  ax.set_extent( (-dx, dx, -dy, dy), ax.projection );                           # Set axis extent
  log.debug('Adding coast line')  
  ax.add_feature(cfeature.COASTLINE.with_scale(resloution), linewidth=linewidth)
  log.debug('Adding states')  
  ax.add_feature(cfeature.STATES, linewidth=linewidth)
  log.debug('Adding borders')  
  ax.add_feature(cfeature.BORDERS, linewidth=linewidth)
  return ax

################################################################################
def add_colorbar( mappable, ax, ticks, **kwargs ):
  log = logging.getLogger(__name__);
  log.debug('Creating color bar')
  fontsize = kwargs.pop('fontsize', 8);                                         # Pop off fontsize from keywords
  title    = kwargs.pop('title',    None);
  ax_x0, ax_y0, ax_w, ax_h = ax._position.bounds;                               # Get size of axes relative to figure size
  ax_w  /=  3.0 
  ax_h  /= 40.0
  cb_ax  = ax.figure.add_axes( (ax_x0, ax_y0-3*ax_h, ax_w, ax_h) )
  cbar   = plt.colorbar(mappable, cax=cb_ax, ticks=ticks, **cbarOpts)
  cbar.ax.xaxis.set_ticks_position('top');                                      # Place labels on top of color bar
  if fontsize:
    x_ticks = cbar.ax.get_xticklabels();
    y_ticks = cbar.ax.get_yticklabels()
    cbar.ax.set_xticklabels(x_ticks, fontsize=fontsize)
    cbar.ax.set_yticklabels(y_ticks, fontsize=fontsize)

  if title:
    cbar.set_label(title, size=fontsize)
    
  return cbar;
  
################################################################################
def plot_500hPa_vort_hght_barbs( ax, lon, lat, vort, hght, u=None, v=None, **kwargs ):
  '''
  Name:
    plot_500hPa_vort_hght_barbs
  Purpose:
    A python function to plot a 500 hPa plot like the one in the
    upper left of the HDWX 4-panel plot
  Inputs:
    ax    : Axis to plot on
    lon   : Longitude values for plot
    lat   : Latitude values for plot
    vort  : Vorticity at 500 hPa to plot
    hght  : Geopotential heights at 500 hPa to plot
  Keywords:
    u : u-wind components for wind barbs
    v : v-wind components for wind barbs
  Outputs:
    Returns the filled contour, contour, and colorbar objects
  '''
  log = logging.getLogger(__name__)
  log.info('Creating 500 hPa plot')

  ax = plot_basemap(ax)
  log.debug('Plotting vorticity')
  cf = ax.contourf(lon, lat, vort, 
                         cmap      = color_maps.vort_500['cmap'], 
                         norm      = color_maps.vort_500['norm'],
                         levels    = color_maps.vort_500['lvls'],
                         **contfOpts)

  log.debug('Plotting geopotential height')
  c = ax.contour(lon, lat, hght, **contOpts)
  ax.clabel(c, **clabOpts)
  cbar = add_colorbar( cf, ax, color_maps.vort_500['lvls'], **kwargs )
  
  return cf, c, cbar

################################################################################
def plot_250hPa_isotach_hght_barbs( ax, lon, lat, isotach, hght, u=None, v=None, **kwargs ):
  '''
  Name:
    plot_250hPa_isotach_hght_barbs
  Purpose:
    A python function to plot a 250 hPa plot like the one in the
    upper right of the HDWX 4-panel plot
  Inputs:
    ax      : Axis to plot on
    lon     : Longitude values for plot
    lat     : Latitude values for plot
    isotach : Wind magnitudes at 250 hPa to plot
    hght    : Geopotential heights at 250 hPa to plot
  Keywords:
    u : u-wind components for wind barbs
    v : v-wind components for wind barbs
  Outputs:
    Returns the filled contour, contour, and colorbar objects
  '''
  log = logging.getLogger(__name__)
  log.info('Creating 250 hPa plot')

  ax = plot_basemap(ax)
  log.debug('Plotting winds')
  cf = ax.contourf(lon, lat, isotach, 
                      cmap      = color_maps.wind_250['cmap'], 
                      norm      = color_maps.wind_250['norm'],
                      levels    = color_maps.wind_250['lvls'],
                      **contfOpts)

  log.debug('Plotting geopotential height')
  c = ax.contour(lon, lat, hght, **contOpts)
  ax.clabel(c, **clabOpts)
  cbar = add_colorbar( cf, ax, color_maps.wind_250['lvls'], **kwargs )

  return cf, c, cbar

################################################################################
def plot_850hPa_temp_hght_barbs( ax, lon, lat, temp, hght, u=None, v=None, **kwargs ):
  '''
  Name:
    plot_850hPa_temp_hght_barbs
  Purpose:
    A python function to plot a 850 hPa plot like the one in the
    lower left of the HDWX 4-panel plot
  Inputs:
    ax    : Axis to plot on
    lon   : Longitude values for plot
    lat   : Latitude values for plot
    temp  : temperature at 850 hPa to plot
    hght  : Geopotential heights at 850 hPa to plot
  Keywords:
    u : u-wind components for wind barbs
    v : v-wind components for wind barbs
  Outputs:
    Returns the filled contour, contour, and colorbar objects
  '''
  log = logging.getLogger(__name__)
  log.info('Creating 850 hPa plot')

  ax = plot_basemap(ax)
  log.info('Plotting surface temperature')
  cf = ax.contourf(lon, lat, temp, 
                      cmap      = color_maps.temp_850['cmap'], 
                      norm      = color_maps.temp_850['norm'],
                      levels    = color_maps.temp_850['lvls'],
                      **contfOpts)

  log.debug('Plotting geopotential height')
  c = ax.contour(lon, lat, hght, **contOpts)
  ax.clabel(c, **clabOpts)
  cbar = add_colorbar( cf, ax, color_maps.temp_850['lvls'], **kwargs )

  return cf, c, cbar

################################################################################
def plot_surface( ax, lon, lat, rh, mslp, thickness, u=None, v=None, **kwargs ):
  '''
  Name:
    plot_surface
  Purpose:
    A python function to plot a surface plot like the one in the
    lower right of the HDWX 4-panel plot
  Inputs:
    ax        : Axis to plot on
    lon       : Longitude values for plot
    lat       : Latitude values for plot
    rh        : Relative humidity at 700 hPa
    mslp      : Mean sea-level pressure
    thickness : 1000-500 hPa thickness
  Keywords:
    u : u-wind components for wind barbs
    v : v-wind components for wind barbs
  Outputs:
    Returns the filled contour, contour, and colorbar objects
  '''
  log = logging.getLogger(__name__);
  log.info('Creating surface hPa plot')

  ax = plot_basemap(ax)
  log.info('Plotting precipitable water')
  cf = ax.contourf(data['long'], data['lat'], data['prcp_wtr'], 
                         cmap      = 'Greens',
                         zorder    = 0,
                         transform = transform)

  log.debug('Plotting geopotential height')
  c = ax.contour(lon, lat, mslp, **contOpts)
  ax.clabel(c, **clabOpts)
  cbar = add_colorbar( cf, ax, color_maps.temp_850['lvls'], **kwargs )

  return cf, c, cb
################################################################################
def forecast_4_panel( data, cent_lon = -100.0, cent_lat = 40.0):
  '''
  Name:
    forecast_4_panel
  Purpose:
    A python function to create a plot like the one in the
    HDWX 4-panel plot
  Inputs:
    data : A dictionary (should be xarray in future?) with all variables
            required for the plots. Must set up a convention in the future
  Keywords:
    None.
  Outputs:
    Returns the filled contour, contour, and colorbar objects
  '''
  log = logging.getLogger(__name__);
  log.debug('Plotting 4-panel forecast map')
  map_proj  = ccrs.LambertConformal(central_longitude = cent_lon, 
                                    central_latitude  = cent_lat)
  
  log.debug('Setting up 4-panel plot')
  # Create the figure and plot background on different axes
  fig, axarr = plt.subplots(nrows=2, ncols=2, figsize=(16, 9), 
                            subplot_kw={'projection': map_proj});
  plt.subplots_adjust(
    left   = 0.005, 
    bottom = 0.050, 
    right  = 0.995, 
    top    = 1.000, 
    wspace = 0.050, 
    hspace = 0.100
  )
  
  axlist = axarr.flatten()

  plot_500hPa_vort_hght_barbs(     axlist[0], data['long'], data['lat'], data['vort_500'], data['hght_500'] )
  plot_250hPa_isotach_hght_barbs( axlist[1], data['long'], data['lat'], data['wind_300'], data['hght_300'] )
  plot_850hPa_temp_hght_barbs(    axlist[2], data['long'], data['lat'], data['temp_sfc'], data['hght_500'] )

  # Set figure title
#   fig.suptitle(data['time'], fontsize=24)


if __name__ == "__main__":
  log = logging.getLogger(__name__)
  log.setLevel(logging.INFO)
  srm = logging.StreamHandler()
  srm.setLevel(logging.DEBUG)
  log.addHandler( srm );
  
  file = 'gfs_output.nc'
  data = gfs_4_panel( file )
  forecast_4_panel( data )
#   plt.show()
  plt.savefig('/Users/kwodzicki/4-panel-test.png', dpi = 120)