import logging;
import os, uuid, json;
from awips.dataaccess import DataAccessLayer as DAL;
import matplotlib.pyplot as plt;
import cartopy.crs as ccrs;

from .data_backends.awips_model_utils import awips_fcst_times, awips_model_base;
from .data_backends.awips_models import NAM40;

from .plotting.plot_utils       import initFigure, xy_transform, getMapExtentScale;
from .plotting.model_plots      import (
  plot_rh_mslp_thick,
  plot_srfc_temp_barbs,
  plot_1000hPa_theta_e_barbs,
  plot_850hPa_temp_hght_barbs,
  plot_500hPa_vort_hght_barbs,
  plot_250hPa_isotach_hght_barbs
)

dir = os.path.dirname( os.path.realpath(__file__) );
with open( os.path.join( dir, 'plot_opts.json' ), 'r' ) as fid:
  opts = json.load(fid);

def NAM40_Products( outdir = None, dpi = 120, interval = 6 ):
  '''
  Name:
    NAM40_Products
  Purpose:
    A function to get data from NAM40 model to create HDWX products
  Inputs:
    times : List of datetimes to get data for
  Outputs:
    Returns a dictionary containing all data
  Keywords:
    interval : Interval, in hours, for forecast plot creation
    EDEX   : URL for EDEX host to use
  '''
  log = logging.getLogger(__name__);                                            # Set up function for logger
  log.info( 'Getting NAM40 data' );
  
  if outdir is None:
    outdir = os.path.join( os.path.expanduser('~'), 'HDWX' );
  if not os.path.isdir(outdir): os.makedirs( outdir );
  
  DAL.changeEDEXHost( "edex-cloud.unidata.ucar.edu" )
  
  request = DAL.newDataRequest();
  request.setDatatype("grid");
  request.setLocationNames( NAM40['model_name'] );
  
  initTime, fcstTimes, times = awips_fcst_times( request );
  timeFMT   = '%Y%m%dT%H%M%S'
  scale     = 2.5e5
  transform = ccrs.PlateCarree();
  mapProj   = ccrs.LambertConformal(
                           central_longitude = -100.0, 
                           central_latitude  =   40.0); 

  dirs = {'4-panel'  : os.path.join( outdir, '4-panel'  ),
          'mslp'     : os.path.join( outdir, 'mslp'     ),
          'surface'  : os.path.join( outdir, 'surface'  ),
          '1000-hPa' : os.path.join( outdir, '1000-hPa' ),
          '850-hPa'  : os.path.join( outdir, '850-hPa'  ),
          '500-hPa'  : os.path.join( outdir, '500-hPa'  ),
          '250-hPa'  : os.path.join( outdir, '250-hPa'  )}
  for key, val in dirs.items():                                                 # Iterate over all key/value pairs in dictionary
    if not os.path.isdir(val):                                                  # If the directory does NOT exist
      os.makedirs( val );                                                       # Create it

  fig = plt.figure( **opts['figure_opts'] )
  plt.subplots_adjust( **opts['subplot_adjust'] );                              # Set up subplot margins

  # for i in range( len(times) ):
  for i in range( 1 ):
    if (fcstTimes[i].hour % interval) != 0: continue;                           # If the forecast hour does not fall on the requested interval, skip it
    period = times[i].getValidPeriod().duration() // 3600;                      # Get the period over which the forecast time is valid
    if (period != 1) and ((period % interval) != 0): continue;                  # If the period is NOT an hour AND NOT the interval, continue

    fcstTime = fcstTimes[i].strftime(timeFMT)
    
    base_file  = '{}_{}.png'.format( NAM40['model_name'], fcstTime )
    filesExist = True;
    files      = {}
    for key, val in dirs.items():
      files[key] = os.path.join( val, base_file)
      if not os.path.isfile( files[key] ):
        filesExist = False

    if not filesExist:                                                          # If any of the plot files are missing
      data = awips_model_base( request, times[i], NAM40['model_vars'], NAM40['mdl2stnd'] )
      data['lon'], data['lat'] = xy_transform(
        mapProj, transform, data['lon'], data['lat']
      );                                                                        # Transform the data; saves some time

    # 4-panel plot
    fig.clf();
    if os.path.isfile( files['4-panel'] ):
      log.info( '4-Panel file exists, skipping: {}'.format(fcstTimes[i]) )
    else:
      log.info( 'Creating 4-panel image for: {}'.format(fcstTimes[i]) )
      ax = [ fig.add_subplot(221, projection = mapProj, label = uuid.uuid4()),
             fig.add_subplot(222, projection = mapProj, label = uuid.uuid4()),
             fig.add_subplot(223, projection = mapProj, label = uuid.uuid4()),
             fig.add_subplot(224, projection = mapProj, label = uuid.uuid4())]

      extent, scale = getMapExtentScale( ax[0], data['lon'], data['lat'] )
      plot_500hPa_vort_hght_barbs(    ax[0], data, extent = extent );
      plot_250hPa_isotach_hght_barbs( ax[1], data, extent = extent );
      plot_850hPa_temp_hght_barbs(    ax[2], data, extent = extent );
      plot_rh_mslp_thick(        ax[3], data, extent = extent );

      fig.savefig( files['4-panel'], dpi = dpi )

    extent = None
    # MSLP plot
    fig.clf();
    if os.path.isfile( files['mslp'] ):
      log.info( 'MSLP file exists, skipping: {}'.format(fcstTimes[i]) )
    else:
      log.info( 'Creating MSLP image for: {}'.format(fcstTimes[i]) )
      ax = fig.add_subplot(111, projection = mapProj, label = uuid.uuid4())
      if extent is None:
        extent, scale = getMapExtentScale( ax, data['lon'], data['lat'] );

      plot_rh_mslp_thick( ax, data, extent = extent )
      fig.savefig( files['mslp'], dpi = dpi )

    # Surface temps and wind
    fig.clf();
    if os.path.isfile( files['surface'] ):
      log.info( 'surface file exists, skipping: {}'.format(fcstTimes[i]) )
    else:
      log.info( 'Creating surface image for: {}'.format(fcstTimes[i]) )
      ax = fig.add_subplot(111, projection = mapProj, label = uuid.uuid4())
      if extent is None:
        extent, scale = getMapExtentScale( ax, data['lon'], data['lat'] );

      plot_srfc_temp_barbs( ax, data, extent = extent )
      fig.savefig( files['surface'], dpi = dpi )

    # 1000-hPa Theta-E Plot
    fig.clf();
    if os.path.isfile( files['1000-hPa'] ):
      log.info( '1000-hPa file exists, skipping: {}'.format(fcstTimes[i]) )
    else:
      log.info( 'Creating 1000-hPa image for: {}'.format(fcstTimes[i]) )
      ax = fig.add_subplot(111, projection = mapProj, label = uuid.uuid4())
      if extent is None:
        extent, scale = getMapExtentScale( ax, data['lon'], data['lat'] );

      plot_1000hPa_theta_e_barbs( ax, data, extent = extent )
      fig.savefig( files['1000-hPa'], dpi = dpi )

    # 850-hPa Plot
    fig.clf();
    if os.path.isfile( files['850-hPa'] ):
      log.info( '850-hPa file exists, skipping: {}'.format(fcstTimes[i]) )
    else:
      log.info( 'Creating 850-hPa image for: {}'.format(fcstTimes[i]) )
      ax = fig.add_subplot(111, projection = mapProj, label = uuid.uuid4())
      if extent is None:
        extent, scale = getMapExtentScale( ax, data['lon'], data['lat'] );

      plot_850hPa_temp_hght_barbs( ax, data, extent = extent )
      fig.savefig( files['850-hPa'], dpi = dpi )
      

    # 500-hPa Plot
    fig.clf();
    if os.path.isfile( files['500-hPa'] ):
      log.info( '500-hPa file exists, skipping: {}'.format(fcstTimes[i]) )
    else:
      log.info( 'Creating 500-hPa image for: {}'.format(fcstTimes[i]) )
      ax = fig.add_subplot(111, projection = mapProj, label = uuid.uuid4())
      if extent is None:
        extent, scale = getMapExtentScale( ax, data['lon'], data['lat'] );

      plot_500hPa_vort_hght_barbs( ax, data, extent = extent )
      fig.savefig( files['500-hPa'], dpi = dpi )
      

    # 250-hPa Plot
    fig.clf();
    if os.path.isfile( files['250-hPa'] ):
      log.info( '250-hPa file exists, skipping: {}'.format(fcstTimes[i]) )
    else:
      log.info( 'Creating 250-hPa image for: {}'.format(fcstTimes[i]) )
      ax = fig.add_subplot(111, projection = mapProj, label = uuid.uuid4())
      if extent is None:
        extent, scale = getMapExtentScale( ax, data['lon'], data['lat'] );

      plot_250hPa_isotach_hght_barbs( ax, data, extent = extent )
      fig.savefig( files['250-hPa'], dpi = dpi )