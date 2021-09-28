import logging;
import os, json;
import numpy as np;
import matplotlib.pyplot as plt;
import cartopy.crs as ccrs;
from metpy.calc import wind_speed;

from .plot_utils import (
  initFigure, 
  add_colorbar, 
  plot_barbs, 
  plot_basemap, 
  baseLabel, 
  xy_transform, 
  getMapExtentScale
);
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
    Various
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

  cf = c = cbar = None
  if 'rh' not in data:
    log.error( 'No relative humidity data')
  elif '700.0MB' not in data['rh']:
    log.error( 'No relative humidity data at 700 hPa')
  else:
    log.debug('Plotting relative humidity')
    cf = ax.contourf(xx, yy, data['rh']['700.0MB'], 
                      cmap   = color_maps.surface['cmap'], 
                      norm   = color_maps.surface['norm'],
                      levels = color_maps.surface['lvls'],
                      **opts['contourf_Opts'])
    cbar = add_colorbar( ax, cf, color_maps.surface['lvls'], **kwargs );            # Add colorbar
  
  if 'geopotential' not in data:
    log.error( 'No geopotential height data') 
  elif '1000.0MB' not in data['geopotential height']:
    log.error('Missing geopotential height data for 1000 hPa')
  elif '500.0MB' not in data['geopotential height']:
    log.error('No geopotential height data for 500 hPa')
  else:                                                                         # Else, required variables in dictionary
    thick  = data['geopotential height']['500.0MB'].to('meter').m;
    thick -= data['geopotential height']['1000.0MB'].to('meter').m;                    # Compute thickness
    c      = ax.contour(xx, yy, thick, **contour_levels.thickness);             # Draw red/blue dashed lines
    ax.clabel(c, **opts['clabel_Opts']);                                        # Update labels

  if ('mslp' in data) and ('0.0MSL' in data['mslp']):
    log.debug('Plotting mean sea level pressure')
    c = ax.contour(xx, yy, data['mslp']['0.0MSL'].to('hPa').m, 
         levels = contour_levels.mslp, 
         **opts['contour_Opts']
        )
    ax.clabel(c, **opts['clabel_Opts'])
  else:
    log.error('No mean sea level pressure data')

  txt = baseLabel( data['model'], data['initTime'], data['fcstTime'] );         # Get base string for label
  txt.append('700-hPa RH, MSLP, 1000--500-hPa THICK');                          # Update label
  t = ax.text(0.5, 0, '\n'.join( txt ),
                 verticalalignment   = 'top', 
                 horizontalalignment = 'center',
                 transform           = ax.transAxes);                           # Add label to axes

  return cf, c, cbar

