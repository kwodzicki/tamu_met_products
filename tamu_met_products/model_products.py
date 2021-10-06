import logging
import os, uuid, json
from datetime import datetime

from awips.dataaccess import DataAccessLayer as DAL
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

from .data_backends.awips_model_utils import get_init_fcst_times, AWIPSModelDownloader, ISO
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

class ModelPlotter( object ):
  """
  Generate model products from various different models
  """

  TIMEFMT   = '%Y%m%dT%H%M%S'

  def __init__(self, outdir = None, **kwargs):
    self.log = logging.getLogger(__name__)                                            # Set up function for logger

    self._model = '' 
    self._dirs  = {}

    self.outdir = outdir 
      

    mapOpts        = opts['projection'].copy()
    mapProj        = getattr( ccrs, mapOpts.pop('name') )
    self.mapProj   = mapProj( **mapOpts ) 
    self.transform = ccrs.PlateCarree()

    self.fig       = plt.figure( **opts['figure_opts'] )
    plt.subplots_adjust( **opts['subplot_adjust'] )                              # Set up subplot margins

  @property
  def outdir(self):
    return os.path.join( self._outdir, self.model )
  @outdir.setter
  def outdir(self, val):
    if val is None:
      self._outdir = os.path.join( os.path.expanduser('~'), 'HDWX' )
    else:
      self._outdir = val

  @property
  def model(self):
    return self._model
  @model.setter
  def model(self, val):
    self._model  = val
    self._dirs = {'4-panel'  : os.path.join( self.outdir, '4-panel'  ),
                  'mslp'     : os.path.join( self.outdir, 'mslp'     ),
                  'surface'  : os.path.join( self.outdir, 'surface'  ),
                  '1000-hPa' : os.path.join( self.outdir, '1000-hPa' ),
                  '850-hPa'  : os.path.join( self.outdir, '850-hPa'  ),
                  '500-hPa'  : os.path.join( self.outdir, '500-hPa'  ),
                  '250-hPa'  : os.path.join( self.outdir, '250-hPa'  ),
                  'precip'   : os.path.join( self.outdir, 'precip'   )}

  @property
  def dirs(self):
    return self._dirs

  def checkFile(self, date, product, update=False, makedirs=True):
    sfile = self.filePath( date, product )

    if not update and os.path.isfile( sfile  ):
      self.log.info( f'File exists, skipping: {sfile}' )
      return None
    if makedirs:
      root = os.path.dirname( sfile )
      if not os.path.isdir( root ): os.makedirs( root )
    return sfile

  def filterTimes(self, dates):
    toDownload = []                                                             # List of times to download
    for date in dates:                                                          # Iterate over all dates
      files = self.filePaths( date )                                            # Get list of files for given date
      if not all( map( os.path.isfile, files.values() ) ):                      # If NOT all of the files exist
        toDownload.append( date )                                               # Append date toDownload list
    return toDownload 

  def filePath( self, date, product, root=None ):
    """
    Generate full path to given product image

    Arguments:
      date (DataTime) : Date for the forecast
      product (str) : Name of product to be created

    Keyword arguments:
      root (str) : Root directory to place images in. If None provided
        self.dirs[ product ] is used.

    """

    if isinstance( date, (list, tuple)): date = date[0]
    if root is None: root = self.dirs.get(product)

    initTime, fcstTime = get_init_fcst_times( date, strfmt = self.TIMEFMT )

    fileName  = f'{self.model}_{fcstTime}.png'
    return os.path.join( root, initTime, fileName )

  def filePaths( self, date ):
    files = {}
    for product, root in self.dirs.items():
      try:
        files[product] = self.filePath( date, product, root )
      except Exception as err:
        self.log.debug( f'Hit weird time index exception : {err}' )
        pass
    return files

  def _clearFig( self ):
    """Clear current figure plot"""

    if self.fig:
      self.log.debug( 'Clearing figure' )
      self.fig.clf()

  def NAM40_Products( self, **kwargs ):
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

    self.model = NAM40['model_name']
 
    downloader = AWIPSModelDownloader( NAM40['model_name'], **kwargs )
    times      = downloader.fcst_times()
    if not kwargs.get('update', False):
      times      = self.filterTimes( times )
    
    for data in downloader.getData( times, NAM40['model_vars'], NAM40['mdl2stnd'] ):
      self.standardProducts(data, **kwargs )

  
  def GFS_Products( self, **kwargs ):
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
    self.model = GFS['model_name']
 
    downloader = AWIPSModelDownloader( GFS['model_name'], **kwargs )
    times      = downloader.fcst_times()
    if not kwargs.get('update', False):
      times      = self.filterTimes( times )
    
    for data in downloader.getData( times, GFS['model_vars'], GFS['mdl2stnd'] ):
      self.standardProducts(data, scale = GFS['map_scale'], **kwargs )

  
  def standardProducts(self, data, dpi = 120, interval = 21600, scale = None, **kwargs ):
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
  
    data['lon'], data['lat'] = xy_transform(
       self.mapProj, self.transform, data['lon'], data['lat']
    )                                                                        # Transform the data; saves some time

    self.plot_4Panel(  data, **kwargs )
    self.plot_MSLP(    data, **kwargs )
    self.plot_precip(  data, **kwargs )
    self.plot_surface( data, **kwargs )
    self.plot_1000hPa( data, **kwargs )
    self.plot_850hPa(  data, **kwargs )
    self.plot_500hPa(  data, **kwargs )
    self.plot_250hPa(  data, **kwargs )

  def plot_4Panel( self, data, update=False, **kwargs ): 
    """Create 4-panel forecast product"""

    key   = '4-panel'
    sfile = self.checkFile( data['time'], key, update=update)
    if sfile:
      self._clearFig()
      self.log.info( 'Creating {} image for: {}'.format(key, data['fcstTime']) )
      os.makedirs( os.path.dirname( sfile ), exist_ok=True )
      ax = [ self.fig.add_subplot(221, projection = self.mapProj, label = uuid.uuid4()),
             self.fig.add_subplot(222, projection = self.mapProj, label = uuid.uuid4()),
             self.fig.add_subplot(223, projection = self.mapProj, label = uuid.uuid4()),
             self.fig.add_subplot(224, projection = self.mapProj, label = uuid.uuid4())]
  
      extent, scale = getMapExtentScale( ax[0], data['lon'], data['lat'], **kwargs )
      plot_500hPa_vort_hght_barbs(    ax[0], data, extent=extent, scale=scale )
      plot_250hPa_isotach_hght_barbs( ax[1], data, extent=extent, scale=scale )
      plot_850hPa_temp_hght_barbs(    ax[2], data, extent=extent, scale=scale )
      plot_rh_mslp_thick(             ax[3], data, extent=extent, scale=scale )
  
      self.fig.savefig( sfile, dpi = kwargs.get('dpi', None) )

  def plot_MSLP(self, data, update=False, **kwargs): 
    """Create plot with mean sea-level pressure"""

    key   = 'mslp'
    sfile = self.checkFile( data['time'], key, update=update)
    if sfile:
      self._clearFig()
      self.log.info( 'Creating {} image for: {}'.format(key, data['fcstTime']) )
      ax = self.fig.add_subplot(111, projection = self.mapProj, label = uuid.uuid4())
      extent, scale = getMapExtentScale( ax, data['lon'], data['lat'], **kwargs )
  
      plot_rh_mslp_thick( ax, data, extent = extent )
      self.fig.savefig( sfile, dpi = kwargs.get('dpi', None) )

  def plot_precip(self, data, update=False, **kwargs):
    """Create precipitation forecast product"""

    key   = 'precip'
    sfile = self.checkFile( data['time'], key, update=update)
    if sfile:
      self._clearFig()
      self.log.info( 'Creating {} image for: {}'.format(key, data['fcstTime']) )
      ax = self.fig.add_subplot(111, projection = self.mapProj, label = uuid.uuid4())
      extent, scale = getMapExtentScale( ax, data['lon'], data['lat'], **kwargs )
  
      plot_precip_mslp_temps( ax, data, extent = extent )
      self.fig.savefig( sfile, dpi = kwargs.get('dpi', None) )

  def plot_surface(self, data, update=False, **kwargs):
    """Create surface forecast product"""

    key   = 'surface'
    sfile = self.checkFile( data['time'], key, update=update)
    if sfile:
      self._clearFig()
      self.log.info( 'Creating {} image for: {}'.format(key, data['fcstTime']) )
      ax = self.fig.add_subplot(111, projection = self.mapProj, label = uuid.uuid4())
      extent, scale = getMapExtentScale( ax, data['lon'], data['lat'], **kwargs )
  
      plot_srfc_temp_barbs( ax, data, extent = extent )
      self.fig.savefig( sfile, dpi = kwargs.get('dpi', None) )

  def plot_1000hPa(self, data, update=False, **kwargs):
    """Create 1000hPa forecast product"""

    key   = '1000-hPa'
    sfile = self.checkFile( data['time'], key, update=update)
    if sfile:
      self._clearFig()
      self.log.info( 'Creating {} image for: {}'.format(key, data['fcstTime']) )
      ax = self.fig.add_subplot(111, projection = self.mapProj, label = uuid.uuid4())
      extent, scale = getMapExtentScale( ax, data['lon'], data['lat'], **kwargs )
  
      plot_1000hPa_theta_e_barbs( ax, data, extent = extent )
      self.fig.savefig( sfile, dpi = kwargs.get('dpi', None) )

  def plot_850hPa( self, data, update=False, **kwargs):
    """Create 850hPa forecast product"""

    key   = '850-hPa'
    sfile = self.checkFile( data['time'], key, update=update)
    if sfile:
      self._clearFig()

      self.log.info( 'Creating {} image for: {}'.format(key, data['fcstTime']) )
      ax = self.fig.add_subplot(111, projection = self.mapProj, label = uuid.uuid4())
      extent, scale = getMapExtentScale( ax, data['lon'], data['lat'], **kwargs )
  
      plot_850hPa_temp_hght_barbs( ax, data, extent = extent )
      self.fig.savefig( sfile, dpi = kwargs.get('dpi', None) )
 

  def plot_500hPa(self, data, update=False, **kwargs):
    """Create 500hPa forecast product"""

    key   = '500-hPa'
    sfile = self.checkFile( data['time'], key, update=update)
    if sfile:
      self._clearFig()
      self.log.info( 'Creating {} image for: {}'.format(key, data['fcstTime']) )
      ax = self.fig.add_subplot(111, projection = self.mapProj, label = uuid.uuid4())
      extent, scale = getMapExtentScale( ax, data['lon'], data['lat'], **kwargs )
  
      plot_500hPa_vort_hght_barbs( ax, data, extent = extent )
      self.fig.savefig( sfile, dpi = kwargs.get('dpi', None) )
  

  def plot_250hPa( self, data, update=False, **kwargs):
    """Create 250hPa forecast product"""

    key   = '250-hPa'
    sfile = self.checkFile( data['time'], key, update=update)
    if sfile:
      self._clearFig()
      self.log.info( 'Creating {} image for: {}'.format(key, data['fcstTime']) )
      ax = self.fig.add_subplot(111, projection = self.mapProj, label = uuid.uuid4())
      extent, scale = getMapExtentScale( ax, data['lon'], data['lat'], **kwargs )
  
      plot_250hPa_isotach_hght_barbs( ax, data, extent = extent )
      self.fig.savefig( sfile, dpi = kwargs.get('dpi', None) )
