import logging;
import os, json;
import matplotlib.pyplot as plt
import cartopy.crs as ccrs;

from .plot_utils import initFigure, xy_transform, getMapExtentScale;
from .model_plots import (
  plot_srfc_rh_mslp_thick,
  plot_850hPa_temp_hght_barbs,
  plot_500hPa_vort_hght_barbs,
  plot_250hPa_isotach_hght_barbs
)


dir = os.path.dirname( os.path.dirname(__file__) );
with open( os.path.join( dir, 'plot_opts.json' ), 'r' ) as fid:
  opts = json.load(fid);

################################################################################
def forecast_4_panel( data, initTime, fcstTime, **kwargs):
  '''
  Name:
    forecast_4_panel
  Purpose:
    A python function to create a plot like the one in the
    HDWX 4-panel plot
  Inputs:
    data : A dictionary (should be xarray in future?) with all variables
            required for the plots. Must set up a convention in the future
    initTime : A datetime object with the model initialize time
    fcstTime : A datetime object with the model forecast time
  Keywords:
    None.
  Outputs:
    Returns the filled contour, contour, and colorbar objects
  '''
  log = logging.getLogger(__name__);
  log.debug('Plotting 4-panel forecast map')
  
  log.debug('Setting up 4-panel plot')
  # Create the figure and plot background on different axes
  fig, ax = initFigure(2, 2, **kwargs );
  plt.subplots_adjust( **opts['subplot_adjust'] );                              # Set up subplot margins
  
  ax = ax.flatten()
  
  transform = kwargs.pop('transform', None)
  if transform is not None:
    data['lon'], data['lat'] = xy_transform(
      map_projection, transform, data['lon'], data['lat']
    );                                                                          # Transform the data; saves some time

  extent, scale = getMapExtentScale( ax[0], data['lon'], data['lat'] )
  plot_500hPa_vort_hght_barbs( 
    ax[0], data['lon'], data['lat'],
    data['abs_vor 500.0MB'], data['geo_hght 500.0MB'], 
    data['model'], initTime, fcstTime, 
    u      = data['u_wind 500.0MB'], 
    v      = data['v_wind 500.0MB'],
    extent = extent
  )

  plot_250hPa_isotach_hght_barbs(
    ax[1], data['lon'], data['lat'],
    data['u_wind 250.0MB'],  data['v_wind 250.0MB'], data['geo_hght 250.0MB'],
    data['model'], initTime, fcstTime,
    extent = extent
  )

  plot_850hPa_temp_hght_barbs(
    ax[2], data['lon'], data['lat'],
    data['temp 850.0MB'], data['geo_hght 850.0MB'], 
    data['model'], initTime, fcstTime, 
    u      = data['u_wind 850.0MB'], 
    v      = data['v_wind 850.0MB'],
    extent = extent
  )
  
  plot_srfc_rh_mslp_thick(
    ax[3], data['lon'], data['lat'],
    data['rh 700.0MB'], data['mslp 0.0MSL'], 
    data['geo_hght 1000.0MB'], data['geo_hght 500.0MB'],
    data['model'], initTime, fcstTime,
    extent = extent
  )

  return fig;
