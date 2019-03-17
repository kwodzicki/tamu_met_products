import logging
log = logging.getLogger(__name__)
srm = logging.StreamHandler()
srm.setFormatter(
  logging.Formatter( 
    '%(levelname)-.4s - %(asctime)s - %(name)s.%(funcName)-15.15s - %(message)s',
    '%Y-%m-%d %H:%M:%S'
  )
)

srm.setLevel( logging.INFO )
log.setLevel( logging.DEBUG )
log.addHandler( srm )