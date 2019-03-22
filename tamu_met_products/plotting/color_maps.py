import numpy as np
from matplotlib.colors import ListedColormap, BoundaryNorm
from . import contour_levels;

def buildCMAP( inVar ):
  if isinstance( inVar['rgb'], list):                                           # If rgb tag is a list instance
    inVar['rgb']  = np.array( inVar['rgb'] ).transpose() / 255.0;               # Convert to numpy array, transpose, and divide by 255
  inVar['cmap'] = ListedColormap( inVar['rgb'][1:-1,:] );                       # Initialize color map; first and last points in the rgb values are under/over colors
  inVar['cmap'].set_under( inVar['rgb'][ 0,:] );                                # Set colorbar under color
  inVar['cmap'].set_over(  inVar['rgb'][-1,:] );                                # Set colorbar over color
  inVar['norm'] = BoundaryNorm( inVar['lvls'], inVar['cmap'].N );               # Set colorbar labels?
  return inVar

# precip
precip = {
  'rgb' : [ [255, 127,   0,   0,  16,  30,   0,   0, 137, 145, 139, 139, 205, 238, 255, 205],
            [255, 255, 205, 139,  78, 144, 178, 238, 104,  44,   0,   0,   0,  64, 127, 133],
            [255,   0,   0,   0, 139, 255, 238, 238, 205, 238, 139,   0,   0,   0,   0,   0] ],
  'lvls' : contour_levels.precip
}
precip = buildCMAP( precip )

# 500 hPa vorticity
vort_500 = {
  'rgb' : [ [123, 144,  41,  41, 255, 255, 255, 255, 253, 253, 235, 203, 137],
            [ 17,  57, 147, 237, 255, 255, 255, 253, 164, 127,  47,   8,  17],
            [137, 234, 251, 237, 255, 255, 255,  56,  88,  35,  52,  20, 137] ],
  'lvls' : contour_levels.vorticity['500']
}
vort_500 = buildCMAP( vort_500 )

# 250 hPa winds
wind_250 = {
  'rgb'  : [ [255, 255, 253, 253, 235, 203, 137],
             [255, 253, 164, 127,  47,   8,  17],
             [255,  56,  88,  35,  52,  20, 137] ],
  'lvls' : contour_levels.winds['250']
}
wind_250 = buildCMAP( wind_250 )


# 850 hPa temps
temp_850 = {
  'rgb'  : [ [ 11,  30,  41,  31, 132, 255, 253, 253, 252, 137, 144, 137],
             [ 36, 179, 237, 203, 253, 253, 164, 127,  13,   3,  57,  17],
             [251, 235, 237,  35,  49,  56,  88,  35,  27,   9, 234, 137] ],
  'lvls' : contour_levels.temperature['850']
}
temp_850 = buildCMAP( temp_850 )

# 850 hPa temps
temp_2m = {
  'rgb'  : [ [  0,  11,  30,  41,  31, 132, 255, 253, 253, 252, 137, 137, 144, 137],
             [  9,  36, 179, 237, 203, 253, 253, 164, 127,  13,   3, 104,  57,  17],
             [255, 251, 235, 237,  35,  49,  56,  88,  35,  27,   9, 205, 234, 137] ],
  'lvls' : contour_levels.temperature['2m']
}
temp_2m = buildCMAP( temp_2m )


# Surface plot
surface = {
  'rgb'  : [ [255, 131,  41,  31,  17],
             [255, 253, 252, 203, 137],
             [255,  49,  46,  35,  20] ],
  'lvls' : contour_levels.humidity['700']
}
surface = buildCMAP( surface )

theta_e_1000 = {
  'rgb'  : temp_850['rgb'][:-1,:],
  'lvls' : contour_levels.theta_e['1000']
}
theta_e_1000 = buildCMAP( theta_e_1000 )
