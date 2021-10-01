import logging
import os, json
from metpy.calc import wind_speed
from metpy.units import units

from .plot_utils import add_colorbar, plot_barbs

from . import color_maps
from . import contour_levels

dir = os.path.dirname( os.path.dirname(__file__) );
with open( os.path.join(dir, 'plot_opts.json'), 'r' ) as fid:
  OPTS = json.load(fid);

def convertHeight( height ):
  unit = 'FHAG' if height.units == units('meter') else 'MB'
  return f'{height.magnitude:0.1f}{unit}'

def contourf( ax, x, y, z, **kwargs ):
  """
  General filled contour function with some fixed options

  Arguments:
    ax (GeoAxes) : Axis to draw the geopotential heights on
    x (ndarray) : x-axis data for plotting
    y (ndarray) : y-axis data for plotting
    z (ndarray) : data to draw filled contours for

  Keyword arguments:
    **kwargs : Arguments accepted by matplotlib contourf()

  Returns:
    tuple : Object for filled contours and colorbar

  """

  cf   = ax.contourf( x, y, z, **kwargs, **OPTS['contourf_Opts'] )              # Draw filled contours
  cbar = add_colorbar( ax, cf, None, **kwargs )                                 # Add a color bar

  return cf, cbar                                                               # Return the filled contour reference and colorbar reference

def plot_wind_barbs( ax, data, height, **kwargs ):
  """
  Draw wind barbs at a given height

  Arguments:
    ax (GeoAxes) : Axis to draw the geopotential heights on
    data (AWIPSData) : Dictionary containing data to plot
    height (Quantity) : Altitude/height to plot

  Keyword arguments:
    varname (str) : Name of variable to plot
    **kwargs : passed to contour function

  Returns:
    tuple :

  """

  log     = logging.getLogger( __name__ )

  uvName  = kwargs.get( 'varName', ('u wind', 'v wind',) ) 
  height  = convertHeight( height )

  try:
    u_wind = data.getVar( uvName[0], height )
    v_wind = data.getVar( uvName[1], height )
  except Exception as err:
    log.error( err )
  else:
    plot_barbs( ax, data['xx'], data['yy'], u_wind, v_wind, **kwargs )                          # Plot wind barbs


def contourf_isotachs(ax, data, height, **kwargs):
  """
  Draw filled contours for isotachs at a given height

  Arguments:
    ax (GeoAxes) : Axis to draw the geopotential heights on
    data (AWIPSData) : Dictionary containing data to plot
    height (Quantity) : Altitude/height to plot

  Keyword arguments:
    varname (str) : Name of variable to plot
    unit (str) : Unit to convert to for plotting
    **kwargs : passed to contour function

  Returns:
    tuple :

  """

  log     = logging.getLogger( __name__ )
  uvName  = kwargs.pop( 'varname', ('u wind', 'v wind',) ) 
  unit    = kwargs.pop( 'unit', 'kts' )
  height  = convertHeight( height)
  
  try:
    u_wind = data.getVar( uvName[0], height)
    v_wind = data.getVar( uvName[1], height)
  except Exception as err:
    log.error( err )
    return None, None, None
  
  kwargs.update( color_maps.winds.get(height, {}) )

  log.debug('Plotting isotachs')
  var      = wind_speed( u_wind, v_wind ).to(unit).magnitude                    # Compute windspeed and convert to knots
  cf, cbar = contourf(ax, data['xx'], data['yy'], var, **kwargs) 

  return var, cf, cbar

def contourf_vorticity( ax, data, height, **kwargs ):
  """
  Draw filled contours for vorticity at a given height

  Arguments:
    ax (GeoAxes) : Axis to draw the geopotential heights on
    data (AWIPSData) : Dictionary containing data to plot
    height (Quantity) : Altitude/height to plot

  Keyword arguments:
    varname (str) : Name of variable to plot
    unit (str) : Unit to convert to for plotting
    **kwargs : passed to contour function

  Returns:
    tuple :

  """

  log     = logging.getLogger( __name__ )

  varName = kwargs.pop( 'varname', 'abs_vort' ) 
  unit    = kwargs.pop( 'unit', None )
  height  = convertHeight( height)

  try:
    var = data.getVar( varName, height).magnitude * 1.0e5
  except Exception as err:
    log.error( err )
    return None, None, None
  
  kwargs.update( color_maps.vorticity.get(height, {}) )

  log.debug( f'Plotting {varName} at {height}' ) 
  cf, cbar = contourf( ax, data['xx'], data['yy'], var, **kwargs ) 

  return var, cf, cbar

def contourf_temperature( ax, data, height, **kwargs ):
  """
  Draw filled contours for temperature at a given height

  Arguments:
    ax (GeoAxes) : Axis to draw the geopotential heights on
    data (AWIPSData) : Dictionary containing data to plot
    height (Quantity) : Altitude/height to plot

  Keyword arguments:
    varname (str) : Name of variable to plot
    unit (str) : Unit to convert to for plotting
    **kwargs : passed to contour function

  Returns:
    tuple :

  """

  log     = logging.getLogger( __name__ )

  varName = kwargs.pop( 'varname', 'temperature' ) 
  unit    = kwargs.pop('unit', 'degC')
  height  = convertHeight( height)

  try:
    var = data.getVar( varName, height)
    var = var.to( unit ).magnitude
  except Exception as err:
    log.error( err )
    return None, None, None

  kwargs.update( color_maps.temperature.get(height, {}) )

  log.debug( f'Plotting {varName} at {height}' ) 
  cf, cbar = contourf(ax, data['xx'], data['yy'], var, **kwargs ) 

  return var, cf, cbar

