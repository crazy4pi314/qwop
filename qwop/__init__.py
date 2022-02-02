from .exporters import *
from .visualization import *

try:
    import sys
    if sys.version_info >= (3, 8):
        from importlib import metadata
        __version__ = metadata.version('qwop')
        del metadata
    else:
        import pkg_resources
        __version__ = pkg_resources.get_distribution('qwop').version
        del pkg_resources
    del sys
except:
    __version__ = "<unknown>"
