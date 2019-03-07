import numpy as np
from matplotlib.colors import ListedColormap, BoundaryNorm

# 500 hPa vorticity
rgb  = [ [123, 144,  41,  41, 255, 255, 255, 255, 253, 253, 235, 203, 137],
         [ 17,  57, 147, 237, 255, 255, 255, 253, 164, 127,  47,   8,  17],
         [137, 234, 251, 237, 255, 255, 255,  56,  88,  35,  52,  20, 137]]
rgb  = np.array( rgb ).transpose() / 255.0;
bds  = np.arange(-9, 25, 3);
cmap = ListedColormap( rgb[1:-1,:] )
cmap.set_under( rgb[ 0,:] )
cmap.set_over(  rgb[-1,:] )
vort_500 = {
  'cmap' : cmap,
  'norm' : BoundaryNorm(bds, cmap.N),
  'lvls' : bds
}

# 250 hPa winds
rgb  = [ [255, 255, 253, 253, 235, 203, 137],
         [255, 253, 164, 127,  47,   8,  17],
         [255,  56,  88,  35,  52,  20, 137]]
rgb  = np.array( rgb ).transpose() / 255.0;
bds  = np.arange(70, 171, 20);
cmap = ListedColormap( rgb[1:-1,:] )
cmap.set_under( rgb[ 0,:] )
cmap.set_over(  rgb[-1,:] )
wind_250 = {
  'cmap' : cmap,
  'norm' : BoundaryNorm(bds, cmap.N),
  'lvls' : bds
}

# 850 hPa temps
rgb  = [ [ 11,  30,  41,  31, 132, 255, 253, 253, 252, 137, 144, 137],
         [ 36, 179, 237, 203, 253, 253, 164, 127,  13,   3,  57,  17],
         [251, 235, 237,  35,  49,  56,  88,  35,  27,   9, 234, 137]]
rgb  = np.array( rgb ).transpose() / 255.0;
bds  = np.arange(-20, 31, 5);
cmap = ListedColormap( rgb[1:-1,:] )
cmap.set_under( rgb[ 0,:] )
cmap.set_over(  rgb[-1,:] )
temp_850 = {
  'cmap' : cmap,
  'norm' : BoundaryNorm(bds, cmap.N),
  'lvls' : bds
}