################################################################################
def plot_precip_mslp_temps( ax, data, **kwargs ):
  '''
  Name:
    plot_precip_mslp_temps
  Purpose:
    A python function to plot a surface plot like the one in the
    lower right of the HDWX 4-panel plot
  Inputs:
    ax       : A GeoAxes object for axes to plot data on
    data     : Dictionary with all data plot
  Keywords:
    Various
  Outputs:
    Returns the filled contour, contour, and colorbar objects
  '''
  log = logging.getLogger(__name__);
  log.info('Creating precip plot')

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
    kwargs['extent'], kwargs['scale'] = getMapExtentScale(ax, xx, yy)
  ax = plot_basemap(ax, **kwargs);                                              # Set up the basemap, get updated axis and map scale

  cf = c1 = c2 = c3 = c4 = cbar = None
  if ('precip' in data) and ('0.0SFC' in data['precip']):
    log.debug('Plotting precipitation')
    cf = ax.contourf(xx, yy, data['precip']['0.0SFC'].to('inch').m, 
                      cmap   = color_maps.precip['cmap'], 
                      norm   = color_maps.precip['norm'],
                      levels = color_maps.precip['lvls'],
                      **opts['contourf_Opts'])
    cbar = add_colorbar( ax, cf, color_maps.precip['lvls'], **kwargs );            # Add colorbar
  else:
    log.error('No precipitation data')

  # Temperature
  if 'temperature' not in data:
    log.error( 'No temperature data')
  else:
    # 850 temp
    if '850.0MB' not in data['temperature']:
      log.error('No temperature data!')
    else:
      log.debug('Plotting surface temperature')
      temp = data['temperature']['850.0MB'].to('degC')
      c1   = ax.contour(xx, yy, temp.m, 
             levels = 0, colors = (1,0,0), linewidths = 4);                       # Contour for 0 degree C line
      c2   = ax.contour(xx, yy, temp.m, 
             levels = 0, colors = (1,1,1), linewidths = 2);                       # Contour for 0 degree C line
    # Surface temp
    if '2.0FHAG' not in data['temperature']:
      log.error('No temperature data!')
    else:
      log.debug('Plotting surface temperature')
      c3 = ax.contour(xx, yy, data['temperature']['2.0FHAG'].to('degC').m, 
           levels = 0, colors = (1,0,0), linewidths = 4);                       # Contour for 0 degree C line

  # MSLP
  if ('mslp' in data) and ('0.0MSL' in data['mslp']):                                               # If mean sea level pressure data NOT in dictionary
    log.debug('Plotting mean sea level pressure')
    c4 = ax.contour(xx, yy, data['mslp']['0.0MSL'].to('hPa').m, 
         levels = contour_levels.mslp, 
         **opts['contour_Opts']
        )
    ax.clabel(c4, **opts['clabel_Opts'])
  else:
    log.error('No mean sea level pressure data')

  txt = baseLabel( data['model'], data['initTime'], data['fcstTime'] );         # Get base string for label
  txt.append('MSLP, SFC AND 850-hPa 0 DEG, 6-HR PRECIP');                       # Update label
  t = ax.text(0.5, 0, '\n'.join( txt ),
                 verticalalignment   = 'top', 
                 horizontalalignment = 'center',
                 transform           = ax.transAxes);                           # Add label to axes

  return cf, (c1, c2, c3, c4), cbar
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
    kwargs['extent'], kwargs['scale'] = getMapExtentScale(ax, xx, yy, **kwargs)
  ax = plot_basemap(ax, **kwargs);                                              # Set up the basemap, get updated axis and map scale

  cf = c = cbar = None
  if 'temperature' not in data:
    log.error('No temperature data')
  elif '2.0FHAG' not in data:
    log.error('No 2 meter temperature data')
  else:                                                                         # Else, required variables in dictionary
    log.debug('Plotting temperature data')
    cf = ax.contourf(xx, yy, data['temperature']['2.0FHAG'].to('degF').m, 
                      cmap   = color_maps.temp_2m['cmap'], 
                      norm   = color_maps.temp_2m['norm'],
                      levels = color_maps.temp_2m['lvls'],
                      **opts['contourf_Opts'])
    cbar = add_colorbar( ax, cf, color_maps.temp_2m['lvls'], **kwargs );            # Add colorbar

  if 'u wind' not in data:
    log.error( 'No u-wind component in data')
  elif 'v wind' not in data:
    log.error( 'No v-wind component in data')
  elif '10.0FHAG' not in data['u wind']:
    log.error( 'No 10 meter u-wind component in data')
  elif '10.0FHAG' not in data['v wind']:
    log.error( 'No 10 meter v-wind component in data')
  else:
    plot_barbs(
      ax, xx, yy, data['u wind']['10.0FHAG'], data['v wind']['10.0FHAG'], **kwargs
    );                                                                          # Plot wind barbs

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

  cf = c = cbar = None;
  if 'theta_e' not in data:
    log.error('No equivalent potential temperature data')
  elif '1000.0MB' not in data['theta_e']:                                       # Else, required variables in dictionary
    log.error('No equivalent potential temperature data at 1000 hPa')
  else:
    log.debug('Plotting relative humidity')
    cf = ax.contourf(xx, yy, data['theta_e']['1000.0MB'].to('K').m, 
                      cmap   = color_maps.theta_e_1000['cmap'], 
                      norm   = color_maps.theta_e_1000['norm'],
                      levels = color_maps.theta_e_1000['lvls'],
                      **opts['contourf_Opts'])
    cbar = add_colorbar( ax, cf, color_maps.theta_e_1000['lvls'], **kwargs );       # Add colorbar

  if 'u wind' not in data:
    log.error( 'No u-wind component in data')
  elif 'v wind' not in data:
    log.error( 'No v-wind component in data')
  elif '1000.0MB' not in data['u wind']:
    log.error( 'No 1000hPa u-wind component in data')
  elif '1000.0MB' not in data['v wind']:
    log.error( 'No 1000hPa v-wind component in data')
  else:
    plot_barbs( ax, xx, yy, data['u wind']['1000.0MB'], data['v wind']['1000.0MB'] ); # Plot wind barbs

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
    kwargs['extent'], kwargs['scale'] = getMapExtentScale(ax, xx, yy, **kwargs)
  ax = plot_basemap(ax, **kwargs);                                              # Set up the basemap, get updated axis and map scale

  cf = c1 = c2 = cbar = None
  if 'temperature' not in data:
    log.error('No temperature data!')
  elif '850.0MB' not in data['temperature']:
    log.error('No temperature data at 850 hPa')
  else:
    log.debug('Plotting surface temperature')
    temp = data['temperature']['850.0MB'].to('degC')
    cf   = ax.contourf(xx, yy, temp.m, 
                      cmap   = color_maps.temp_850['cmap'], 
                      norm   = color_maps.temp_850['norm'],
                      levels = color_maps.temp_850['lvls'],
                      **opts['contourf_Opts'])
    cbar = add_colorbar( ax, cf, color_maps.temp_850['lvls'], **kwargs );           # Add colorbar
    c1   = ax.contour(xx, yy, temp.m, 
           levels = 0, colors = (0,0,1), linewidths = 2);                       # Contour for 0 degree C line
  
  if 'geopotential' not in data:
    log.error('No temperature data!')
  elif '850.0MB' not in data['geopotential height']:
    log.error('No temperature data at 850 hPa')
  else:
    log.debug('Plotting geopotential height')
    c2 = ax.contour(xx, yy, data['geopotential height']['850.0MB'].to('meter').m, 
          levels = contour_levels.heights['850'],
          **opts['contour_Opts']
        );                                                                      # Contour the geopotential height
    ax.clabel(c2, **opts['clabel_Opts']);                                       # Change contour label settings

  if 'u wind' not in data:
    log.error( 'No u-wind component in data')
  elif 'v wind' not in data:
    log.error( 'No v-wind component in data')
  elif '850.0MB' not in data['u wind']:
    log.error( 'No 850hPa u-wind component in data')
  elif '850.0MB' not in data['v wind']:
    log.error( 'No 850hPa v-wind component in data')
  else:
    plot_barbs(
      ax, xx, yy, data['u wind']['850.0MB'], data['v wind']['850.0MB'], **kwargs
    );                                                                          # Plot wind barbs

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
  log.debug( kwargs )

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
    kwargs['extent'], kwargs['scale'] = getMapExtentScale(ax, xx, yy, **kwargs)
  ax = plot_basemap(ax, **kwargs);                                              # Set up the basemap, get updated axis and map scale

  cf = c = cbar = None
  if 'abs_vort' not in data:
    log.error('No absolute voriticity data!');
  elif '500.0MB' not in data['abs_vort']:
    log.error('No absolute voriticity data at 500hPa!');
  else:
    log.debug('Plotting vorticity') 
    cf = ax.contourf(xx, yy, data['abs_vort']['500.0MB'].m * 1.0e5, 
                         cmap   = color_maps.vort_500['cmap'], 
                         norm   = color_maps.vort_500['norm'],
                         levels = color_maps.vort_500['lvls'],
                         **opts['contourf_Opts'])
    cbar = add_colorbar( ax, cf, color_maps.vort_500['lvls'], **kwargs );             # Add a color bar
 
  if 'geopotential' not in data:
    log.error('No geopotential height data')
  elif '500.0MB' not in data['geopotential height']:
    log.error('No geopotential height data at 500hPa')
  else:  
    log.debug('Plotting geopotential height')
    c = ax.contour(xx, yy, data['geopotential height']['500.0MB'].to('meter').m, 
         levels = contour_levels.heights['500'],
         **opts['contour_Opts']
        );                                                                        # Contour the geopotential height
    ax.clabel(c, **opts['clabel_Opts']);                                          # Change contour label settings
 
  if 'u wind' not in data:
    log.error( 'No u-wind component in data')
  elif 'v wind' not in data:
    log.error( 'No v-wind component in data')
  elif '500.0MB' not in data['u wind']:
    log.error( 'No 500hPa u-wind component in data')
  elif '500.0MB' not in data['v wind']:
    log.error( 'No 500hPa v-wind component in data')
  else:
    plot_barbs(
      ax, xx, yy, data['u wind']['500.0MB'], data['v wind']['500.0MB'], **kwargs
    );                                                                          # Plot wind barbs
  
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
    kwargs['extent'], kwargs['scale'] = getMapExtentScale(ax, xx, yy, **kwargs)
  ax = plot_basemap(ax, **kwargs);                                              # Set up the basemap, get updated axis and map scale

  cf = c = cbar = None;
  if 'u wind' not in data:
    log.error( 'No u-wind component in data')
  elif 'v wind' not in data:
    log.error( 'No v-wind component in data')
  elif '250.0MB' not in data['u wind']:
    log.error( 'No 250hPa u-wind component in data')
  elif '250.0MB' not in data['v wind']:
    log.error( 'No 250hPa v-wind component in data')
  else:
    log.debug('Plotting isotachs')
    isotach = wind_speed( data['u wind']['250.0MB'], data['v wind']['250.0MB'] );     # Compute windspeed and convert to knots
    cf      = ax.contourf(xx, yy, isotach.to('kts').m, 
                      cmap   = color_maps.wind_250['cmap'], 
                      norm   = color_maps.wind_250['norm'],
                      levels = color_maps.wind_250['lvls'],
                      **opts['contourf_Opts'])
    cbar    = add_colorbar( ax, cf, color_maps.wind_250['lvls'], **kwargs );        # Add a color bar
 

  if 'geopotential' not in data:
    log.error('No geopotential height data')
  elif '250.0MB' not in data['geopotential height']:
    log.error('No geopotential height data at 250hPa')
  else:  
    log.debug('Plotting geopotential height')
    c = ax.contour(xx, yy, data['geopotential height']['250.0MB'].to('meter').m, 
           levels = contour_levels.heights['250'],
           **opts['contour_Opts']
       );                                                                       # Contour the geopotential height
    ax.clabel(c, **opts['clabel_Opts']);                                        # Change contour label settings

  if cf is not None:                                                            # If cf is not None, that means the u- and v-winds exist
    plot_barbs(
      ax, xx, yy, data['u wind']['250.0MB'], data['v wind']['250.0MB'], **kwargs
    );                                                                          # Plot wind barbs

  txt = baseLabel( data['model'], data['initTime'], data['fcstTime'] );         # Get base string for label
  txt.append('250-hPa HEIGHTS, WINDS, ISOTACHS (KT)');                          # Update label
  t = ax.text(0.5, 0, '\n'.join( txt ),
                 verticalalignment   = 'top', 
                 horizontalalignment = 'center',
                 transform           = ax.transAxes);                           # Add label to axes

  return cf, c, cbar
