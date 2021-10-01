import numpy as np
from matplotlib.colors import ListedColormap, BoundaryNorm
from . import contour_levels;

def buildCMAP( inVar ):
  if 'rgb' not in inVar:
    for val in inVar.values():
      return buildCMAP( val )

  if isinstance( inVar['rgb'], list):                                           # If rgb tag is a list instance
    inVar['rgb']  = np.array( inVar['rgb'] ).transpose() / 255.0;               # Convert to numpy array, transpose, and divide by 255
  inVar['cmap'] = ListedColormap( inVar['rgb'][1:-1,:] );                       # Initialize color map; first and last points in the rgb values are under/over colors
  inVar['cmap'].set_under( inVar['rgb'][ 0,:] );                                # Set colorbar under color
  inVar['cmap'].set_over(  inVar['rgb'][-1,:] );                                # Set colorbar over color
  inVar['norm'] = BoundaryNorm( inVar['levels'], inVar['cmap'].N );               # Set colorbar labels?

  return inVar

def popRGB( *args ):
  for arg in args:
    if arg.pop('rgb', None) is None:
      for val in arg.values():
        popRGB( val )

# precip
precip = {
  'rgb'    : [ [255, 127,   0,   0,  16,  30,   0,   0, 137, 145, 139, 139, 205, 238, 255, 205],
               [255, 255, 205, 139,  78, 144, 178, 238, 104,  44,   0,   0,   0,  64, 127, 133],
               [255,   0,   0,   0, 139, 255, 238, 238, 205, 238, 139,   0,   0,   0,   0,   0] ],
  'levels' : contour_levels.precip
}

# 500 hPa vorticity
vorticity = {
  '500.0MB' : {
    'rgb'    : [ [123, 144,  41,  41, 255, 255, 255, 255, 253, 253, 235, 203, 137],
                 [ 17,  57, 147, 237, 255, 255, 255, 253, 164, 127,  47,   8,  17],
                 [137, 234, 251, 237, 255, 255, 255,  56,  88,  35,  52,  20, 137] ],
    'levels' : contour_levels.vorticity['500.0MB']
  }
}
for val in vorticity.values(): val = buildCMAP( val )


# 250 hPa winds
winds = {
  '250.0MB' : {
    'rgb'    : [ [255, 255, 253, 253, 235, 203, 137],
                 [255, 253, 164, 127,  47,   8,  17],
                 [255,  56,  88,  35,  52,  20, 137] ],
    'levels' : contour_levels.winds['250.0MB']
  }
}
for val in winds.values(): val = buildCMAP( val )

# 850 hPa temps
temperature = {
  '2.0FHAG' : {
    'rgb'    : [ [  0,  11,  30,  41,  31, 132, 255, 253, 253, 252, 137, 137, 144, 137],
                 [  9,  36, 179, 237, 203, 253, 253, 164, 127,  13,   3, 104,  57,  17],
                 [255, 251, 235, 237,  35,  49,  56,  88,  35,  27,   9, 205, 234, 137] ],
    'levels' : contour_levels.temperature['2.0FHAG']
  },
  '850.0MB' : {
    'rgb'    : [ [ 11,  30,  41,  31, 132, 255, 253, 253, 252, 137, 144, 137],
                 [ 36, 179, 237, 203, 253, 253, 164, 127,  13,   3,  57,  17],
                 [251, 235, 237,  35,  49,  56,  88,  35,  27,   9, 234, 137] ],
    'levels' : contour_levels.temperature['850.0MB']
  }
}
for val in temperature.values(): val = buildCMAP( val )

# Surface plot
surface = {
  'rgb'    : [ [255, 131,  41,  31,  17],
               [255, 253, 252, 203, 137],
               [255,  49,  46,  35,  20] ],
  'levels' : contour_levels.humidity['700.0MB']
}
surface = buildCMAP( surface )

theta_e = {
  '1000.0MB' : {
    'rgb'    : temperature['850.0MB']['rgb'][:-1,:],
    'levels' : contour_levels.theta_e['1000.0MB']
  }
}
for val in theta_e.values(): val = buildCMAP( val )

popRGB( precip, vorticity, winds, temperature, surface, theta_e ) 
