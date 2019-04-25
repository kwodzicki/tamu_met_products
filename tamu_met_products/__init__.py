import logging
log = logging.getLogger(__name__)
srm = logging.StreamHandler()
srm.setFormatter(
  logging.Formatter( 
    '%(asctime)s %(levelname)s %(name)s.%(funcName)-15.15s - %(message)s',
    '%Y-%m-%d %H:%M:%S'
  )
)

srm.setLevel( logging.DEBUG )
log.setLevel( logging.DEBUG )
log.addHandler( srm )