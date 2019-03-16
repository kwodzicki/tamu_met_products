import logging
import os, json;
import cartopy.feature as cfeature
from matplotlib.pyplot import colorbar;

dir = os.path.dirname( os.path.realpath(__file__) );
with open( os.path.join( dir, 'plot_opts.json' ), 'r' ) as fid:
  opts = json.load(fid);
  
################################################################################
def baseLabel(model, initTime, fcstTime):
  '''
  Name:
    baseLabel
  Purpose:
    A python function create time labels for plot
  Inputs:
    model    : Name of the model
    initTime : Datetime object with model initialization time
    fcstTime : Datetime object with model forecast time
  Keywords:
    None
  Outputs:
    Returns two element list
  '''  
  initFMT  = '%y%m%d/%H%M'
  fcstFMT  = '%a %y%m%d/%H%M'
  dTime    = int( (fcstTime - initTime).total_seconds() / 3600.0 )
  initTime = '{}F{:03d}'.format( initTime.strftime( initFMT ), dTime )
  fcstTime = '{}V{:03d}'.format( fcstTime.strftime( fcstFMT ), dTime )
  return ['{} FORECAST INIT {}'.format(    model, initTime ),
         '{:03d}-HR FCST VALID {}'.format( dTime, fcstTime )]

################################################################################
def plot_basemap(ax, **kwargs):
  '''
  Name:
    plot_basemap
  Purpose:
    A python function to set up base maps for an axis
  Inputs:
    ax    : Axis to plot on
  Keywords:
    Arguments for set_extent, and cartopy cfeatures
  Outputs:
    Returns the update axis object
  '''  
  log        = logging.getLogger(__name__)
  scale      = kwargs.pop( 'scale',      5.0e5 );
  resloution = kwargs.pop( 'resolution', '50m' );
  linewidth  = kwargs.pop( 'linewidth',  0.5 );

  ax.outline_patch.set_visible(False);                                          # Remove frame from plot
  fig_w,fig_h = ax.figure.get_size_inches() * 2.54;                             # Get size of figure in centimeters
  log.debug( 'Figure size: {:5.2f}x{:5.2f}'.format( fig_w, fig_h) );

  ax_x0,ax_y0,ax_w,ax_h = ax._position.bounds;                                  # Get size of axes relative to figure size
  log.debug( 'Axis size:   {:5.3f}x{:5.3f}, {:5.3f}x{:5.3f}'.format( ax_x0, ax_y0, ax_w,  ax_h) );

  dx = scale * (fig_w * ax_w) / 2.0;                                            # Multiply figure width by axis width, divide by 2 and multiply by scale
  dy = scale * (fig_h * ax_h) / 2.0;                                            # Multiply figure height by axis height, divide by 2 and multiply by scale
 
  log.debug( 'Map Extent:   {:5.3f}, {:5.3f}, {:5.3f}, {:5.3f}'.format( -dx, dx, -dy, dy) );

  log.debug('Setting axis extent')  
  ax.set_extent( (-dx, dx, -dy, dy), ax.projection );                           # Set axis extent
  log.debug('Adding coast line')  
  ax.add_feature(cfeature.COASTLINE.with_scale(resloution), linewidth=linewidth)
  log.debug('Adding states')  
  ax.add_feature(cfeature.STATES, linewidth=linewidth)
  log.debug('Adding borders')  
  ax.add_feature(cfeature.BORDERS, linewidth=linewidth)
  return ax, scale

################################################################################
def add_colorbar( mappable, ax, ticks, **kwargs ):
  log = logging.getLogger(__name__);
  log.debug('Creating color bar')
  fontsize = kwargs.pop('fontsize', 8);                                         # Pop off fontsize from keywords
  title    = kwargs.pop('title',    None);
  ax_x0, ax_y0, ax_w, ax_h = ax._position.bounds;                               # Get size of axes relative to figure size
  ax_w  /=  4.0 
  ax_h  /= 40.0
  cb_ax  = ax.figure.add_axes( (ax_x0, ax_y0-3*ax_h, ax_w, ax_h) )
  cbar   = colorbar(mappable, cax=cb_ax, ticks=ticks, **opts['colorbar_Opts'])
  cbar.ax.xaxis.set_ticks_position('top');                                      # Place labels on top of color bar
  if fontsize:
    x_ticks = cbar.ax.get_xticklabels();
    y_ticks = cbar.ax.get_yticklabels()
    cbar.ax.set_xticklabels(x_ticks, fontsize=fontsize)
    cbar.ax.set_yticklabels(y_ticks, fontsize=fontsize)

  if title:
    cbar.set_label(title, size=fontsize)
    
  return cbar;

################################################################################
def plot_barbs( ax, scale, xx, yy, u, v ):
  skip = int( round(scale / abs(xx[0,1]-xx[0,0]) ) )//2
  ax.barbs( xx[::skip,::skip],         yy[::skip,::skip], 
            u.to('kts')[::skip,::skip].m, v.to('kts')[::skip,::skip].m, 
            **opts['barb_Opts']
  )

################################################################################
def xy_transform( proj, transform, xx, yy):
  '''
  Name:
    xy_tranform
  Purpose:
    A helper function to transform x- and y-values from the
    'transform' projection to the GeoAxes 'ax' projection.
  Inputs:
    proj      : Projection to project data to
    transform : A cartopy projection for the x- and y-values
    xx        : X-values; typically longitudes
    yy        : Y-values; typically latitudes
  Outputs:
    Returns the re-projected x- and y-values
  Keywords:
    None.
  '''
  if hasattr(xx, 'magnitude'): xx = xx.magnitude;                               # IF has a magnitude attribute, then is a Quantity object so get magnitude
  if hasattr(yy, 'magnitude'): yy = yy.magnitude;                               # IF has a magnitude attribute, then is a Quantity object so get magnitude
  xyz = proj.transform_points(transform, xx, yy);                               # Project x- and y-values to map; cuts down on projecting multiple times
  return xyz[:,:,0], xyz[:,:,1]