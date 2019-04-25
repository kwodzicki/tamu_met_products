import logging;
import numpy as np;
from datetime import datetime, timedelta
from metpy.units import units
from metpy.calc import (
  absolute_vorticity, 
  mixed_parcel,
  parcel_profile,
  cape_cin,
  equivalent_potential_temperature, 
  lat_lon_grid_deltas
);
from awips.dataaccess import DataAccessLayer as DAL;

iso = '%Y-%m-%d %H:%M:%S';  # ISO format for date

def calcMLCAPE( levels, temperature, dewpoint, depth = 100.0 * units.hPa ):
  _, T_parc, Td_par = mixed_parcel(levels, temperature, dewpoint, 
            depth       = depth,
            interpolate = False,
  )
  profile        = parcel_profile(levels, T_parc, Td_parc)
  cape, cin = cape_cin( levels, temperature, dewpoint, profile )
  return cape;

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
def awips_fcst_times( request, interval = 3600, max_forecast = None ):
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
    interval     : Time step between forecast times in seconds
                      Default is 3600s (1 hour)
    max_forecast : Maximum forecast time to get, in seconds.
                      Default is last available time
  '''
  cycles    = DAL.getAvailableTimes(request, True);                             # Get forecast cycles
  times     = DAL.getAvailableTimes(request)                                    # Get forecast times
  times     = DAL.getForecastRun(cycles[-1], times);                            # Get forecast times in latest cycle

  if max_forecast is None:
    max_forecast = times[-1].getFcstTime();                                     # Set max_forecast value default based on model
  nTimes    =  max_forecast // interval + 1;                                    # Number of forecast steps to get based on inteval
  flt_times = [ [] for i in range( nTimes ) ]                                   # Initialized list of empty lists for forecast times
  
  for time in times:                                                            # Iterate over all times
    fcstTime = time.getFcstTime();                                              # Get the valid forecast time
    if ((fcstTime % interval) == 0) and (fcstTime < max_forecast):              # If the forecast hour falls on the interval requested AND is before the max forecast time
      fcstDur = time.getValidPeriod().duration();                               # Get duration of the forecast period
      if (fcstDur == 0) or (fcstDur == interval):                               # If instantaneous forecast period OR period covers requested interval
        index = fcstTime // interval;                                           # Index for the times flt_times array
        flt_times[index].append( time );                                        # Append the time to the list at index
  return flt_times;                                                             # Return forecast runs for latest cycle

################################################################################
def awips_model_base( request, time, model_vars, mdl2stnd, previous_data = None ):
  '''
  Name:
    awips_model_base
  Purpose:
    A function to get data from NAM40 model to create HDWX products
  Inputs:
    request    : A DataAccessLayer request object
    time       : List of datatime(s) for data to grab
    model_vars : Dictionary with variables/levels to get
    mdl2stnd   : Dictionary to convert from model variable names
                  to standardized names
  Outputs:
    Returns a dictionary containing all data
  Keywords:
    previous_data : Dictionary with data from previous time step
  '''
  log = logging.getLogger(__name__);                                            # Set up function for logger
  initTime, fcstTime = get_init_fcst_times( time[0] )
  data = {'model'    : request.getLocationNames()[0],
          'initTime' : initTime,
          'fcstTime' : fcstTime};                                               # Initialize empty dictionary

  log.info('Attempting to download {} data'.format( data['model'] ) )

  for var in model_vars:                                                        # Iterate over variables in the vars list
    log.debug( 'Getting: {}'.format( var ) );
    request.setParameters( *model_vars[var]['parameters'] );                    # Set parameters for the download request
    request.setLevels(     *model_vars[var]['levels'] );                        # Set levels for the download request
    
    response = DAL.getGridData(request, time)                                   # Request the data

    for res in response:                                                        # Iterate over all data request responses
      varName = res.getParameter();                                             # Get name of the variable in the response
      varLvl  = res.getLevel();                                                 # Get level of the variable in the response
      varName = mdl2stnd [ varName ];                                           # Convert variable name to local standarized name
      if varName not in data: data[varName] = {};                               # If variable name NOT in data dictionary, initialize new dictionary under key
      data[ varName ][ varLvl ] = res.getRawData();                             # Add data under level name
      try:                                                                      # Try to
        unit = units( res.getUnit() );                                          # Get units and convert to MetPy units
      except:                                                                   # On exception
        unit = '?';                                                             # Set units to ?
      else:                                                                     # If get units success
        data[ varName ][ varLvl ] *= unit;                                      # Get data and create MetPy quantity by multiplying by units

      log.debug( 'Got data for:\n  Var:  {}\n  Lvl:  {}\n  Unit: {}'.format(
        varName, varLvl, unit
      ) )
  data['lon'], data['lat'] = res.getLatLonCoords();                             # Get latitude and longitude values
  data['lon'] *= units('degree');                                               # Add units of degree to longitude
  data['lat'] *= units('degree');                                               # Add units of degree to latitude

  # Absolute vorticity
  dx, dy = lat_lon_grid_deltas( data['lon'], data['lat'] );                     # Get grid spacing in x and y
  uTag = mdl2stnd[ model_vars['wind']['parameters'][0] ];                       # Get initial tag name for u-wind
  vTag = mdl2stnd[ model_vars['wind']['parameters'][1] ];                       # Get initial tag name for v-wind
  if (uTag in data) and (vTag in data):                                         # If both tags are in the data structure
    data['abs_vort'] = {};                                                      # Add absolute vorticity key
    for lvl in model_vars['wind']['levels']:                                    # Iterate over all leves in the wind data
      if (lvl in data[uTag]) and (lvl in data[vTag]):                           # If given level in both u- and v-wind dictionaries
        log.debug( 'Computing absolute vorticity at {}'.format( lvl ) );
        data['abs_vort'][ lvl ] = \
          absolute_vorticity( data[uTag][lvl], data[vTag][lvl], 
                              dx, dy, data['lat'] );                            # Compute absolute vorticity

  # 1000 MB equivalent potential temperature  
  if ('temperature' in data) and ('dewpoint' in data):                          # If temperature AND depoint data were downloaded
    data['theta_e'] = {}
    T, Td = 'temperature', 'dewpoint'
    if ('1000.0MB' in data[T]) and ('1000.0MB' in data[Td]):                    # If temperature AND depoint data were downloaded
      log.debug( 'Computing equivalent potential temperature at 1000 hPa' )
      data['theta_e']['1000.0MB'] = equivalent_potential_temperature(
      1000.0 * units('hPa'), data[T]['1000.0MB'], data[Td]['1000.0MB']
    )

    return data
    # MLCAPE
    log.debug( 'Computing mixed layer CAPE' )
    T_lvl   = list( data[T].keys()  );
    Td_lvl  = list( data[Td].keys() );
    levels  = list( set( T_lvl ).intersection( Td_lvl ) );
    levels  = [float(lvl.replace('MB','')) for lvl in levels]
    levels  = sorted( levels, reverse=True )

    nLvl    = len(levels)
    if nLvl > 0:
      log.debug( 'Found {} matching levels in temperature and dewpoint data'.format(nLvl) )
      nLat, nLon = data['lon'].shape;
      
      data['MLCAPE'] = np.zeros( (nLat, nLon,),       dtype=np.float32 ) * units('J/kg')
      TT             = np.zeros( (nLvl, nLat, nLon,), dtype=np.float32 ) * units('degC')
      TTd            = np.zeros( (nLvl, nLat, nLon,), dtype=np.float32 ) * units('degC')
  
      log.debug( 'Sorting temperature and dewpoint data by level' )
      for i in range( nLvl ):
        key = '{:.1f}MB'.format( levels[i] )
        TT[i,:,:]  = data[T][key].to('degC')
        TTd[i,:,:] = data[Td][key].to('degC')
      
      levels   = np.array( levels ) * units.hPa
      depth    = 100.0 * units.hPa

      log.debug( 'Iterating over grid boxes to compute MLCAPE' )
      for j in range( nLat ):
        for i in range( nLon ):
          try:
            _, T_parc, Td_parc = mixed_parcel( levels, TT[:,j,i], TTd[:,j,i], 
              depth       = depth,
              interpolate = False,
            )
            profile   = parcel_profile(levels, T_parc, Td_parc)
            cape, cin = cape_cin( levels, TT[:,j,i], TTd[:,j,i], profile )
          except:
            log.warning( 
              'Failed to compute MLCAPE for lon/lat: {}; {}'.format(
                data['lon'][j,i], data['lat'][j,i]
              )
            )
          else:
            data['MLCAPE'][j,i] = cape
  return data;                                                                  # Return data dictionary