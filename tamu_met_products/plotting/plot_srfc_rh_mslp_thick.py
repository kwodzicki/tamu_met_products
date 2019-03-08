import logging;
import os, json;
import numpy as np;
import cartopy.crs as ccrs;
from .plot_utils import add_colorbar, plot_barbs, plot_basemap, baseLabel;
from . import color_maps;

dir = os.path.dirname( os.path.realpath(__file__) );
with open( os.path.join( dir, 'plot_opts.json' ), 'r' ) as fid:
  opts = json.load(fid);

thickness_lvls  = np.arange(-25, 26) 
thickness_width = (thickness_lvls == 0)*2 + 1;

thickness_clr   = np.full(thickness_lvls.size, 'r')
thickness_clr[thickness_lvls < 0] = 'b'

thickness_sty   = np.full(thickness_lvls.size, 'dashed')
thickness_sty[thickness_lvls == 0] = 'solid'

thickness_lvls  = thickness_lvls * 40 + 5500


mslp_lvls = np.arange(-25, 26) * 4 + 1016

################################################################################
def plot_srfc_rh_mslp_thick( ax, lon, lat, rh, mslp, hght_1000, hght_500, model, initTime, fcstTime, u=None, v=None, **kwargs ):
  '''
  Name:
    plot_srfc_rh_mslp_thick
  Purpose:
    A python function to plot a surface plot like the one in the
    lower right of the HDWX 4-panel plot
  Inputs:
    ax        : Axis to plot on
    lon       : Longitude values for plot
    lat       : Latitude values for plot
    rh        : Relative humidity at 700 hPa
    mslp      : Mean sea-level pressure
    hght_1000 : Height of the 1000 hPa 
    hght_500  : Height of the 500 hPa 
    model     : Name of the model being plotted
    initTime  : Initialization time of the model run
    fcstTime  : Forecast time of the model run
  Keywords:
    u : u-wind components for wind barbs
    v : v-wind components for wind barbs
  Outputs:
    Returns the filled contour, contour, and colorbar objects
  '''
  log = logging.getLogger(__name__);
  log.info('Creating surface hPa plot')
  projection = kwargs.pop( 'projection', ccrs.PlateCarree() );                  # Get default data projection
  
  xyz = ax.projection.transform_points(projection, lon.m, lat.m);               # Project longitude/latitude to map; cuts down on projecting multiple times
  xx  = xyz[:,:,0];                                                             # Get re-projected longitudes
  yy  = xyz[:,:,1];                                                             # Get re-projected latitudes

  ax, scale = plot_basemap(ax);                                                 # Set up the basemap, get updated axis and map scale

  thick = hght_500 - hght_1000;                                                 # Compute thickness
  log.info('Plotting thickness')
  cf = ax.contourf(xx, yy, rh, 
                      cmap      = color_maps.surface['cmap'], 
                      norm      = color_maps.surface['norm'],
                      levels    = color_maps.surface['lvls'],
                      **opts['contourf_Opts'])
  c = ax.contour(xx, yy, thick, 
       levels     = thickness_lvls,
       linewidths = thickness_width,
       linestyles = thickness_sty,
       colors     = thickness_clr  
  );                                                                            # Draw red/blue dashed lines
  ax.clabel(c, **opts['clabel_Opts']);                                          # Update labels

  log.debug('Plotting geopotential height')
  c = ax.contour(xx, yy, mslp.to('hPa'), 
       levels    = mslp_lvls, 
       **opts['contour_Opts'])
  ax.clabel(c, **opts['clabel_Opts'])
  cbar = add_colorbar( cf, ax, color_maps.surface['lvls'], **kwargs );          # Add colorbar

  txt = baseLabel( model, initTime, fcstTime );                                 # Get base string for label
  txt.append('700-hPa RH, MSLP, 1000--500-hPa THICK');                          # Update label
  t = ax.text(0.5, 0, '\n'.join( txt ),
                 verticalalignment   = 'top', 
                 horizontalalignment = 'center',
                 transform           = ax.transAxes);                           # Add label to axes

  return cf, c, cbar