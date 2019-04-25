# stnd_levels = [1000, 925, 850, 700, 500, 400, 300, 250, 200, 150, 100, 70, 50, 10]
stnd_levels = [1000, 850, 500, 250]
stnd_levels = ['{:.1f}MB'.format(i) for i in stnd_levels]

NAM40 = {
    'model_name' : 'NAM40',
    'model_vars' : {
        'wind'          : {'parameters' : ['uW', 'vW'],
                           'levels'     : ['10.0FHAG'] + stnd_levels},
        'temperature'   : {'parameters' : ['T'], 
                           'levels'     : ['2.0FHAG'] + stnd_levels},
        'dewpoint'      : {'parameters' : ['DpT'], 
                           'levels'     : stnd_levels},
        'geopotential'  : {'parameters' : ['GH'],
                           'levels'     : ['1000.0MB', '850.0MB', '500.0MB', '250.0MB']},
        'MSLP'          : {'parameters' : ['PMSL'],
                           'levels'     : ['0.0MSL']},
        'RH'            : {'parameters' : ['RH'],
                           'levels'     : ['1000.0MB', '700.0MB']},
        'precip'        : {'parameters' : ['TP6hr'],
                           'levels'     : ['0.0SFC']},
    },
    'mdl2stnd' : {
        'uW'    : 'u wind',
        'vW'    : 'v wind',
        'DpT'   : 'dewpoint',
        'T'     : 'temperature',
        'GH'    : 'geopotential height',
        'PMSL'  : 'mslp',
        'RH'    : 'rh',
        'TP6hr' : 'precip'
    }
}


GFS = {
    'model_name' : 'GFS',
    'map_scale'  : 2.0e5,
    'model_vars' : {
        'wind'          : {'parameters' : ['uW', 'vW'],
                           'levels'     : ['10.0FHAG'] + stnd_levels},
        'temperature'   : {'parameters' : ['T'], 
                           'levels'     : ['2.0FHAG'] + stnd_levels},
        'dewpoint'      : {'parameters' : ['DpT'], 
                           'levels'     : stnd_levels},
        'geopotential'  : {'parameters' : ['GH'],
                           'levels'     : ['1000.0MB', '850.0MB', '500.0MB', '250.0MB']},
        'MSLP'          : {'parameters' : ['PMSL'],
                           'levels'     : ['0.0MSL']},
        'RH'            : {'parameters' : ['RH'],
                           'levels'     : ['1000.0MB', '700.0MB']},
        'precip'        : {'parameters' : ['TP6hr'],
                           'levels'     : ['0.0SFC']},
    },
    'mdl2stnd' : {
        'uW'    : 'u wind',
        'vW'    : 'v wind',
        'DpT'   : 'dewpoint',
        'T'     : 'temperature',
        'GH'    : 'geopotential height',
        'PMSL'  : 'mslp',
        'RH'    : 'rh',
        'TP6hr' : 'precip'
    }
}