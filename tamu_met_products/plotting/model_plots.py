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
def plot_rh_mslp_thick( ax, data, **kwargs ):
  '''
  Name:
    plot_srfc_rh_mslp_thick
  Purpose:
    A python function to plot a surface plot like the one in the
    lower right of the HDWX 4-panel plot
  Inputs:
    ax       : A GeoAxes object for axes to plot data on
    data     : Dictionary with all data plot
  Keywords:
    u : u-wind components for wind barbs
    v : v-wind components for wind barbs
  Outputs:
    Returns the filled contour, contour, and colorbar objects
  '''
  log = logging.getLogger(__name__);
  log.info('Creating surface hPa plot')

  if 'lon' not in data:
    log.error('No longitude values in data')
    return None, None, None;
  elif 'lat' not in data:
    log.error('No latitude values in data')
    return None, None, None;

  transform = kwargs.pop( 'transform', None );                                  # Get transformation for x- and y-values
  if transform is not None:                                                     # If transform is not None, then we must transform the points for plotting
    xx, yy = xy_transform( ax.projection, transform, data['lon'], data['lat'] )
  else:
    xx, yy = data['lon'], data['lat']
  if 'extent' not in kwargs:
    kwargs['extent'], scale = getMapExtentScale(ax, xx, yy)
  ax = plot_basemap(ax, **kwargs);                                              # Set up the basemap, get updated axis and map scale

  if ('rh 700.0MB' not in data):
    log.error('No relative humidity data')
    cf = cbar = None;
  else:                                                                         # Else, required variables in dictionary
    log.debug('Plotting relative humidity')
    cf = ax.contourf(xx, yy, data['rh 700.0MB'], 
                      cmap   = color_maps.surface['cmap'], 
                      norm   = color_maps.surface['norm'],
                      levels = color_maps.surface['lvls'],
                      **opts['contourf_Opts'])
    cbar = add_colorbar( cf, color_maps.surface['lvls'], **kwargs );            # Add colorbar

  if ('geo_hght 1000.0MB' not in data) or ('geo_hght 500.0MB' not in data):     # If the required geopotential heights are NOT in dictionary
    log.error('No geopotential height info at 1000 hPa or 500 hPa')
    c = None;
  else:                                                                         # Else, required variables in dictionary
    thick  = data['geo_hght 500.0MB'].to('meter').m;
    thick -= data['geo_hght 1000.0MB'].to('meter').m;                           # Compute thickness
    c      = ax.contour(xx, yy, thick, **contour_levels.thickness);             # Draw red/blue dashed lines
    ax.clabel(c, **opts['clabel_Opts']);                                        # Update labels

  if ('mslp 0.0MSL' not in data):                                               # If mean sea level pressure data NOT in dictionary
    log.error('No mean sea level pressure data')
    c = None
  else:                                                                         # Else, required variables in dictionary
    log.debug('Plotting mean sea level pressure')
    c = ax.contour(xx, yy, data['mslp 0.0MSL'].to('hPa').m, 
         levels = contour_levels.mslp, 
         **opts['contour_Opts']
        )
    ax.clabel(c, **opts['clabel_Opts'])

  txt = baseLabel( data['model'], data['initTime'], data['fcstTime'] );         # Get base string for label
  txt.append('700-hPa RH, MSLP, 1000--500-hPa THICK');                          # Update label
  t = ax.text(0.5, 0, '\n'.join( txt ),
                 verticalalignment   = 'top', 
                 horizontalalignment = 'center',
                 transform           = ax.transAxes);                           # Add label to axes

  return cf, c, cbar

