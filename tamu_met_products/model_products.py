import logging
import os, uuid, json

from awips.dataaccess import DataAccessLayer as DAL
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

from .data_backends.awips_model_utils import get_init_fcst_times, AWIPSModelDownloader
from .data_backends.awips_models import NAM40, GFS

from .plotting.plot_utils       import initFigure, xy_transform, getMapExtentScale
from .plotting.model_plots      import (
  plot_rh_mslp_thick,
  plot_precip_mslp_temps, 
  plot_srfc_temp_barbs,
  plot_1000hPa_theta_e_barbs,
  plot_850hPa_temp_hght_barbs,
  plot_500hPa_vort_hght_barbs,
  plot_250hPa_isotach_hght_barbs
)

dir = os.path.dirname( os.path.realpath(__file__) )
with open( os.path.join( dir, 'plot_opts.json' ), 'r' ) as fid:
  opts = json.load(fid)

def NAM40_Products( **kwargs ):
  """
  Get data from NAM40 model to create HDWX products

  Arguments:
    None.

  Keyword arguments:
    outdir (str) : Diretory to seave images to
    dpi (int) : Dots-per-inch for output plots
    interval (int) : Interval, in seconds, for forecast plot creation.
                 Default is 6 hourly (21600 s)
    EDEX   : URL for EDEX host to use

  """

  downloader = AWIPSModelDownloader( NAM40['model_name'], **kwargs )
  times      = downloader.fcst_times()
  for time in times:
    if time:
      data = downloader.getData( time, NAM40['model_vars'], NAM40['mdl2stnd'] )
      standardProducts(data, **kwargs )

def GFS_Products( **kwargs ):
  """
  Get data from GFS model to create HDWX products

  Arguments:
    None.

  Keyword arguments:
    outdir (str) : Diretory to seave images to
    dpi (int) : Dots-per-inch for output plots
    interval (int) : Interval, in seconds, for forecast plot creation.
                 Default is 6 hourly (21600 s)
    EDEX   : URL for EDEX host to use

  """

  downloader = AWIPSModelDownloader( GFS['model_name'], **kwargs )
  times      = downloader.fcst_times()
  for time in times:
    if time:
      data = downloader.getData( time, GFS['model_vars'], GFS['mdl2stnd'] )
      standardProducts(data, scale = GFS['map_scale'], **kwargs )
      #standardProducts( data, scale = GFS['map_scale'], **kwargs )

