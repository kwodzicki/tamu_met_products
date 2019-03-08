import logging;
import matplotlib.pyplot as plt
import cartopy.crs as ccrs;

from .plot_srfc_rh_mslp_thick        import plot_srfc_rh_mslp_thick
from .plot_850hPa_temp_hght_barbs    import plot_850hPa_temp_hght_barbs;
from .plot_500hPa_vort_hght_barbs    import plot_500hPa_vort_hght_barbs
from .plot_250hPa_isotach_hght_barbs import plot_250hPa_isotach_hght_barbs


################################################################################
def forecast_4_panel( data, initTime, fcstTime, cent_lon = -100.0, cent_lat = 40.0):
  '''
  Name:
    forecast_4_panel
  Purpose:
    A python function to create a plot like the one in the
    HDWX 4-panel plot
  Inputs:
    data : A dictionary (should be xarray in future?) with all variables
            required for the plots. Must set up a convention in the future
  Keywords:
    None.
  Outputs:
    Returns the filled contour, contour, and colorbar objects
  '''
  log = logging.getLogger(__name__);
  log.debug('Plotting 4-panel forecast map')
  map_proj  = ccrs.LambertConformal(central_longitude = cent_lon, 
                                    central_latitude  = cent_lat)
  
  log.debug('Setting up 4-panel plot')
  # Create the figure and plot background on different axes
  fig, axarr = plt.subplots(nrows=2, ncols=2, figsize=(16, 9), 
                            subplot_kw={'projection': map_proj});
  plt.subplots_adjust(
    left   = 0.005, 
    bottom = 0.050, 
    right  = 0.995, 
    top    = 1.000, 
    wspace = 0.050, 
    hspace = 0.125
  )
  
  axlist = axarr.flatten()

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
