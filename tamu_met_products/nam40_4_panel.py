import logging;
import os
from awips.dataaccess import DataAccessLayer as DAL;

from .data_backends.awips_model_utils import awips_fcst_times, awips_model_base;
from .data_backends.awips_models import NAM40;

from .plotting.forecast_4_panel import forecast_4_panel

home = os.path.expanduser('~')

def NAM40_4_Panel():
  '''
  Name:
    NAM40_awips
  Purpose:
    A function to get data from NAM40 model to create HDWX products
  Inputs:
    times : List of datetimes to get data for
  Outputs:
    Returns a dictionary containing all data
  Keywords:
    EDEX   : URL for EDEX host to use
  '''
  log = logging.getLogger(__name__);                                            # Set up function for logger
  log.info( 'Getting NAM40 data' );
  
  outdir = os.path.join( home, 'NAM_4_Panel' );
  if not os.path.isdir(outdir): os.makedirs( outdir );
  
  DAL.changeEDEXHost( "edex-cloud.unidata.ucar.edu" )
  
  request = DAL.newDataRequest();
  request.setDatatype("grid");
  request.setLocationNames( NAM40['model_name'] );
  
  initTime, fcstTimes, times = awips_fcst_times( request );
  
  timeFMT = '%Y%m%dT%H%M%S'
  for i in range( len(times) ):
    fcstTime = fcstTimes[i].strftime(timeFMT)
    fileName = '{}_{}.png'.format( NAM40['model_name'], fcstTime )
    filePath = os.path.join( outdir, fileName );
    if os.path.isfile( filePath ):
      log.info( 'File exists, skipping: {}'.format(fcstTimes[i]) )
    else:
      log.info( 'Creating image for: {}'.format(fcstTimes[i]) )
      data = awips_model_base( request, times[i], NAM40['model_vars'], NAM40['mdl2stnd'] )  
      fig  = forecast_4_panel( data, initTime, fcstTimes[i] );
      fig.savefig( filePath )