def contourf_RH(ax, data, height, **kwargs):
  """
  Draw filled contours for relative humidity at a given height

  Arguments:
    ax (GeoAxes) : Axis to draw the geopotential heights on
    data (AWIPSData) : Dictionary containing data to plot
    height (Quantity) : Altitude/height to plot

  Keyword arguments:
    varname (str) : Name of variable to plot
    unit (str) : Unit to convert to for plotting
    **kwargs : passed to contour function

  Returns:
    tuple :

  """

  log     = logging.getLogger( __name__ )

  varName = kwargs.pop( 'varname', 'rh' ) 
  unit    = kwargs.pop('unit', 'percent')
  height  = convertHeight( height)

  try:
    var = data.getVar( varName, height )
    var = var.to( unit ).magnitude
  except Exception as err:
    log.error( err )
    return None, None, None

  kwargs.update( color_maps.surface )

  log.debug( f'Plotting {varName} at {height}' ) 
  cf, cbar = contourf(ax, data['xx'], data['yy'], var, **kwargs )

  return var, cf, cbar

def contourf_theta_e(ax, data, height, **kwargs):
  """
  Draw filled contours for equivalent potential temperature at a given height

  Arguments:
    ax (GeoAxes) : Axis to draw the geopotential heights on
    data (AWIPSData) : Dictionary containing data to plot
    height (Quantity) : Altitude/height to plot

  Keyword arguments:
    varname (str) : Name of variable to plot
    unit (str) : Unit to convert to for plotting
    **kwargs : passed to contour function

  Returns:
    tuple :

  """

  log     = logging.getLogger( __name__ )

  varName = kwargs.pop( 'varname', 'theta_e' )
  unit    = kwargs.pop( 'unit', 'K') 
  height  = convertHeight( height)

  try:
    var = data.getVar( varName, height )
    var = var.to(unit).magnitude
  except Exception as err:
    log.error( err )
    return None, None, None

  kwargs.update( color_maps.theta_e.get( height, None) )

  log.debug( f'Plotting {varName} at {height}' ) 
  cf, cbar = contourf(ax, data['xx'], data['yy'], var, **kwargs)

  return var, cf, cbar

def contour_height(ax, data, height, fill=False, **kwargs):
  """
  Draw contour lines for geopotential height at a given height

  Arguments:
    ax (GeoAxes) : Axis to draw the geopotential heights on
    data (AWIPSData) : Dictionary containing data to plot
    height (Quantity) : Altitude/height to plot

  Keyword arguments:
    varname (str) : Name of variable to plot
    unit (str) : Unit to convert to for plotting
    **kwargs : passed to contour function

  Returns:
    tuple :

  """

  log = logging.getLogger(__name__)

  varName = kwargs.pop('varname', 'geopotential height' )                       # Get name of variable to plot
  unit    = kwargs.pop( 'unit', 'meter' )
  height  = convertHeight( height)                                              # Ensure height is in proper format for indexing various color map, contour level, etc dictionaries

  try:                                                                          # Try to get the data at given level from the data dictionary
    var = data.getVar( varName, height )
    var = var.to( unit ).magnitude
  except Exception as err:                                                      # If there is an exception getting the data, log the error and return None; fail 'quietly'
    log.error( err )
    return None, None

  log.debug( f'Plotting {varName}' )
  c = ax.contour(data['xx'], data['yy'], var, 
         levels = contour_levels.heights.get(height, None),
         **OPTS['contour_Opts']
     )                                                                        # Contour the geopotential height
  ax.clabel(c, **OPTS['clabel_Opts'])                                         # Change contour label settings

  return var, c

def contour_thickness(ax, data, height1, height2, fill=False, **kwargs):
  """
  Draw contour lines for geopotential height at a given height

  Arguments:
    ax (GeoAxes) : Axis to draw the geopotential heights on
    data (AWIPSData) : Dictionary containing data to plot
    height (Quantity) : Altitude/height to plot

  Keyword arguments:
    varname (str) : Name of variable to plot
    unit (str) : Unit to convert to for plotting
    **kwargs : passed to contour function

  Returns:
    tuple :

  """

  log = logging.getLogger(__name__)

  varName = kwargs.pop('varname', 'geopotential height' ) 
  unit    = kwargs.pop('unit', 'meter')
  height1 = convertHeight( height1 )
  height2 = convertHeight( height2 )

  try:
    var1 = data.getVar( varName, height1)
    var2 = data.getVar( varName, height2)
    var  = var2.to(unit).m - var1.to(unit).m                                    # Compute thickness
  except Exception as err:
    log.error( err )
    return None, None
  
  log.debug( f'Plotting {varName}' )

  c = ax.contour(data['xx'], data['yy'], var, **contour_levels.thickness)       # Draw red/blue dashed lines
  ax.clabel(c, **OPTS['clabel_Opts'])                                        # Update labels

  return var, c
