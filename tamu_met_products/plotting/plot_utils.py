import logging
import os, uuid, json;
import matplotlib.pyplot as plt;
import cartopy.crs as ccrs;
import cartopy.feature as cfeature

dir = os.path.dirname( os.path.dirname(__file__) );
with open( os.path.join( dir, 'plot_opts.json' ), 'r' ) as fid:
  opts = json.load(fid);

################################################################################
def initFigure(nrows, ncols, **kwargs):
  if 'map_projection' in kwargs:                                                # If a map projection was input
    mapProj = kwargs.pop('map_projection');                                     # Use that projection
  else:                                                                         # Else
    mapProj  = getattr(ccrs, opts['projection']['name'] );                      # Default map projection from plotting options
    centLong = kwargs.pop('central_longitude', 
                          opts["projection"]["central_longitude"]);             # Default central longitude of projection
    centLat  = kwargs.pop('central_latitude',  
                          opts["projection"]["central_latitude"]);              # Default central latitude of projection
    mapProj  = mapProj( central_longitude = centLong, 
                        central_latitude  = centLat);                           # Projection of the figure

  if "figsize" in kwargs:  
    opts["figure_opts"]["figsize"] = kwargs["figsize"];
  if "dpi" in kwargs:
    opts["figure_opts"]["dpi"] = kwargs["dpi"];

  fig, ax  = plt.subplots(nrows=nrows, ncols=ncols, **opts["figure_opts"], 
                          subplot_kw={'projection': mapProj});                  # Set up figure with one (1) subplot
  plt.subplots_adjust( **opts['subplot_adjust'] );                              # Set up subplot margins
  return fig, ax

