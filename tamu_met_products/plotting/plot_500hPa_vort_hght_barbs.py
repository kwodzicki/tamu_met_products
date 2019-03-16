import logging;
import os, json;
import cartopy.crs as ccrs;
from .plot_utils import add_colorbar, plot_barbs, plot_basemap, baseLabel, xy_transform;
from . import color_maps;

dir = os.path.dirname( os.path.realpath(__file__) );
with open( os.path.join( dir, 'plot_opts.json' ), 'r' ) as fid:
  opts = json.load(fid);

################################################################################
def plot_500hPa_vort_hght_barbs( ax, xx, yy, vort, hght, model, initTime, fcstTime, u=None, v=None, **kwargs ):
  '''
  Name:
    plot_500hPa_vort_hght_barbs
  Purpose:
    A python function to plot a 500 hPa plot like the one in the
    upper left of the HDWX 4-panel plot
  Inputs:
    ax       : A GeoAxes object for axes to plot data on
    xx       : x-values for plot
    yy       : y-values for plot
    vort     : Vorticity at 500 hPa to plot
    hght     : Geopotential heights at 500 hPa to plot
    model    : Name of the model being plotted
    initTime : Initialization time of the model run
    fcstTime : Forecast time of the model run
  Keywords:
    u : u-wind components for wind barbs
    v : v-wind components for wind barbs
    All keywords accecpted by plotting methods
  Outputs:
    Returns the filled contour, contour, and colorbar objects
  '''
  log = logging.getLogger(__name__)
  log.info('Creating 500 hPa plot')

  transform = kwargs.pop( 'transform', None );                                  # Get transformation for x- and y-values
  if transform is not None:                                                     # If transform is not None, then we must transform the points for plotting
    xx, yy = xy_transform( ax.projection, transform, xx, yy )

  ax, scale = plot_basemap(ax, **kwargs);                                       # Set up the basemap, get updated axis and map scale

  log.debug('Plotting vorticity') 
  if vort.max().m < 1.0: vort *= 1.0e5;                                         # If vorticity values too small, scale them
  cf = ax.contourf(xx, yy, vort, 
                         cmap      = color_maps.vort_500['cmap'], 
                         norm      = color_maps.vort_500['norm'],
                         levels    = color_maps.vort_500['lvls'],
                         **opts['contourf_Opts'])

  plot_barbs( ax, scale, xx, yy, u, v );                                        # Plot wind barbs
    
  log.debug('Plotting geopotential height')
  c = ax.contour(xx, yy, hght, **opts['contour_Opts']);                         # Contour the geopotential height
  ax.clabel(c, **opts['clabel_Opts']);                                          # Change contour label settings
  cbar = add_colorbar( cf, ax, color_maps.vort_500['lvls'], **kwargs )          # Add a color bar
  
  txt = baseLabel( model, initTime, fcstTime );                                 # Get base string for label
  txt.append('500-hPa HEIGHTS, WINDS, ABS VORT');                               # Update Label 
  t = ax.text(0.5, 0, '\n'.join( txt ),
                 verticalalignment   = 'top', 
                 horizontalalignment = 'center',
                 transform           = ax.transAxes);                           # Add label to axes

  return cf, c, cbar