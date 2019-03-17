import logging;
import os, json;
import numpy as np;
import matplotlib.pyplot as plt;
import cartopy.crs as ccrs;
from metpy.calc import wind_speed;

from .plot_utils import initFigure, add_colorbar, plot_barbs, plot_basemap, baseLabel, xy_transform, getMapExtentScale;
from . import color_maps;
from . import contour_levels;

dir = os.path.dirname( os.path.dirname(__file__) );
with open( os.path.join(dir, 'plot_opts.json'), 'r' ) as fid:
  opts = json.load(fid);

################################################################################
def plot_srfc_rh_mslp_thick( ax, xx, yy, rh, mslp, hght_1000, hght_500, model, initTime, fcstTime, u=None, v=None, **kwargs ):
  '''
  Name:
    plot_srfc_rh_mslp_thick
  Purpose:
    A python function to plot a surface plot like the one in the
    lower right of the HDWX 4-panel plot
  Inputs:
    ax        : A GeoAxes object for axes to plot data on
    xx        : x-values for plot
    yy        : y-values for plot
    rh        : Reyyive humidity at 700 hPa
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

  transform = kwargs.pop( 'transform', None );                                  # Get transformation for x- and y-values
  if transform is not None:                                                     # If transform is not None, then we must transform the points for plotting
    xx, yy = xy_transform( ax.projection, transform, xx, yy )

  if 'extent' not in kwargs:
    kwargs['extent'], scale = getMapExtentScale(ax, xx, yy)
  ax = plot_basemap(ax, **kwargs);                                              # Set up the basemap, get updated axis and map scale

  thick = hght_500 - hght_1000;                                                 # Compute thickness
  log.info('Plotting thickness')
  cf = ax.contourf(xx, yy, rh, 
                      cmap   = color_maps.surface['cmap'], 
                      norm   = color_maps.surface['norm'],
                      levels = color_maps.surface['lvls'],
                      **opts['contourf_Opts'])
  cbar = add_colorbar( cf, color_maps.surface['lvls'], **kwargs );          # Add colorbar

  c = ax.contour(xx, yy, thick, **contour_levels.thickness);                    # Draw red/blue dashed lines
  ax.clabel(c, **opts['clabel_Opts']);                                          # Update labels

  log.debug('Plotting geopotential height')
  c = ax.contour(xx, yy, mslp.to('hPa'), 
         levels = contour_levels.mslp, 
         **opts['contour_Opts']
      )
  ax.clabel(c, **opts['clabel_Opts'])

  txt = baseLabel( model, initTime, fcstTime );                                 # Get base string for label
  txt.append('700-hPa RH, MSLP, 1000--500-hPa THICK');                          # Update label
  t = ax.text(0.5, 0, '\n'.join( txt ),
                 verticalalignment   = 'top', 
                 horizontalalignment = 'center',
                 transform           = ax.transAxes);                           # Add label to axes

  return cf, c, cbar

################################################################################
def plot_850hPa_temp_hght_barbs( ax, xx, yy, temp, hght, model, initTime, fcstTime, u=None, v=None, **kwargs ):
  '''
  Name:
    plot_850hPa_temp_hght_barbs
  Purpose:
    A python function to plot a 850 hPa plot like the one in the
    lower left of the HDWX 4-panel plot
  Inputs:
    ax       : A GeoAxes object for axes to plot data on
    xx       : x-values for plot
    yy       : y-values for plot
    temp     : temperature at 850 hPa to plot
    hght     : Geopotential heights at 850 hPa to plot
    model    : Name of the model being plotted
    initTime : Initialization time of the model run
    fcstTime : Forecast time of the model run
  Keywords:
    u : u-wind components for wind barbs
    v : v-wind components for wind barbs
    All keywords accecpted by plotting methods. Useful keywords below:
  Outputs:
    Returns the filled contour, contour, and colorbar objects
  '''
  log = logging.getLogger(__name__)
  log.info('Creating 850 hPa plot')

  transform = kwargs.pop( 'transform', None );                                  # Get transformation for x- and y-values
  if transform is not None:                                                     # If transform is not None, then we must transform the points for plotting
    xx, yy = xy_transform( ax.projection, transform, xx, yy )

  if 'extent' not in kwargs:
    kwargs['extent'], scale = getMapExtentScale(ax, xx, yy)
  ax = plot_basemap(ax, **kwargs);                                              # Set up the basemap, get updated axis and map scale

  log.info('Plotting surface temperature')

  cf = ax.contourf(xx, yy, temp.to('degC'), 
                      cmap   = color_maps.temp_850['cmap'], 
                      norm   = color_maps.temp_850['norm'],
                      levels = color_maps.temp_850['lvls'],
                      **opts['contourf_Opts'])
  cbar = add_colorbar( cf, color_maps.temp_850['lvls'], **kwargs );             # Add colorbar

  c1 = ax.contour(xx, yy, temp.to('degC'), 
         levels = 0, colors = (0,0,1), linewidths = 2);                         # Contour for 0 degree C line

  plot_barbs( ax, xx, yy, u, v );                                               # Plot wind barbs
  
  log.debug('Plotting geopotential height')
  c2 = ax.contour(xx, yy, hght, 
          levels = contour_levels.heights['850'],
          **opts['contour_Opts']
      );                                                                        # Contour the geopotential height
  ax.clabel(c2, **opts['clabel_Opts']);                                         # Change contour label settings

  txt = baseLabel( model, initTime, fcstTime );                                 # Get base string for label
  txt.append('850-hPa HEIGHTS, WINDS, TEMP (C)');                               # Update label
  t = ax.text(0.5, 0, '\n'.join( txt ),
                 verticalalignment   = 'top', 
                 horizontalalignment = 'center',
                 transform           = ax.transAxes)                            # Add label to axes

  return cf, (c1, c2), cbar

################################################################################
def plot_500hPa_vort_hght_barbs( ax, xx, yy, vort, hght, model, initTime, fcstTime, u=None, v=None, **kwargs ):
  '''
  Name:
    plot_500hPa_vort_hght_barbs
  Purpose:
    A python function to plot a 500 hPa plot like the one in the
    upper left of the HDWX 4-panel plot
  Inputs:
    ax       : A GeoAxes object for axes to plot data on
    xx       : x-values for plot
    yy       : y-values for plot
    vort     : Vorticity at 500 hPa to plot
    hght     : Geopotential heights at 500 hPa to plot
    model    : Name of the model being plotted
    initTime : Initialization time of the model run
    fcstTime : Forecast time of the model run
  Keywords:
    u : u-wind components for wind barbs
    v : v-wind components for wind barbs
    All keywords accecpted by plotting methods. Useful keywords below:
      ax    : A GeoAxes object for axes to plot data on
  Outputs:
    Returns the filled contour, contour, and colorbar objects
  '''
  log = logging.getLogger(__name__)
  log.info('Creating 500 hPa plot')

  transform = kwargs.pop( 'transform', None );                                  # Get transformation for x- and y-values
  if transform is not None:                                                     # If transform is not None, then we must transform the points for plotting
    xx, yy = xy_transform( ax.projection, transform, xx, yy )

  if 'extent' not in kwargs:
    kwargs['extent'], scale = getMapExtentScale(ax, xx, yy)
  ax = plot_basemap(ax, **kwargs);                                              # Set up the basemap, get updated axis and map scale

  log.debug('Plotting vorticity') 
  if vort.max().m < 1.0: vort *= 1.0e5;                                         # If vorticity values too small, scale them
  cf = ax.contourf(xx, yy, vort, 
                         cmap   = color_maps.vort_500['cmap'], 
                         norm   = color_maps.vort_500['norm'],
                         levels = color_maps.vort_500['lvls'],
                         **opts['contourf_Opts'])
  cbar = add_colorbar( cf, color_maps.vort_500['lvls'], **kwargs );             # Add a color bar

  plot_barbs( ax, xx, yy, u, v );                                               # Plot wind barbs
    
  log.debug('Plotting geopotential height')
  c = ax.contour(xx, yy, hght, 
         levels = contour_levels.heights['500'],
         **opts['contour_Opts']
      );                                                                        # Contour the geopotential height
  ax.clabel(c, **opts['clabel_Opts']);                                          # Change contour label settings
  
  txt = baseLabel( model, initTime, fcstTime );                                 # Get base string for label
  txt.append('500-hPa HEIGHTS, WINDS, ABS VORT');                               # Update Label 
  t = ax.text(0.5, 0, '\n'.join( txt ),
                 verticalalignment   = 'top', 
                 horizontalalignment = 'center',
                 transform           = ax.transAxes);                           # Add label to axes

  return cf, c, cbar;

################################################################################
def plot_250hPa_isotach_hght_barbs( ax, xx, yy, u, v, hght, model, initTime, fcstTime, **kwargs ):
  '''
  Name:
    plot_250hPa_isotach_hght_barbs
  Purpose:
    A python function to plot a 250 hPa plot like the one in the
    upper right of the HDWX 4-panel plot
  Inputs:
    ax       : A GeoAxes object for axes to plot data on
    xx       : x-values for plot
    yy       : y-values for plot
    u        : U-wind component
    v        : V-wind component
    hght     : Geopotential heights at 250 hPa to plot
    model    : Name of the model being plotted
    initTime : Initialization time of the model run
    fcstTime : Forecast time of the model run
  Keywords:
    All keywords accecpted by plotting methods. Useful keywords below:
      ax    : A GeoAxes object for axes to plot data on
  Outputs:
    Returns the filled contour, contour, and colorbar objects
  '''
  log = logging.getLogger(__name__)
  log.info('Creating 250 hPa plot')

  transform = kwargs.pop( 'transform', None );                                  # Get transformation for x- and y-values
  if transform is not None:                                                     # If transform is not None, then we must transform the points for plotting
    xx, yy = xy_transform( ax.projection, transform, xx, yy )

  if 'extent' not in kwargs:
    kwargs['extent'], scale = getMapExtentScale(ax, xx, yy)
  ax = plot_basemap(ax, **kwargs);                                              # Set up the basemap, get updated axis and map scale

  log.debug('Plotting winds')
  isotach = wind_speed( u, v ).to('kts');                                       # Compute windspeed and convert to knots
  cf = ax.contourf(xx, yy, isotach, 
                      cmap   = color_maps.wind_250['cmap'], 
                      norm   = color_maps.wind_250['norm'],
                      levels = color_maps.wind_250['lvls'],
                      **opts['contourf_Opts'])
  cbar = add_colorbar( cf, color_maps.wind_250['lvls'], **kwargs );             # Add a color bar

  plot_barbs( ax, xx, yy, u, v );                                               # Plot wind barbs
 
  log.debug('Plotting geopotential height')
  c = ax.contour(xx, yy, hght, 
         levels = contour_levels.heights['250'],
         **opts['contour_Opts']
      );                                                                        # Contour the geopotential height
  ax.clabel(c, **opts['clabel_Opts']);                                          # Change contour label settings

  txt = baseLabel( model, initTime, fcstTime );                                 # Get base string for label
  txt.append('250-hPa HEIGHTS, WINDS, ISOTACHS (KT)');                          # Update label
  t = ax.text(0.5, 0, '\n'.join( txt ),
                 verticalalignment   = 'top', 
                 horizontalalignment = 'center',
                 transform           = ax.transAxes);                           # Add label to axes

  return cf, c, cbar