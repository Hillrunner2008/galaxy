"""
Qualityscore class
"""

import data
import logging
from galaxy.datatypes.sniff import *
from galaxy import util

log = logging.getLogger(__name__)

class QualityScore ( data.Text ):
    """
    until we know more about quality score formats
    """
    file_ext = "qual"
    
    def set_peek( self, dataset, line_count=None ):
        if not dataset.dataset.purged:
            dataset.peek = data.get_file_peek( dataset.file_name )
            if line_count is None:
                dataset.blurb = data.nice_size( dataset.get_size() )
            else:
                dataset.blurb = "%s lines, Quality score file" % util.commaify( str( line_count ) )
        else:
            dataset.peek = 'file does not exist'
            dataset.blurb = 'file purged from disk'
    
    def display_peek(self, dataset):
        try:
            return dataset.peek
        except:
            return "Quality score file (%s)" % ( data.nice_size( dataset.get_size() ) )


      