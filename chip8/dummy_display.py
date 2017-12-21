import logging

LOG = logging.getLogger(__name__)


class DummyDisplay(object):
    """Dummy display"""

    def clear(self):
        LOG.debug("Clearing display")
