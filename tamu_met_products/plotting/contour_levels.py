import numpy as np;

mslp         = np.arange(-25, 26) * 4 + 1016;              # contour levels for mean sea level pressure

# 1000-500 hPa hickness settings
thickness = {
  'levels' : np.arange(-25, 26)
}
thickness['linewidths'] = (thickness['levels'] == 0)*2 + 1;
thickness['linestyles'] = np.full(thickness['levels'].size, 'dashed')
thickness['linestyles'][thickness['levels'] == 0] = 'solid'
thickness['colors']     = np.full( thickness['levels'].size, 'r')
thickness['colors'][thickness['levels'] < 0] = 'b';
thickness['levels']     = thickness['levels'] * 40 + 5500

# Relative humdity; in percent
humidity = {
  '700' : np.arange(  60,   91,  10)
}

precip = np.array([0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 1.0, 
                   1.50, 2.00, 2.5, 3.00, 3.5, 4.00, 4.5, 5.0])
# Temperatures at 850 hPa
temperature = {
  '2m'  : np.arange(  20,   81,   5),
  '850' : np.arange( -20,   31,   5)
}

# Vorticity; don't forget to scale by 10^5
vorticity = {
  '500' : np.arange(  -9,   25,   3)
}

# Winds
winds = {
  '250' : np.arange(  70,  171,  20)
}

theta_e = {
  '1000' : np.arange( 280, 371, 10 ) 
}

#Heights 
heights = {
  '850' : np.arange( -25, 26 ) *  30 + 1500,
  '700' : np.arange( -25, 26 ) *  30 + 3000,
  '500' : np.arange( -25, 26 ) *  60 + 5400,
  '300' : np.arange( -25, 26 ) * 120 + 9000,
  '250' : np.arange( -25, 26 ) * 120 + 9000
}
