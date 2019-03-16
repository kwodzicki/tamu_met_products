import logging;
import os, json;
import matplotlib.pyplot as plt
import cartopy.crs as ccrs;

from .plot_utils                     import xy_transform;
from .plot_srfc_rh_mslp_thick        import plot_srfc_rh_mslp_thick
from .plot_850hPa_temp_hght_barbs    import plot_850hPa_temp_hght_barbs;
from .plot_500hPa_vort_hght_barbs    import plot_500hPa_vort_hght_barbs
from .plot_250hPa_isotach_hght_barbs import plot_250hPa_isotach_hght_barbs


dir = os.path.dirname( os.path.realpath(__file__) );
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
  map_projection    = kwargs.pop('map_projection', None)
  if map_projection is None:
    central_longitude = kwargs.pop('central_longitude', -100.0)
    central_latitude  = kwargs.pop('central_latitude',    40.0)
    map_projection    = ccrs.LambertConformal(
                           central_longitude = central_longitude, 
                           central_latitude  = central_latitude);               # Projection of the figure
  
  log.debug('Setting up 4-panel plot')
  # Create the figure and plot background on different axes
  fig, axarr = plt.subplots(nrows=2, ncols=2, figsize=(16, 9), 
                            subplot_kw={'projection': map_projection});
  plt.subplots_adjust( **opts['subplot_adjust'] );                              # Set up subplot margins
  
  axlist = axarr.flatten()
  
  transform = kwargs.pop('transform', None)
  if transform is not None:
    data['lon'], data['lat'] = xy_transform(
      map_projection, transform, data['lon'], data['lat']
    );                                                                          # Transform the data; saves some time

  plot_500hPa_vort_hght_barbs( 
    axlist[0], data['lon'], data['lat'],
    data['abs_vor 500.0MB'], data['geo_hght 500.0MB'], 
    data['model'], initTime, fcstTime, 
    u = data['u_wind 500.0MB'], 
    v = data['v_wind 500.0MB'] 
  )

  plot_250hPa_isotach_hght_barbs(
    axlist[1], data['lon'], data['lat'],
    data['u_wind 250.0MB'],  data['v_wind 250.0MB'], data['geo_hght 250.0MB'],
    data['model'], initTime, fcstTime, 
  )

  plot_850hPa_temp_hght_barbs(
    axlist[2], data['lon'], data['lat'],
    data['temp 850.0MB'], data['geo_hght 850.0MB'], 
    data['model'], initTime, fcstTime, 
    u = data['u_wind 850.0MB'], 
    v = data['v_wind 850.0MB']
  )
  
  plot_srfc_rh_mslp_thick(
    axlist[3], data['lon'], data['lat'],
    data['rh 700.0MB'], data['mslp 0.0MSL'], 
    data['geo_hght 1000.0MB'], data['geo_hght 500.0MB'],
    data['model'], initTime, fcstTime, 
  )

  return fig;
