# tamu_met_products

**tamu_met_products** Python package provides utilities for creating forecasting
products for 

## Main features

* Compatible with Python3.6+

## Installation

Whenever it's possible, please always use the latest version from the repository.
To install it using `pip`:

    pip install git+https://github.com/kms22134/tamu_met_products

## Dependencies


## Included modules

#### data_backends
  - awips_model_utils.py
    
    Contains functions to download model data using python-awips DataAccessLayer.
    Some notes on how times and levels work in awips follow, as their
    documentation is a little lacking.
    
    - Times

      A large variety of times exists in terms of valid periods. I found it is
      key to check the valid period duration (seconds) to determine the types
      of data that will be available given the time; 6 hr accumulated precip
      will only be available for time periods of 6 hours. To check the duration,
      run the following

            time.getValidPeriod().duration()

      which will return a time in seconds.

    - Levels

      To the the short form of the units (i.e. MB or SFC), one needs to access
      the .masterLevel.name attribute of the class.

      It is also good to check the `.levelonevalue` and `.leveltwovalue`. If the
      level class represents a layer, `.leveltwovalue` will be -999999.0; a
      check for `< 0` will work nicely.


## License

tamu_met_products is released under the terms of the GNU GPL v3 license.