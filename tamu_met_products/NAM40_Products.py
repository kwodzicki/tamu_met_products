import logging;
import os, json;
from awips.dataaccess import DataAccessLayer as DAL;
import matplotlib.pyplot as plt;
import cartopy.crs as ccrs;

from .data_backends.awips_model_utils import awips_fcst_times, awips_model_base;
from .data_backends.awips_models import NAM40;

from .plotting.plot_utils       import initFigure, xy_transform;
from .plotting.forecast_4_panel import forecast_4_panel
from .plotting.model_plots      import (
  plot_srfc_rh_mslp_thick,
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

  dirs = {'4-panel' : os.path.join( outdir, '4-panel' ),
          'surface' : os.path.join( outdir, 'surface' ),
          '850-hPa' : os.path.join( outdir, '850-hPa' ),
          '500-hPa' : os.path.join( outdir, '500-hPa' ),
          '250-hPa' : os.path.join( outdir, '250-hPa' )}
  for key, val in dirs.items():                                                 # Iterate over all key/value pairs in dictionary
    if not os.path.isdir(val):                                                  # If the directory does NOT exist
      os.makedirs( val );                                                       # Create it

  for i in range(1):#range( len(times) ):
    if (fcstTimes[i].hour % interval) != 0: continue;                           # If the forecast hour does not fall on the requested interval, skip it
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
    if os.path.isfile( files['4-panel'] ):
      log.info( '4-Panel file exists, skipping: {}'.format(fcstTimes[i]) )
    else:
      log.info( 'Creating 4-panel image for: {}'.format(fcstTimes[i]) )
      fig  = forecast_4_panel( data, initTime, fcstTimes[i], map_projection = mapProj );
      fig.savefig( files['4-panel'], dpi = dpi )


    # Surface plot
    if os.path.isfile( files['surface'] ):
      log.info( 'Surface file exists, skipping: {}'.format(fcstTimes[i]) )
    else:
      log.info( 'Creating surface image for: {}'.format(fcstTimes[i]) )
      fig, ax = initFigure(1, 1)

      plot_srfc_rh_mslp_thick(
        ax, data['lon'], data['lat'],
        data['rh 700.0MB'], data['mslp 0.0MSL'], 
        data['geo_hght 1000.0MB'], data['geo_hght 500.0MB'],
        data['model'], initTime, fcstTimes[i],
        scale = scale 
      )
      fig.savefig( files['surface'], dpi = dpi )


    # 850-hPa Plot
    if os.path.isfile( files['850-hPa'] ):
      log.info( '850-hPa file exists, skipping: {}'.format(fcstTimes[i]) )
    else:
      log.info( 'Creating 850-hPa image for: {}'.format(fcstTimes[i]) )
      fig, ax = initFigure(1, 1)

      plot_850hPa_temp_hght_barbs(
        ax, data['lon'], data['lat'],
        data['temp 850.0MB'], data['geo_hght 850.0MB'], 
        data['model'], initTime, fcstTimes[i], 
        u = data['u_wind 850.0MB'], 
        v = data['v_wind 850.0MB'],
        scale = scale
      )
      fig.savefig( files['850-hPa'], dpi = dpi )

    # 500-hPa Plot
    if os.path.isfile( files['500-hPa'] ):
      log.info( '500-hPa file exists, skipping: {}'.format(fcstTimes[i]) )
    else:
      log.info( 'Creating 500-hPa image for: {}'.format(fcstTimes[i]) )
      fig, ax = initFigure(1, 1)

      plot_500hPa_vort_hght_barbs( 
        ax, data['lon'], data['lat'],
        data['abs_vor 500.0MB'], data['geo_hght 500.0MB'], 
        data['model'], initTime, fcstTimes[i], 
        u = data['u_wind 500.0MB'], 
        v = data['v_wind 500.0MB'] ,
        scale = scale
      )
      fig.savefig( files['500-hPa'], dpi = dpi )

    # 250-hPa Plot
    if os.path.isfile( files['250-hPa'] ):
      log.info( '250-hPa file exists, skipping: {}'.format(fcstTimes[i]) )
    else:
      log.info( 'Creating 250-hPa image for: {}'.format(fcstTimes[i]) )
      fig, ax = initFigure(1, 1)

      plot_250hPa_isotach_hght_barbs(
        ax, data['lon'], data['lat'],
        data['u_wind 250.0MB'],  data['v_wind 250.0MB'], data['geo_hght 250.0MB'],
        data['model'], initTime, fcstTimes[i],
        scale = scale
      )
      fig.savefig( files['250-hPa'], dpi = dpi )


  
  