################################################################################
def plot_srfc_temp_barbs( ax, data, **kwargs ):
  '''
  Name:
    plot_srfc_temp_barbs
  Purpose:
    A python function to plot 2 meter temperature and 10 meter wind barbs
  Inputs:
    ax       : A GeoAxes object for axes to plot data on
    data     : Dictionary with all data plot
  Keywords:
    u : u-wind components for wind barbs
    v : v-wind components for wind barbs
  Outputs:
    Returns the filled contour, contour, and colorbar objects
  '''
  log = logging.getLogger(__name__);
  log.info('Creating surface hPa plot')

  if 'lon' not in data:
    log.error('No longitude values in data')
    return None, None, None;
  elif 'lat' not in data:
    log.error('No latitude values in data')
    return None, None, None;

  transform = kwargs.pop( 'transform', None );                                  # Get transformation for x- and y-values
  if transform is not None:                                                     # If transform is not None, then we must transform the points for plotting
    xx, yy = xy_transform( ax.projection, transform, data['lon'], data['lat'] )
  else:
    xx, yy = data['lon'], data['lat']
  if 'extent' not in kwargs:
    kwargs['extent'], scale = getMapExtentScale(ax, xx, yy)
  ax = plot_basemap(ax, **kwargs);                                              # Set up the basemap, get updated axis and map scale

  if ('temp 2.0FHAG' not in data):
    log.error('No temperature data')
    cf = cbar = None;
  else:                                                                         # Else, required variables in dictionary
    log.debug('Plotting temperature data')
    cf = ax.contourf(xx, yy, data['temp 2.0FHAG'].to('degF').m, 
                      cmap   = color_maps.temp_2m['cmap'], 
                      norm   = color_maps.temp_2m['norm'],
                      levels = color_maps.temp_2m['lvls'],
                      **opts['contourf_Opts'])
    cbar = add_colorbar( cf, color_maps.temp_2m['lvls'], **kwargs );            # Add colorbar

  if ('u_wind 10.0FHAG' not in data) or ('v_wind 10.0FHAG' not in data):
    log.error('Missing wind component(s)!')
  else:
    plot_barbs( ax, xx, yy, data['u_wind 10.0FHAG'], data['v_wind 10.0FHAG'] ); # Plot wind barbs

  txt = baseLabel( data['model'], data['initTime'], data['fcstTime'] );         # Get base string for label
  txt.append('2-M TEMP (F) AND 10-M WINDS');                                    # Update label
  t = ax.text(0.5, 0, '\n'.join( txt ),
                 verticalalignment   = 'top', 
                 horizontalalignment = 'center',
                 transform           = ax.transAxes);                           # Add label to axes

  return cf, None, cbar

################################################################################
def plot_1000hPa_theta_e_barbs( ax, data, **kwargs ):
  '''
  Name:
    plot_1000hPa_theta_e_barbs
  Purpose:
    A python function to plot a 1000 hPa equivalent potential temperature and
    winds
  Inputs:
    ax       : A GeoAxes object for axes to plot data on
    data     : Dictionary with all data plot
  Keywords:
    u : u-wind components for wind barbs
    v : v-wind components for wind barbs
  Outputs:
    Returns the filled contour, contour, and colorbar objects
  '''
  log = logging.getLogger(__name__);
  log.info('Creating surface hPa plot')

  if 'lon' not in data:
    log.error('No longitude values in data')
    return None, None, None;
  elif 'lat' not in data:
    log.error('No latitude values in data')
    return None, None, None;

  transform = kwargs.pop( 'transform', None );                                  # Get transformation for x- and y-values
  if transform is not None:                                                     # If transform is not None, then we must transform the points for plotting
    xx, yy = xy_transform( ax.projection, transform, data['lon'], data['lat'] )
  else:
    xx, yy = data['lon'], data['lat']
  if 'extent' not in kwargs:
    kwargs['extent'], scale = getMapExtentScale(ax, xx, yy)
  ax = plot_basemap(ax, **kwargs);                                              # Set up the basemap, get updated axis and map scale

  if ('theta_e 1000.0MB' not in data):
    log.error('No equivalent potential temperature data')
    cf = cbar = None;
  else:                                                                         # Else, required variables in dictionary
    log.debug('Plotting relative humidity')
    cf = ax.contourf(xx, yy, data['theta_e 1000.0MB'].to('K').m, 
                      cmap   = color_maps.theta_e_1000['cmap'], 
                      norm   = color_maps.theta_e_1000['norm'],
                      levels = color_maps.theta_e_1000['lvls'],
                      **opts['contourf_Opts'])
    cbar = add_colorbar( cf, color_maps.theta_e_1000['lvls'], **kwargs );       # Add colorbar

  if ('u_wind 1000.0MB' not in data) or ('v_wind 1000.0MB' not in data):
    log.error('Missing wind component(s)!')
  else:
    plot_barbs( ax, xx, yy, data['u_wind 1000.0MB'], data['v_wind 1000.0MB'] ); # Plot wind barbs

  txt = baseLabel( data['model'], data['initTime'], data['fcstTime'] );         # Get base string for label
  txt.append('1000-hPa EQUIVALENT POTENTIAL TEMPERATURE AND WINDS');            # Update label
  t = ax.text(0.5, 0, '\n'.join( txt ),
                 verticalalignment   = 'top', 
                 horizontalalignment = 'center',
                 transform           = ax.transAxes);                           # Add label to axes

  return cf, None, cbar

