NAM40 = {
    'model_name' : 'NAM40',
    'model_vars' : {
        'winds' : {'parameters' : ['uW', 'vW'],
                   'levels'     : ['850.0MB', '500.0MB', '250.0MB']},
        'temp'  : {'parameters' : ['T'], 
                   'levels'     : ['850.0MB']},
        'geoH'  : {'parameters' : ['GH'],
                   'levels'     : ['1000.0MB', '850.0MB', '500.0MB', '250.0MB']},
        'MSLP'  : {'parameters' : ['PMSL'],
                   'levels'     : ['0.0MSL']},
        'RH'    : {'parameters' : ['RH'],
                   'levels'     : ['700.0MB']}
    },
    'mdl2stnd' : {
        'uW'   : 'u_wind',
        'vW'   : 'v_wind',
        'T'    : 'temp',
        'GH'   : 'geo_hght',
        'PMSL' : 'mslp',
        'RH'   : 'rh'
    }
}