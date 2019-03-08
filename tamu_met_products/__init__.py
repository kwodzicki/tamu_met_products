import logging
log = logging.getLogger(__name__)
srm = logging.StreamHandler()
srm.setLevel( logging.DEBUG )
log.setLevel( logging.DEBUG )
log.addHandler( srm )