################################################################################
def plot_850hPa_temp_hght_barbs( ax, data, **kwargs ):
  '''
  Name:
    plot_850hPa_temp_hght_barbs
  Purpose:
    A python function to plot a 850 hPa plot like the one in the
    lower left of the HDWX 4-panel plot
  Inputs:
    ax       : A GeoAxes object for axes to plot data on
    data     : Dictionary with all data plot
  Keywords:
    u : u-wind components for wind barbs
    v : v-wind components for wind barbs
    All keywords accecpted by plotting methods. Useful keywords below:
  Outputs:
    Returns the filled contour, contour, and colorbar objects
  '''
  log = logging.getLogger(__name__)
  log.info('Creating 850 hPa plot')

  if 'lon' not in data:
    log.error('No longitude values in data')
    return None, None, None;
  elif 'lat' not in data:
    log.error('No latitude values in data')
    return None, None, None;

  transform = kwargs.pop( 'transform', None );                                  # Get transformation for x- and y-values
  if transform is not None:                                                     # If transform is not None, then we must transform the points for plotting
    xx, yy = xy_transform( ax.projection, transform, data['lon'], data['lat'] )
  else:
    xx, yy = data['lon'], data['lat']

  if 'extent' not in kwargs:
    kwargs['extent'], scale = getMapExtentScale(ax, xx, yy)
  ax = plot_basemap(ax, **kwargs);                                              # Set up the basemap, get updated axis and map scale

  if ('temp 850.0MB' not in data):
    log.error('No temperature data!')
    cf = cbar = c1 = None;
  else:
    log.debug('Plotting surface temperature')
    temp = data['temp 850.0MB'].to('degC')
    cf   = ax.contourf(xx, yy, temp.m, 
                      cmap   = color_maps.temp_850['cmap'], 
                      norm   = color_maps.temp_850['norm'],
                      levels = color_maps.temp_850['lvls'],
                      **opts['contourf_Opts'])
    cbar = add_colorbar( cf, color_maps.temp_850['lvls'], **kwargs );           # Add colorbar
    c1   = ax.contour(xx, yy, temp.m, 
           levels = 0, colors = (0,0,1), linewidths = 2);                       # Contour for 0 degree C line
  
  if ('geo_hght 850.0MB' not in data):
    log.error('No geopotential height data!')
    c2 = None
  else:
    log.debug('Plotting geopotential height')
    c2 = ax.contour(xx, yy, data['geo_hght 850.0MB'].to('meter').m, 
          levels = contour_levels.heights['850'],
          **opts['contour_Opts']
        );                                                                      # Contour the geopotential height
    ax.clabel(c2, **opts['clabel_Opts']);                                       # Change contour label settings

  if ('u_wind 850.0MB' not in data) or ('v_wind 850.0MB' not in data):
    log.error('Missing wind component(s)!')
  else:
    plot_barbs( ax, xx, yy, data['u_wind 850.0MB'], data['v_wind 850.0MB'] );   # Plot wind barbs

  txt = baseLabel( data['model'], data['initTime'], data['fcstTime'] );         # Get base string for label
  txt.append('850-hPa HEIGHTS, WINDS, TEMP (C)');                               # Update label
  t = ax.text(0.5, 0, '\n'.join( txt ),
                 verticalalignment   = 'top', 
                 horizontalalignment = 'center',
                 transform           = ax.transAxes)                            # Add label to axes

  return cf, (c1, c2), cbar

