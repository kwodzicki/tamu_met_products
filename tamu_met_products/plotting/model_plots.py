import logging
import os
from metpy.units import units

from .plotters import *
from .plot_utils import add_colorbar, plot_basemap, baseLabel, parseArgs 

from . import color_maps
from . import contour_levels

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

  height = units.Quantity( 700, 'hPa' )
  thick1 = units.Quantity(1000, 'hPa' )
  thick2 = units.Quantity( 500, 'hPa' )
  try:
    parseArgs( ax, data, kwargs )
  except Exception as err:
    log.error( err )
    return None, None, None

  ax = plot_basemap(ax, **kwargs);                                              # Set up the basemap, get updated axis and map scale

  var, cf, cbar = contourf_RH( ax, data, height, **kwargs)                         # Contour fill relative humidity
  var, c        = contour_thickness(ax, data, thick1, thick2, **kwargs)               # Contour thickness between 2 levels

  try:
    var = data.getVar( 'mslp', '0.0MSL' )
  except Exception as err:
    log.error( err )
  else:
    log.debug('Plotting mean sea level pressure')
    c = ax.contour(data['xx'], data['yy'], var.to('hPa').m, 
         levels = contour_levels.mslp, 
         **OPTS['contour_Opts']
        )
    ax.clabel(c, **OPTS['clabel_Opts'])

  txt = baseLabel( data['model'], data['initTime'], data['fcstTime'] )         # Get base string for label
  txt.append(f'{height.magnitude:d}-hPa RH, MSLP, {thick1.magnitude:d}--{thick2.magnitude:d}-hPa THICK')                          # Update label
  t = ax.text(0.5, 0, os.linesep.join( txt ),
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

  try:
    parseArgs( ax, data, kwargs )
  except Exception as err:
    log.error( err )
    return None, None, None

  ax = plot_basemap(ax, **kwargs);                                              # Set up the basemap, get updated axis and map scale

  cf = c1 = c2 = c3 = c4 = cbar = None
  try:
    var = data.getVar( 'precip', '0.0SFC' ).to('inch').magnitude
  except Exception as err:
    log.error( err )
  else:
    log.debug('Plotting precipitation')
    var, cf, cbar = contourf(ax, data['xx'], data['yy'], var, **color_maps.precip, **kwargs) 

    #cf = ax.contourf(data['xx'], data['yy'], var, 
    #                **color_maps.precip, 
    #                **OPTS['contourf_Opts'])
    #cbar = add_colorbar( ax, cf, color_maps.precip['levels'], **kwargs );            # Add colorbar

  # Temperature
  varName = 'temperature'
  height  = units.Quantity( 850, 'hPa')
  try:
    var = data.getVar( varName, height ).to('degC').magnitude
    # 850 temp
  except Exception as err:
    log.error( err )
  else:
    log.debug( f'Plotting {varName} at {height}')
    c1   = ax.contour(data['xx'], data['yy'], var, 
           levels = 0, colors = (1,0,0), linewidths = 4);                       # Contour for 0 degree C line
    c2   = ax.contour(data['xx'], data['yy'], var, 
           levels = 0, colors = (1,1,1), linewidths = 2);                       # Contour for 0 degree C line

  height = units.Quantity(2, 'meter')
  try:
    var = data.getVar( varName, height ).to('degC').magnitude
  except Exception as err:
    log.error( err )
  else:
    log.debug( f'Plotting {varName} at {height}')
    c3 = ax.contour(data['xx'], data['yy'], var, 
         levels = 0, colors = (1,0,0), linewidths = 4);                       # Contour for 0 degree C line

  # MSLP
  try:
    var = data.getVar( 'mslp', '0.0MSL' ).to('hPa').magnitude
  except Exception as err:
    log.error( err )
  else:
    log.debug('Plotting mean sea level pressure')
    c4 = ax.contour(data['xx'], data['yy'], var, 
         levels = contour_levels.mslp, 
         **OPTS['contour_Opts']
        )
    ax.clabel(c4, **OPTS['clabel_Opts'])

  txt = baseLabel( data['model'], data['initTime'], data['fcstTime'] );         # Get base string for label
  txt.append('MSLP, SFC AND 850-hPa 0 DEG, 6-HR PRECIP');                       # Update label
  t = ax.text(0.5, 0, os.linesep.join( txt ),
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
  log = logging.getLogger(__name__)
  log.info('Creating surface hPa plot')

  height_2m  = units.Quantity( 2, 'meter')
  height_10m = units.Quantity(10, 'meter')

  try:
    parseArgs( ax, data, kwargs )
  except Exception as err:
    log.error( err )
    return None, None, None

  ax = plot_basemap(ax, **kwargs)                                               # Set up the basemap, get updated axis and map scale

  var, cf, cbar = contourf_temperature( ax, data, height_2m,  unit='degF', **kwargs)
  _             = plot_wind_barbs(      ax, data, height_10m, **kwargs)

  txt = baseLabel( data['model'], data['initTime'], data['fcstTime'] )         # Get base string for label
  txt.append( f'{height_2m.magnitude:d}-M TEMP (F) AND {height_10m.magnitude:d}-M WINDS') # Update label
  t = ax.text(0.5, 0, os.linesep.join( txt ),
                 verticalalignment   = 'top', 
                 horizontalalignment = 'center',
                 transform           = ax.transAxes)                            # Add label to axes

  return cf, None, cbar

################################################################################
def plot_1000hPa_theta_e_barbs( ax, data, **kwargs ):
  """
  Plot a 1000 hPa equivalent potential temperature and  winds

  Arguments::
    ax       : A GeoAxes object for axes to plot data on
    data     : Dictionary with all data plot

  Keyword arguments:
    **kwargs

  Returns:
    tuple : Filled contour, contour, and colorbar objects

  """

  log = logging.getLogger(__name__);
  log.info('Creating Theta-e plot')

  try:
    parseArgs( ax, data, kwargs )
  except Exception as err:
    log.error( err )
    return None, None, None

  ax = plot_basemap(ax, **kwargs);                                              # Set up the basemap, get updated axis and map scale

  height = units.Quantity(1000, 'hPa')
  var, cf, cbar = contourf_theta_e(ax, data, height, **kwargs)
  _             = plot_wind_barbs( ax, data, height, **kwargs)

  txt = baseLabel( data['model'], data['initTime'], data['fcstTime'] );         # Get base string for label
  txt.append( f'{height.magnitude:d}-hPa EQUIVALENT POTENTIAL TEMPERATURE AND WINDS');            # Update label
  t = ax.text(0.5, 0, os.linesep.join( txt ),
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
  height = units.Quantity(850, 'hPa')

  try:
    parseArgs( ax, data, kwargs )
  except Exception as err:
    log.error( err )
    return None, None, None

  ax = plot_basemap(ax, **kwargs);                                              # Set up the basemap, get updated axis and map scale

  var, cf, cbar = contourf_temperature( ax, data, height, **kwargs )
  c1            = ax.contour(data['xx'], data['yy'], var,
                    levels = 0, colors = (0,0,1), linewidths = 2)               # Contour for 0 degree C line
  var, c2       = contour_height(       ax, data, height, **kwargs )  
  _             = plot_wind_barbs(      ax, data, height, **kwargs ) 

  txt = baseLabel( data['model'], data['initTime'], data['fcstTime'] );         # Get base string for label
  txt.append( f'{height.magnitude:d}-hPa HEIGHTS, WINDS, TEMP (C)');                               # Update label
  t = ax.text(0.5, 0, os.linesep.join( txt ),
                 verticalalignment   = 'top', 
                 horizontalalignment = 'center',
                 transform           = ax.transAxes)                            # Add label to axes

  return cf, (c1, c2), cbar

################################################################################
def plot_500hPa_vort_hght_barbs( ax, data, **kwargs ):
  """
  Plot a 500 hPa plot like the one in the  upper left of the HDWX 4-panel plot

  Arguments:
    ax (GeoAxes) : Axis to plot data on
    data (AWIPSData) :  Dictionary with all data plot

  Keyword arguments:
    All keywords accecpted by plotting methods. 

  Returns:
    tuple : Filled contour, contour, and colorbar objects

  """

  log = logging.getLogger(__name__)
  log.info('Creating 500 hPa plot')

  height = units.Quantity(500, 'hPa')                                            # Set data level

  try:
    parseArgs( ax, data, kwargs )
  except Exception as err:
    log.error( err )
    return None, None, None

  ax = plot_basemap(ax, **kwargs);                                              # Set up the basemap, get updated axis and map scale

  var, cf, cbar = contourf_vorticity( ax, data, height, **kwargs)                  # Plot vorticity at given level
  var, c,       = contour_height(     ax, data, height, **kwargs)                  # Plot heights at given level
  _             = plot_wind_barbs(    ax, data, height, **kwargs)                  # Plot wind barbs at given level

  txt = baseLabel( data['model'], data['initTime'], data['fcstTime'] )          # Get base string for label
  txt.append( f'{height.magnitude:d}-hPa HEIGHTS, WINDS, ABS VORT');             # Add label for products plotted
  t = ax.text(0.5, 0, os.linesep.join( txt ),
                 verticalalignment   = 'top', 
                 horizontalalignment = 'center',
                 transform           = ax.transAxes);                           # Add label to axes

  return cf, c, cbar

################################################################################
def plot_250hPa_isotach_hght_barbs( ax, data, **kwargs ):
  """
  Plot a 250 hPa plot like the one in the upper right of the HDWX 4-panel plot

  Arguments:
    ax (GeoAxes) : Axis to plot data on
    data (AWIPSData) :  Dictionary with all data plot

  Keyword arguments:
    All keywords accecpted by plotting methods. 

  Returns:
    tuple : Filled contour, contour, and colorbar objects

  """

  log = logging.getLogger(__name__)
  log.info('Creating 250 hPa plot')

  height = units.Quantity( 250, 'hPa' )

  try:
    parseArgs( ax, data, kwargs )
  except Exception as err:
    log.error( err )
    return None, None, None

  ax = plot_basemap(ax, **kwargs);                                              # Set up the basemap, get updated axis and map scale

  var, cf, cbar = contourf_isotachs(ax, data, height, **kwargs)                    # Contour fill isotachs 
  var, c        = contour_height(   ax, data, height, **kwargs)                    # Contour heights
  _             = plot_wind_barbs(  ax, data, height, **kwargs)                    # Plot wind barbs

  txt = baseLabel( data['model'], data['initTime'], data['fcstTime'] )          # Get base string for label
  txt.append( f'{height.magnitude:d}-hPa HEIGHTS, WINDS, ISOTACHS (KT)')         # Add products plotted to label
  t = ax.text(0.5, 0, os.linesep.join( txt ),
                 verticalalignment   = 'top', 
                 horizontalalignment = 'center',
                 transform           = ax.transAxes);                           # Add label to axes

  return cf, c, cbar