################################################################################
def getMapExtentScale(ax, xx = None, yy = None, scale = None):
  '''
  Name:
    getMapExtentScale
  Purpose:
    A python function to determine map extent based on data size
  Inputs:
    ax    : GeoAxis object to plot data on
  Keywords:
    xx  : x-values of data to plot. MUST BE USED WITH YY.
           If input, will be used to determine best scaling for x & y.
           Will override the scale keyword; i.e., if you want a specific
           scaling, use ONLY the scale keyword
    xx  : y-values of data to plot. MUST BE USED WITH xx.
           If input, will be used to determine best scaling for x & y.
           Will override the scale keyword; i.e., if you want a specific
           scaling, use ONLY the scale keyword
    scale : Set scale of the plot where scale is distance in meters that
             one (1) centimeter on the plot will covert. Will determine 
             extent based on plotting area.
  Outputs:
    Returns the map extent and map scale
  '''  
  log = logging.getLogger(__name__)

  fig_w,fig_h = ax.figure.get_size_inches() * 2.54;                             # Get size of figure in centimeters
  log.debug( 'Figure size: {:5.2f}x{:5.2f}'.format( fig_w, fig_h) );

  ax_x0,ax_y0,ax_w,ax_h = ax._position.bounds;                                  # Get size of axes relative to figure size
  log.debug( 'Axis size:   {:5.3f}x{:5.3f}, {:5.3f}x{:5.3f}'.format( ax_x0, ax_y0, ax_w,  ax_h) );
  
  if (xx is not None) and (yy is not None):
    msgFMT  = None;
    x_scale = (xx.max()-xx.min()) / (fig_w * ax_w)
    y_scale = (yy.max()-yy.min()) / (fig_h * ax_h)
    if scale is not None:
      msgFMT = 'Changing user defined scale: {:8.3f} -> {}'.format( scale, '{:8.3f}' )
    scale   = x_scale if (x_scale >= y_scale) else y_scale;
    if msgFMT is not None:
      log.info( msgFMT.format(scale) )

  dx      = scale * (fig_w * ax_w) / 2.0;                                       # Multiply figure width by axis width, divide by 2 and multiply by scale
  dy      = scale * (fig_h * ax_h) / 2.0;                                       # Multiply figure height by axis height, divide by 2 and multiply by scale
  extent  = (-dx, dx, -dy, dy)
  log.debug( 'Map Extent:   {:5.3f}, {:5.3f}, {:5.3f}, {:5.3f}'.format( *extent ) );
  
  return extent, scale

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
    Returns the update axis object and map extent
  '''  
  log        = logging.getLogger(__name__)
  resloution = kwargs.pop( 'resolution', '50m' );
  linewidth  = kwargs.pop( 'linewidth',  0.5 );

  if 'extent' in kwargs:
    extent = kwargs['extent'];
  else:
    kwargs['scale'] = kwargs.pop( 'scale', 5.0e5 );
    extent, scale = getMapExtentScale( ax, scale = kwargs['scale'] );

  log.debug('Setting axis extent')  
  ax.set_extent( extent, ax.projection );                           # Set axis extent
  log.debug('Adding coast line')  
  ax.add_feature(cfeature.COASTLINE.with_scale(resloution), linewidth=linewidth)
  log.debug('Adding states')  
  ax.add_feature(cfeature.STATES, linewidth=linewidth)
  log.debug('Adding borders')  
  ax.add_feature(cfeature.BORDERS, linewidth=linewidth)
  ax.outline_patch.set_visible(False);                                          # Remove frame from plot
  return ax

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
def add_colorbar( mappable, ticks, **kwargs ):
  '''
  Name:
    add_colorbar
  Purpose:
    A python function to add a colorbar to a plot
  Inputs:
    mappable  : The object to add color bar to; i.e., object returned
                 by a call to ax.contourf()
    ticks     : Ticks to draw on colorbar
  Ouputs:
    Returns a colorbar object
  Keywords:
    fontsize : Font size for color bar; Default is 8
    title    : Colorbar title; Default is None
  '''
  log = logging.getLogger(__name__);
  log.debug('Creating color bar')
  fontsize  = kwargs.pop('fontsize', 8);                                         # Pop off fontsize from keywords
  title     = kwargs.pop('title',    None);
  ax        = mappable.ax;                                                      # Get axis from the mappable
  txt       = ax.text(0.5, 0.5, 'X');                                           # Write a capital 'X' so that we can figure out how big text is on plot
  renderer  = ax.figure.canvas.get_renderer();                                  # Renderer of the object
  txt_bbox  = txt.get_window_extent( renderer = renderer );                     # Get bounding box of the text
  cbHeight  = txt_bbox.height / ax.figure.bbox.height;                          # Set cbHeight to height of the text in normalized coordinates
  txt.remove( );                                                                # Remove the text from the image

  ax_x0, ax_y0, ax_w, ax_h = ax._position.bounds;                               # Get size of axes relative to figure size
  ax_w  /=  4.0;                                                                # Divide axis width by 4
  rect   = (ax_x0, ax_y0-2.0*cbHeight, ax_w, cbHeight)
  cb_ax  = ax.figure.add_axes( rect, label = uuid.uuid4() );                    # Add axis for the color bar
  cbar   = plt.colorbar(mappable, cax=cb_ax, ticks=ticks, **opts['colorbar']);  # Generate the colorbar
  cbar.ax.xaxis.set_ticks_position('top');                                      # Place labels on top of color bar
  x_ticks = cbar.ax.get_xticklabels();                                          # Get x-axis tick labels of color bar
  y_ticks = cbar.ax.get_yticklabels();                                          # Get y-axis tick labels of color bar
  cbar.ax.set_xticklabels(x_ticks, fontsize=fontsize);                          # Set fontsize for colorbar x-axis labels
  cbar.ax.set_yticklabels(y_ticks, fontsize=fontsize);                          # Set fontsize for colorbar y-axis labels

  if title: cbar.set_label(title, size=fontsize)                                # Set colorbar title IF there was a title defined

  return cbar;                                                                  # Return the colorbar object

################################################################################
def plot_barbs( ax, xx, yy, u, v ):
  '''
  Name:
    plot_barbs
  Purpose:
    A python funciton to plot wind barbs on a GeoAxes map. Will plot
    barbs roughly every 2 degrees
  Inputs:
    ax     : GeoAxes to plot wind barbs on
    xx     : x-values (in map coordinates) of where to plot barbs
    yy     : y-values (in map coordinates) of where to plot barbs
    u      : u-wind values; Must be pint Quantity
    v      : v-wind values; Must be pint Quantity
  Keywords:
    None.
  Outputs:
    None.
  '''
  log = logging.getLogger(__name__);                                            # Logger for the function
  log.debug( 'Computing skip for winds at 2 degree spacing' )
  diff, skip = 0, 0;                                                            # Initialize difference between x-values and skip
  while diff < 2.0e5:                                                           # While the difference is less than roughly 2 degrees
    skip += 1;                                                                  # Increment skip
    diff  = abs(xx[0,skip] - xx[0,0]);                                          # Compute new difference
  log.debug( 'Skipping every {} values'.format(skip) )
  ax.barbs( xx[::skip,::skip], yy[::skip,::skip], 
            u.to('kts')[::skip,::skip].m, v.to('kts')[::skip,::skip].m, 
            **opts['barb_Opts']
  );                                                                            # Plot the barbs at the specified skip

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