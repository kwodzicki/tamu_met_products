import logging

LOG = logging.getLogger(__name__)
LOG.setLevel( logging.DEBUG )

STREAMHANDLER = logging.StreamHandler()
STREAMHANDLER.setFormatter(
  logging.Formatter( 
    '%(asctime)s [%(levelname)-8.8s] %(name)s.%(funcName)-15.15s - %(message)s',
    '%Y-%m-%d %H:%M:%S'
  )
)
STREAMHANDLER.setLevel( logging.WARNING )

LOG.addHandler( STREAMHANDLER )

