NAM40 = {
    'model_name' : 'NAM40',
    'model_vars' : {
        'winds'  : {'parameters' : ['uW', 'vW'],
                    'levels'     : ['10.0FHAG', '1000.0MB', '850.0MB', '500.0MB', '250.0MB']},
        'temp'   : {'parameters' : ['T'], 
                    'levels'     : ['2.0FHAG', '1000.0MB', '850.0MB']},
        'dew'    : {'parameters' : ['DpT'], 
                    'levels'     : ['1000.0MB']},
        'geoH'   : {'parameters' : ['GH'],
                    'levels'     : ['1000.0MB', '850.0MB', '500.0MB', '250.0MB']},
        'MSLP'   : {'parameters' : ['PMSL'],
                    'levels'     : ['0.0MSL']},
        'RH'     : {'parameters' : ['RH'],
                    'levels'     : ['1000.0MB', '700.0MB']},
        'precip' : {'parameters' : ['TP6hr'],
                    'levels'     : ['0.0SFC']},
    },
    'mdl2stnd' : {
        'uW'    : 'u_wind',
        'vW'    : 'v_wind',
        'DpT'   : 'temp_dew',
        'T'     : 'temp',
        'GH'    : 'geo_hght',
        'PMSL'  : 'mslp',
        'RH'    : 'rh',
        'TP6hr' : 'precip'
    }
}