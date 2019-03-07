import logging;
import numpy as np;
from metpy.units import units
from metpy.calc import absolute_vorticity, lat_lon_grid_deltas;
from awips.dataaccess import DataAccessLayer as DAL;


log = logging.getLogger(__name__);
srm = logging.StreamHandler()
srm.setLevel(logging.DEBUG)
log.setLevel(logging.DEBUG)
log.addHandler( srm )

DAL.changeEDEXHost("edex-cloud.unidata.ucar.edu")

request = DAL.newDataRequest()
request.setDatatype("grid")
request.setLocationNames("NAM40")


vars = {
  'winds' : {'parameters' : ['uW', 'vW'],
             'levels'     : ['850.0MB', '500.0MB', '250.0MB']},
  'temp'  : {'parameters' : ['T'], 
             'levels'     : ['850.0MB']},
  'geoH'  : {'parameters' : ['GH'],
             'levels'     : ['1000.0MB', '850.0MB', '500.0MB', '250.0MB']},
  'MSLP'  : {'parameters' : ['PMSL'],
             'levels'     : ['0.0MSL']},
  'RH'    : {'parameters' : ['RH'],
             'levels'     : ['700.0MB']}
}



def populate_outdata( lon, lat ):
  ny, nx  = lon.shape;
  outdata = {'lon' : 
                {'values' : lon, 
                 'levels' : None,
                 'units'  : None},
            'lat' : 
              {'values' : lat,
               'levels' : None,
               'units'  : None}
            }
  for var in vars:
    for par in vars[var]['parameters']:
      lvls         = vars[var]['levels']
      outdata[par] = {'values' : np.full( (len( lvls ), ny, nx,), np.nan ),
                      'levels' : lvls,
                      'units'  : None}
  return outdata
    

def NAM40_awips():
  log = logging.getLogger(__name__);
  outdata = None;
  log.info('Attempting to download NAM40 data')
  for var in vars:
    log.debug( 'Getting: {}'.format( var ) );
    request.setParameters( *vars[var]['parameters'] );
    request.setLevels(     *vars[var]['levels'] );

    cycles   = DAL.getAvailableTimes(request, True)
    times    = DAL.getAvailableTimes(request)
    fcstRun  = DAL.getForecastRun(cycles[-1], times)
    response = DAL.getGridData(request, [fcstRun[-1]])

    for res in response:
      if outdata is None: 
        lon, lat = res.getLatLonCoords();
        outdata = populate_outdata( lon, lat );
      varName = res.getParameter();                                             # Get name of the variable in the response
      varLvl  = res.getLevel();                                                 # Get level of the variable in the response
      if outdata[varName]['units'] is None:
        try:
          outdata[varName]['units'] = units( res.getUnit() );
        except:
          pass
      log.debug( 
        'Got data for:\n  Var:  {}\n  Lvl:  {}\n  Unit: {}'.format( varName, varLvl, outdata[varName]['units'] )
      )
      for i in range( len(outdata[varName]['levels']) ):                        # Iterate over all requested levels
        if outdata[varName]['levels'][i] == varLvl:                             # If found the level that matches
          outdata[varName]['values'][i,:,:] = res.getRawData();

  log.debug('Applying units to data values');
  for var in outdata:
    if (var == 'lon') or (var == 'lat'): continue;
    if outdata[var]['units']:
      outdata[var]['values'] *= outdata[var]['units']

  log.debug('Computing absolute vorticity');
  dx, dy = lat_lon_grid_deltas(
         outdata['lon']['values'], outdata['lat']['values']
  )
  outdata['ABSV'] = {'values' : np.full( outdata['uW']['values'].shape, np.nan ),
                     'levels' : outdata['uW']['levels'],
                     'unit'   : units('s^-1')}
  for i in range( len(outdata['uW']['levels']) ):
    outdata['ABSV']['values'][i,:,:] = absolute_vorticity(
      outdata['uW']['values'][i,:,:], outdata['vW']['values'][i,:,:], dx, dy, outdata['lat']['values']
    )
  return outdata