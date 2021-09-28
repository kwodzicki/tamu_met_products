import logging
from os import linesep
from datetime import datetime, timedelta

import numpy as np
from metpy.units import units
from metpy.calc import (
  absolute_vorticity, 
  mixed_parcel,
  parcel_profile,
  cape_cin,
  equivalent_potential_temperature, 
  lat_lon_grid_deltas
)

from awips.dataaccess import DataAccessLayer as DAL

iso = '%Y-%m-%d %H:%M:%S'  # ISO format for date

def calcMLCAPE( levels, temperature, dewpoint, depth = 100.0 * units.hPa ):
  _, T_parc, Td_par = mixed_parcel(levels, temperature, dewpoint, 
            depth       = depth,
            interpolate = False,
  )
  profile        = parcel_profile(levels, T_parc, Td_parc)
  cape, cin = cape_cin( levels, temperature, dewpoint, profile )
  return cape

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

class AWIPSData( dict ):
  """
  Subclass fo dict that adds the getVar() method

  The getVar method is add to allow for easy getting of a given variable,
  possibly at a given level. Simply pass in the variable name, and the
  level you would like the variable on, and the data will be returned IF
  exists. If the data does NOT exist, then an exception is raised.
  Place class to this method in a try/except block.

  """

  def getVar( self, name, level=None ):
    """
    Get a variable, at given level

    If the requested variable/level does NOT exist in the dictionary, then
    an exception will be raised.

    The idea behind adding the method is to cut down on if statements that must
    check if the variable exists, then if the given level exists with in the
    variable. All the checking is done within the method.

    Arguments:
      name (str) : Name of the variable to get data for

    Keyword arguments:
      level (str) : Level on which to get the variable for. When not specified
        (i.e., level=None), then all data/levels for the given variable
        are returned.

    Returns:
      Data for given variable/level IF it exists

    """

    if name not in self:                                                        # If the variable does NOT exist
      raise Exception( f'Failed to find variable {name}' )

    if level is not None:                                                       # If level is NOT None
      if level not in self[name]:                                               # If the level does NOT exist in the variable
        raise Exception( f'Failed to find level {level} in variable {name}' )

      return self[name][level]                                                  # Return variable on given level
 
    return self[name]                                                           # Return variable