def standardProducts( data, outdir = None, dpi = 120, interval = 21600, scale = None ):
  """
  Generate 'standard' model products for the HDWX page

  Arguments:
    data (AWIPSData) : Data downlaoded from EDEX server for plotting

  Keyword arguments:
    dpi (int) : Dots per inch of the output images
    interval (int) : Interval, in seconds, for forecast plot creation.
      Default is 6 hourly (21600 s)
    scale (float) : Scaling for maps; meters in projection per cm on page

  Returns:
    None.

  """

  log = logging.getLogger(__name__)                                            # Set up function for logger
  # log.info( 'Getting {} data'.format( modelInfo['model_name'] ) )
  
  if outdir is None:
    outdir = os.path.join( os.path.expanduser('~'), 'HDWX', data['model'] )
  if not os.path.isdir(outdir): 
    os.makedirs( outdir )
    
  timeFMT   = '%Y%m%dT%H%M%S'

  transform = ccrs.PlateCarree()
  mapOpts   = opts['projection'].copy()
  mapProj   = getattr( ccrs, mapOpts.pop('name') )
  mapProj   = mapProj( **mapOpts ) 
  #mapProj   = ccrs.LambertConformal(
  #                         central_longitude = -100.0, 
  #                         central_latitude  =   40.0) 

  dirs = {'4-panel'  : os.path.join( outdir, '4-panel'  ),
          'mslp'     : os.path.join( outdir, 'mslp'     ),
          'surface'  : os.path.join( outdir, 'surface'  ),
          '1000-hPa' : os.path.join( outdir, '1000-hPa' ),
          '850-hPa'  : os.path.join( outdir, '850-hPa'  ),
          '500-hPa'  : os.path.join( outdir, '500-hPa'  ),
          '250-hPa'  : os.path.join( outdir, '250-hPa'  ),
          'precip'   : os.path.join( outdir, 'precip'   )}
  for key, val in dirs.items():                                                 # Iterate over all key/value pairs in dictionary
    if not os.path.isdir(val):                                                  # If the directory does NOT exist
      os.makedirs( val )                                                       # Create it

  fig = plt.figure( **opts['figure_opts'] )
  plt.subplots_adjust( **opts['subplot_adjust'] )                              # Set up subplot margins

  fcstTime = data['fcstTime'].strftime(timeFMT)                           # Convert forecast time to string
  
  base_file  = '{}_{}.png'.format( data['model'], fcstTime )
  filesExist = True
  files      = {}
  for key, val in dirs.items():
    files[key] = os.path.join( val, base_file)
    if not os.path.isfile( files[key] ):
      filesExist = False

  if not filesExist:                                                          # If any of the plot files are missing
    data['lon'], data['lat'] = xy_transform(
      mapProj, transform, data['lon'], data['lat']
    )                                                                        # Transform the data; saves some time

  # 4-panel plot
  fig.clf()
  if os.path.isfile( files['4-panel'] ):
    log.info( '4-Panel file exists, skipping: {}'.format(fcstTime) )
  else:
    log.info( 'Creating 4-panel image for: {}'.format(fcstTime) )
    ax = [ fig.add_subplot(221, projection = mapProj, label = uuid.uuid4()),
           fig.add_subplot(222, projection = mapProj, label = uuid.uuid4()),
           fig.add_subplot(223, projection = mapProj, label = uuid.uuid4()),
           fig.add_subplot(224, projection = mapProj, label = uuid.uuid4())]

    extent, scale = getMapExtentScale( ax[0], data['lon'], data['lat'], scale = scale )
    plot_500hPa_vort_hght_barbs(    ax[0], data, extent=extent, scale=scale )
    plot_250hPa_isotach_hght_barbs( ax[1], data, extent=extent, scale=scale )
    plot_850hPa_temp_hght_barbs(    ax[2], data, extent=extent, scale=scale )
    plot_rh_mslp_thick(             ax[3], data, extent=extent, scale=scale )

    fig.savefig( files['4-panel'], dpi = dpi )

  extent = None
  # MSLP plot
  fig.clf()
  if os.path.isfile( files['mslp'] ):
    log.info( 'MSLP file exists, skipping: {}'.format(fcstTime) )
  else:
    log.info( 'Creating MSLP image for: {}'.format(fcstTime) )
    ax = fig.add_subplot(111, projection = mapProj, label = uuid.uuid4())
    if extent is None:
      extent, scale = getMapExtentScale( ax, data['lon'], data['lat'], scale = scale )

    plot_rh_mslp_thick( ax, data, extent = extent )
    fig.savefig( files['mslp'], dpi = dpi )

  # Precip plot
  fig.clf()
  if os.path.isfile( files['precip'] ):
    log.info( 'Precip file exists, skipping: {}'.format(fcstTime) )
  else:
    log.info( 'Creating precip image for: {}'.format(fcstTime) )
    ax = fig.add_subplot(111, projection = mapProj, label = uuid.uuid4())
    if extent is None:
      extent, scale = getMapExtentScale( ax, data['lon'], data['lat'], scale = scale )

    plot_precip_mslp_temps( ax, data, extent = extent )
    fig.savefig( files['precip'], dpi = dpi )

  # Surface temps and wind
  fig.clf()
  if os.path.isfile( files['surface'] ):
    log.info( 'surface file exists, skipping: {}'.format(fcstTime) )
  else:
    log.info( 'Creating surface image for: {}'.format(fcstTime) )
    ax = fig.add_subplot(111, projection = mapProj, label = uuid.uuid4())
    if extent is None:
      extent, scale = getMapExtentScale( ax, data['lon'], data['lat'], scale = scale )

    plot_srfc_temp_barbs( ax, data, extent = extent )
    fig.savefig( files['surface'], dpi = dpi )

  # 1000-hPa Theta-E Plot
  fig.clf()
  if os.path.isfile( files['1000-hPa'] ):
    log.info( '1000-hPa file exists, skipping: {}'.format(fcstTime) )
  else:
    log.info( 'Creating 1000-hPa image for: {}'.format(fcstTime) )
    ax = fig.add_subplot(111, projection = mapProj, label = uuid.uuid4())
    if extent is None:
      extent, scale = getMapExtentScale( ax, data['lon'], data['lat'], scale = scale )

    plot_1000hPa_theta_e_barbs( ax, data, extent = extent )
    fig.savefig( files['1000-hPa'], dpi = dpi )

  # 850-hPa Plot
  fig.clf()
  if os.path.isfile( files['850-hPa'] ):
    log.info( '850-hPa file exists, skipping: {}'.format(fcstTime) )
  else:
    log.info( 'Creating 850-hPa image for: {}'.format(fcstTime) )
    ax = fig.add_subplot(111, projection = mapProj, label = uuid.uuid4())
    if extent is None:
      extent, scale = getMapExtentScale( ax, data['lon'], data['lat'], scale = scale )

    plot_850hPa_temp_hght_barbs( ax, data, extent = extent )
    fig.savefig( files['850-hPa'], dpi = dpi )
    

  # 500-hPa Plot
  fig.clf()
  if os.path.isfile( files['500-hPa'] ):
    log.info( '500-hPa file exists, skipping: {}'.format(fcstTime) )
  else:
    log.info( 'Creating 500-hPa image for: {}'.format(fcstTime) )
    ax = fig.add_subplot(111, projection = mapProj, label = uuid.uuid4())
    if extent is None:
      extent, scale = getMapExtentScale( ax, data['lon'], data['lat'], scale = scale )

    plot_500hPa_vort_hght_barbs( ax, data, extent = extent )
    fig.savefig( files['500-hPa'], dpi = dpi )
    

  # 250-hPa Plot
  fig.clf()
  if os.path.isfile( files['250-hPa'] ):
    log.info( '250-hPa file exists, skipping: {}'.format(fcstTime) )
  else:
    log.info( 'Creating 250-hPa image for: {}'.format(fcstTime) )
    ax = fig.add_subplot(111, projection = mapProj, label = uuid.uuid4())
    if extent is None:
      extent, scale = getMapExtentScale( ax, data['lon'], data['lat'], scale = scale )

    plot_250hPa_isotach_hght_barbs( ax, data, extent = extent )
    fig.savefig( files['250-hPa'], dpi = dpi )
