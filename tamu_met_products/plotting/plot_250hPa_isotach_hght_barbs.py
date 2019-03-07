import logging;
import os, json;
import cartopy.crs as ccrs;
from metpy.calc import wind_speed;

from .plot_utils import add_colorbar, plot_barbs, plot_basemap, baseLabel;
from . import color_maps;

dir = os.path.dirname( os.path.realpath(__file__) );
with open( os.path.join( dir, 'plot_opts.json' ), 'r' ) as fid:
  opts = json.load(fid);
  

################################################################################
def plot_250hPa_isotach_hght_barbs( ax, lon, lat, u, v, hght, model, initTime, fcstTime, **kwargs ):
  '''
  Name:
    plot_250hPa_isotach_hght_barbs
  Purpose:
    A python function to plot a 250 hPa plot like the one in the
    upper right of the HDWX 4-panel plot
  Inputs:
    ax       : Axis to plot on
    lon      : Longitude values for plot
    lat      : Latitude values for plot
    u        : U-wind component
    v        : V-wind component
    hght     : Geopotential heights at 250 hPa to plot
    model    : Name of the model being plotted
    initTime : Initialization time of the model run
    fcstTime : Forecast time of the model run
  Keywords:
    u : u-wind components for wind barbs
    v : v-wind components for wind barbs
  Outputs:
    Returns the filled contour, contour, and colorbar objects
  '''
  log = logging.getLogger(__name__)
  log.info('Creating 250 hPa plot')
  projection = kwargs.pop( 'projection', ccrs.PlateCarree() );                  # Get default data projection

  xyz = ax.projection.transform_points(projection, lon.m, lat.m);               # Project longitude/latitude to map; cuts down on projecting multiple times
  xx  = xyz[:,:,0];                                                             # Get re-projected longitudes
  yy  = xyz[:,:,1];                                                             # Get re-projected latitudes

  ax, scale = plot_basemap(ax);                                                 # Set up the basemap, get updated axis and map scale

  log.debug('Plotting winds')
  isotach = wind_speed( u, v ).to('kts');                                       # Compute windspeed and convert to knots
  cf = ax.contourf(xx, yy, isotach, 
                      cmap      = color_maps.wind_250['cmap'], 
                      norm      = color_maps.wind_250['norm'],
                      levels    = color_maps.wind_250['lvls'],
                      **opts['contourf_Opts'])

  plot_barbs( ax, scale, xx, yy, u, v );                                        # Plot wind barbs
 
  log.debug('Plotting geopotential height')
  c = ax.contour(lon, lat, hght, **opts['contour_Opts']);                       # Contour the geopotential height
  ax.clabel(c, **opts['clabel_Opts']);                                          # Change contour label settings
  cbar = add_colorbar( cf, ax, color_maps.wind_250['lvls'], **kwargs );         # Add a color bar

  txt = baseLabel( model, initTime, fcstTime );                                 # Get base string for label
  txt.append('250-hPa HEIGHTS, WINDS, ISOTACHS (KT)');                          # Update label
  t = ax.text(0.5, 0, '\n'.join( txt ),
                 verticalalignment   = 'top', 
                 horizontalalignment = 'center',
                 transform           = ax.transAxes);                           # Add label to axes

  return cf, c, cbar