class AWIPSModelDownloader( object ):
  """
  Model data downloader
  """

  def __init__(self, modelName, EDEX = "edex-cloud.unidata.ucar.edu", **kwargs):

    DAL.changeEDEXHost( EDEX )                                                  # Set the EDEX host
    self._request = DAL.newDataRequest()                                        # Initialize a new data request
    self._request.setDatatype( "grid" )                                         # Set data request type to grid data
    self._request.setLocationNames( modelName )                                 # Set data set to modelName

    self.log = logging.getLogger(__name__)                                      # Initialize a logger

  def fcst_times( self, interval = 3600, max_forecast = None ):
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

    cycles    = DAL.getAvailableTimes(self._request, True)                     # Get forecast cycles
    times     = DAL.getAvailableTimes(self._request)                            # Get forecast times

    #self.log.debug( f'Found following model cycles : {cycles}' )
    #self.log.debug( f'Found following model times  : {times}'  )

    try:
      times = DAL.getForecastRun(cycles[-1], times)                          # Get forecast times in latest cycle
    except Exception as err:
      self.log.error( f'Failed to get model run cycle/time : {err}' )
      return [] 
 
    if max_forecast is None:
      max_forecast = times[-1].getFcstTime()                                   # Set max_forecast value default based on model
    nTimes    =  max_forecast // interval + 1                                  # Number of forecast steps to get based on inteval
    flt_times = [ [] for i in range( nTimes ) ]                                 # Initialized list of empty lists for forecast times
    
    for time in times:                                                          # Iterate over all times
      fcstTime = time.getFcstTime()                                            # Get the valid forecast time
      if ((fcstTime % interval) == 0) and (fcstTime < max_forecast):            # If the forecast hour falls on the interval requested AND is before the max forecast time
        fcstDur = time.getValidPeriod().duration()                             # Get duration of the forecast period
        if (fcstDur == 0) or (fcstDur == interval):                             # If instantaneous forecast period OR period covers requested interval
          index = fcstTime // interval                                         # Index for the times flt_times array
          flt_times[index].append( time )                                      # Append the time to the list at index
 
    return flt_times                                                           # Return forecast runs for latest cycle

  def getData( self, time, model_vars, mdl2stnd, previous_data = None ):
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
    initTime, fcstTime = get_init_fcst_times( time[0] )
    data = AWIPSData( model    = self._request.getLocationNames()[0],
                      initTime = initTime,
                      fcstTime = fcstTime)                                            # Initialize empty dictionary

    self.log.info('Attempting to download {} data'.format( data['model'] ) )

    for var in model_vars:                                                      # Iterate over variables in the vars list
      self.log.debug( 'Getting: {}'.format( var ) )
      self._request.setParameters( *model_vars[var]['parameters'] )            # Set parameters for the download request
      self._request.setLevels(     *model_vars[var]['levels'] )                # Set levels for the download request

      response = DAL.getGridData(self._request, time)                           # Request the data

      for res in response:                                                      # Iterate over all data request responses
        varName = res.getParameter()                                           # Get name of the variable in the response
        varLvl  = res.getLevel()                                               # Get level of the variable in the response
        varName = mdl2stnd [ varName ]                                         # Convert variable name to local standarized name
        if varName not in data: data[varName] = {}                             # If variable name NOT in data dictionary, initialize new dictionary under key

        data[ varName ][ varLvl ] = res.getRawData()                           # Add data under level name
        try:                                                                    # Try to
          unit = units( res.getUnit() )                                        # Get units and convert to MetPy units
        except:                                                                 # On exception
          unit = '?'                                                           # Set units to ?
        else:                                                                   # If get units success
          data[ varName ][ varLvl ] *= unit                                    # Get data and create MetPy quantity by multiplying by units

        msgFMT = 'Got data for:{0}  Var:  {1}{0}  Lvl:  {2}{0}  Unit: {3}'
        self.log.debug( msgFMT.format( linesep, varName, varLvl, unit ) )

    data['lon'], data['lat'] = res.getLatLonCoords()                             # Get latitude and longitude values
    data['lon'] *= units('degree')                                               # Add units of degree to longitude
    data['lat'] *= units('degree')                                               # Add units of degree to latitude
  
    # Absolute vorticity
    dx, dy = lat_lon_grid_deltas( data['lon'], data['lat'] )                     # Get grid spacing in x and y
    uTag = mdl2stnd[ model_vars['wind']['parameters'][0] ]                       # Get initial tag name for u-wind
    vTag = mdl2stnd[ model_vars['wind']['parameters'][1] ]                       # Get initial tag name for v-wind
    if (uTag in data) and (vTag in data):                                         # If both tags are in the data structure
      data['abs_vort'] = {}                                                      # Add absolute vorticity key
      for lvl in model_vars['wind']['levels']:                                    # Iterate over all leves in the wind data
        if (lvl in data[uTag]) and (lvl in data[vTag]):                           # If given level in both u- and v-wind dictionaries
          self.log.debug( 'Computing absolute vorticity at {}'.format( lvl ) )
          data['abs_vort'][ lvl ] = \
            absolute_vorticity( data[uTag][lvl], data[vTag][lvl], 
                                dx, dy, data['lat'] )                            # Compute absolute vorticity
  
    # 1000 MB equivalent potential temperature  
    level = '1000.0MB'
    try:
      T  = data.getVar( 'temperature', level )
      Td = data.getVar( 'dewpoint',    level )
    except:
      pass
    else:
      self.log.debug( 'Computing equivalent potential temperature at 1000 hPa' )
      data['theta_e'] = {
        level : equivalent_potential_temperature( 1000.0 * units('hPa'), T, Td )
      }
  
      return data
      # MLCAPE
      self.log.debug( 'Computing mixed layer CAPE' )
      T_lvl   = list( data[T].keys()  )
      Td_lvl  = list( data[Td].keys() )
      levels  = list( set( T_lvl ).intersection( Td_lvl ) )
      levels  = [float(lvl.replace('MB','')) for lvl in levels]
      levels  = sorted( levels, reverse=True )
  
      nLvl    = len(levels)
      if nLvl > 0:
        self.log.debug( 'Found {} matching levels in temperature and dewpoint data'.format(nLvl) )
        nLat, nLon = data['lon'].shape
        
        data['MLCAPE'] = np.zeros( (nLat, nLon,),       dtype=np.float32 ) * units('J/kg')
        TT             = np.zeros( (nLvl, nLat, nLon,), dtype=np.float32 ) * units('degC')
        TTd            = np.zeros( (nLvl, nLat, nLon,), dtype=np.float32 ) * units('degC')
    
        self.log.debug( 'Sorting temperature and dewpoint data by level' )
        for i in range( nLvl ):
          key = '{:.1f}MB'.format( levels[i] )
          TT[i,:,:]  = data[T][key].to('degC')
          TTd[i,:,:] = data[Td][key].to('degC')
        
        levels   = np.array( levels ) * units.hPa
        depth    = 100.0 * units.hPa
  
        self.log.debug( 'Iterating over grid boxes to compute MLCAPE' )
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
              self.log.warning( 
                'Failed to compute MLCAPE for lon/lat: {}; {}'.format(
                  data['lon'][j,i], data['lat'][j,i]
                )
              )
            else:
              data['MLCAPE'][j,i] = cape

    return data                                                                  # Return data dictionary  