################################################################################
def plot_500hPa_vort_hght_barbs( ax, data, **kwargs ):
  '''
  Name:
    plot_500hPa_vort_hght_barbs
  Purpose:
    A python function to plot a 500 hPa plot like the one in the
    upper left of the HDWX 4-panel plot
  Inputs:
    ax       : A GeoAxes object for axes to plot data on
    data     : Dictionary with all data plot
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

  if 'lon' not in data:
    log.error('No longitude values in data')
    return None, None, None;
  elif 'lat' not in data:
    log.error('No latitude values in data')
    return None, None, None;
  
  transform = kwargs.pop( 'transform', None );                                  # Get transformation for x- and y-values
  if transform is not None:                                                     # If transform is not None, then we must transform the points for plotting
    xx, yy = xy_transform( ax.projection, transform, data['lon'], data['lat'] )
  else:
    xx, yy = data['lon'], data['lat']

  if 'extent' not in kwargs:
    kwargs['extent'], scale = getMapExtentScale(ax, xx, yy)
  ax = plot_basemap(ax, **kwargs);                                              # Set up the basemap, get updated axis and map scale

  if 'abs_vor 500.0MB' not in data:
    log.error('No voriticity data!');
    cf = cbar = None;
  else:
    log.debug('Plotting vorticity') 
    cf = ax.contourf(xx, yy, data['abs_vor 500.0MB'].m * 1.0e5, 
                         cmap   = color_maps.vort_500['cmap'], 
                         norm   = color_maps.vort_500['norm'],
                         levels = color_maps.vort_500['lvls'],
                         **opts['contourf_Opts'])
    cbar = add_colorbar( cf, color_maps.vort_500['lvls'], **kwargs );             # Add a color bar
 
  if 'geo_hght 500.0MB' not in data:
    log.error('No geopotential height data')
    c = None;
  else:  
    log.debug('Plotting geopotential height')
    c = ax.contour(xx, yy, data['geo_hght 500.0MB'].to('meter').m, 
         levels = contour_levels.heights['500'],
         **opts['contour_Opts']
        );                                                                        # Contour the geopotential height
    ax.clabel(c, **opts['clabel_Opts']);                                          # Change contour label settings
 
  if ('u_wind 500.0MB' not in data) or ('v_wind 500.0MB' not in data):
    log.error('Missing wind component(s)!')
  else:
    plot_barbs( ax, xx, yy, data['u_wind 500.0MB'], data['v_wind 500.0MB'] );   # Plot wind barbs
  
  txt = baseLabel( data['model'], data['initTime'], data['fcstTime'] );                         # Get base string for label
  txt.append('500-hPa HEIGHTS, WINDS, ABS VORT');                               # Update Label 
  t = ax.text(0.5, 0, '\n'.join( txt ),
                 verticalalignment   = 'top', 
                 horizontalalignment = 'center',
                 transform           = ax.transAxes);                           # Add label to axes

  return cf, c, cbar;

################################################################################
def plot_250hPa_isotach_hght_barbs( ax, data, **kwargs ):
  '''
  Name:
    plot_250hPa_isotach_hght_barbs
  Purpose:
    A python function to plot a 250 hPa plot like the one in the
    upper right of the HDWX 4-panel plot
  Inputs:
    ax       : A GeoAxes object for axes to plot data on
    data     : Dictionary with all data plot
  Keywords:
    All keywords accecpted by plotting methods. Useful keywords below:
      ax    : A GeoAxes object for axes to plot data on
  Outputs:
    Returns the filled contour, contour, and colorbar objects
  '''
  log = logging.getLogger(__name__)
  log.info('Creating 250 hPa plot')

  if 'lon' not in data:
    log.error('No longitude values in data')
    return None, None, None;
  elif 'lat' not in data:
    log.error('No latitude values in data')
    return None, None, None;

  transform = kwargs.pop( 'transform', None );                                  # Get transformation for x- and y-values
  if transform is not None:                                                     # If transform is not None, then we must transform the points for plotting
    xx, yy = xy_transform( ax.projection, transform, data['lon'], data['lat'] )
  else:
    xx, yy = data['lon'], data['lat']

  if 'extent' not in kwargs:
    kwargs['extent'], scale = getMapExtentScale(ax, xx, yy)
  ax = plot_basemap(ax, **kwargs);                                              # Set up the basemap, get updated axis and map scale

  if ('u_wind 250.0MB' not in data) or ('v_wind 250.0MB' not in data):
    log.error('Missing u- or v-wind component')
    cf = cb = None;
  else:
    log.debug('Plotting isotachs')
    isotach = wind_speed( data['u_wind 250.0MB'], data['v_wind 250.0MB'] );     # Compute windspeed and convert to knots
    cf      = ax.contourf(xx, yy, isotach.to('kts').m, 
                      cmap   = color_maps.wind_250['cmap'], 
                      norm   = color_maps.wind_250['norm'],
                      levels = color_maps.wind_250['lvls'],
                      **opts['contourf_Opts'])
    cbar    = add_colorbar( cf, color_maps.wind_250['lvls'], **kwargs );        # Add a color bar
 
  if ('geo_hght 250.0MB' not in data):
    log.error('No geopotential height data')
    c = None;
  else:
    log.debug('Plotting geopotential height')
    c = ax.contour(xx, yy, data['geo_hght 250.0MB'].to('meter').m, 
           levels = contour_levels.heights['250'],
           **opts['contour_Opts']
       );                                                                       # Contour the geopotential height
    ax.clabel(c, **opts['clabel_Opts']);                                        # Change contour label settings

  if cf is not None:                                                            # If cf is not None, that means the u- and v-winds exist
    plot_barbs( ax, xx, yy, data['u_wind 250.0MB'], data['v_wind 250.0MB'] );   # Plot wind barbs

  txt = baseLabel( data['model'], data['initTime'], data['fcstTime'] );         # Get base string for label
  txt.append('250-hPa HEIGHTS, WINDS, ISOTACHS (KT)');                          # Update label
  t = ax.text(0.5, 0, '\n'.join( txt ),
                 verticalalignment   = 'top', 
                 horizontalalignment = 'center',
                 transform           = ax.transAxes);                           # Add label to axes

  return cf, c, cbar