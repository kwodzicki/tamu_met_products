import numpy as np
from matplotlib.colors import ListedColormap, BoundaryNorm
from . import contour_levels;

def buildCMAP( inVar ):
  inVar['rgb']  = np.array( inVar['rgb'] ).transpose() / 255.0;
  inVar['cmap'] = ListedColormap( inVar['rgb'][1:-1,:] )
  inVar['cmap'].set_under( inVar['rgb'][ 0,:] )
  inVar['cmap'].set_over(  inVar['rgb'][-1,:] )
  inVar['norm'] = BoundaryNorm( inVar['lvls'], inVar['cmap'].N );
  return inVar

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

# Surface plot
surface = {
  'rgb'  : [ [255, 131,  41,  31,  17],
             [255, 253, 252, 203, 137],
             [255,  49,  46,  35,  20] ],
  'lvls' : contour_levels.humidity['700']
}
surface = buildCMAP( surface )