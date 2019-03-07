import logging;

from awips.dataaccess import DataAccessLayer as DAL;

from .awips_model_utils import awips_fcst_times, awips_model_base;
from .awips_models import NAM40;



def NAM40_awips( time, EDEX = "edex-cloud.unidata.ucar.edu" ):
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

  DAL.changeEDEXHost( EDEX )

  request = DAL.newDataRequest();
  request.setDatatype("grid");
  request.setLocationNames( NAM40['model_name'] );

  times = awips_fcst_times( request );

  return awips_model_base( request, NAM40['model_vars'], NAM40['mdl2stnd'], EDEX = EDEX )