import logging;
import numpy as np;
from datetime import datetime, timedelta
from metpy.units import units
from metpy.calc import absolute_vorticity, lat_lon_grid_deltas;
from awips.dataaccess import DataAccessLayer as DAL;

iso = '%Y-%m-%d %H:%M:%S';  # ISO format for date

################################################################################
def get_init_fcst_times( time ):
  '''
  Name:
    get_init_fcst_times
  Purpose:
    A python function to extract forecast initialization and forecast
    time from an awips time object
  Inputs:
    time : Time to convert
  Ouputs:
    datetime objects for forecast initialization time and
    forecast time
  Keywords:
    None.
  '''
  initTime = datetime.strptime( str(time), iso )
  fcstTime = initTime + timedelta( seconds = time.getFcstTime() )
  return initTime, fcstTime

################################################################################
def awips_fcst_times( request ):
  '''
  Name:
    awips_fcst_times
  Purpose:
    A function to get forecast times for latest model run
  Inputs:
    request    : A DataAccessLayer request object
  Outputs:
    Returns a list of forecast times
  Keywords:
    None
  '''
  cycles    = DAL.getAvailableTimes(request, True);                             # Get forecast cycles
  times     = DAL.getAvailableTimes(request)                                    # Get forecast times
  times     = DAL.getForecastRun(cycles[-2], times);                            # Get forecast times in latest cycle
  initTime  = datetime.strptime( str(times[0]), iso );                          # Reference time; i.e., initialization time
  fcstTimes = [initTime + timedelta( seconds=t.getFcstTime() ) for t in times]; # Get all forecast times
  return initTime, fcstTimes, times                                             # Return forecast runs for latest cycle

################################################################################
def awips_model_base( request, time, model_vars, mdl2stnd ):
  '''
  Name:
    awips_model_base
  Purpose:
    A function to get data from NAM40 model to create HDWX products
  Inputs:
    request    : A DataAccessLayer request object
    time       : Datatime for data to grab
    model_vars : Dictionary with variables/levels to get
    mdl2stnd   : Dictionary to convert from model variable names
                  to standardized names
  Outputs:
    Returns a dictionary containing all data
  Keywords:
    EDEX   : URL for EDEX host to use
  '''
  log = logging.getLogger(__name__);                                            # Set up function for logger
  initTime, fcstTime = get_init_fcst_times( time )
  data = {'model'    : request.getLocationNames()[0],
          'initTime' : initTime,
          'fcstTime' : fcstTime};                                               # Initialize empty dictionary

  log.info('Attempting to download {} data'.format( data['model'] ) )

  for var in model_vars:                                                        # Iterate over variables in the vars list
    log.debug( 'Getting: {}'.format( var ) );
    request.setParameters( *model_vars[var]['parameters'] );                    # Set parameters for the download request
    request.setLevels(     *model_vars[var]['levels'] );                        # Set levels for the download request

    response = DAL.getGridData(request, [time ])                                # Request the data

    for res in response:                                                        # Iterate over all data request responses
      varName = res.getParameter();                                             # Get name of the variable in the response
      varLvl  = res.getLevel();                                                 # Get level of the variable in the response
      tag     = '{} {}'.format( mdl2stnd[varName], varLvl );                    # Set tag for data dictionary
      try:                                                                      # Try to
        unit = units( res.getUnit() );                                          # Get units and convert to MetPy units
      except:                                                                   # On exception
        unit = '?';                                                             # Set units to ?
        data[ tag ] = res.getRawData();                                         # Just get the data
      else:                                                                     # If get units success
        data[ tag ] = res.getRawData() * unit;                                  # Get data and create MetPy quantity by multiplying by units

      log.debug( 'Got data for:\n  Var:  {}\n  Lvl:  {}\n  Unit: {}'.format(
        varName, varLvl, unit
      ) )
  data['lon'], data['lat'] = res.getLatLonCoords();                             # Get latitude and longitude values
  data['lon'] *= units('degree');                                               # Add units of degree to longitude
  data['lat'] *= units('degree');                                               # Add units of degree to latitude
  dx, dy = lat_lon_grid_deltas( data['lon'], data['lat'] );                     # Get grid spacing in x and y
  for lvl in model_vars['winds']['levels']:                                     # Iterate over all leves in the wind data
    uTag = mdl2stnd[ model_vars['winds']['parameters'][0] ];                    # Get initial tag name for u-wind
    vTag = mdl2stnd[ model_vars['winds']['parameters'][1] ];                    # Get initial tag name for v-wind
    
    uTag, vTag = '{} {}'.format(uTag, lvl), '{} {}'.format(vTag, lvl);          # Append level information to the initial tag names
    if (uTag in data) and (vTag in data):                                       # If both tags are in the data structure
      log.debug( 'Computing absolute vorticity at {}'.format( lvl ) );
      tag = 'abs_vor {}'.format(lvl);                                           # Set tag for vorticity
      data[tag] = absolute_vorticity( data[uTag],data[vTag],dx,dy,data['lat'] );# Compute absolute vorticity
  return data;                                                                  # Return data dictionary