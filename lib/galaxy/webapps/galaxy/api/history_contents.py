"""
API operations on the contents of a history.
"""

from galaxy import exceptions
from galaxy import util
from galaxy import web

from galaxy.web import _future_expose_api as expose_api
from galaxy.web import _future_expose_api_anonymous as expose_api_anonymous
from galaxy.web import _future_expose_api_raw as expose_api_raw

from galaxy.web.base.controller import BaseAPIController
from galaxy.web.base.controller import UsesHistoryDatasetAssociationMixin
from galaxy.web.base.controller import UsesHistoryMixin
from galaxy.web.base.controller import UsesLibraryMixin
from galaxy.web.base.controller import UsesLibraryMixinItems
from galaxy.web.base.controller import UsesTagsMixin

from galaxy.web.base.controller import url_for
from galaxy.util.sanitize_html import sanitize_html

from galaxy.webapps.galaxy.api import histories

import logging
log = logging.getLogger( __name__ )


class HistoryContentsController( BaseAPIController, UsesHistoryDatasetAssociationMixin, UsesHistoryMixin,
                                 UsesLibraryMixin, UsesLibraryMixinItems, UsesTagsMixin ):

    def __init__( self, app ):
        super( HistoryContentsController, self ).__init__( app )
        self.mgrs = util.bunch.Bunch(
            histories = histories.HistoryManager(),
            hdas = HDAManager()
        )

    def _decode_id( self, trans, id ):
        try:
            return trans.security.decode_id( id )
        except:
            raise exceptions.MalformedId( "Malformed History id ( %s ) specified, unable to decode"
                                          % ( str( id ) ), type='error' )

    @expose_api_anonymous
    def index( self, trans, history_id, ids=None, **kwd ):
        """
        index( self, trans, history_id, ids=None, **kwd )
        * GET /api/histories/{history_id}/contents
            return a list of HDA data for the history with the given ``id``
        .. note:: Anonymous users are allowed to get their current history contents

        If Ids is not given, index returns a list of *summary* objects for
        every HDA associated with the given `history_id`.

        If ids is given, index returns a *more complete* json object for each
        HDA in the ids list.

        :type   history_id: str
        :param  history_id: encoded id string of the HDA's History
        :type   ids:        str
        :param  ids:        (optional) a comma separated list of encoded `HDA` ids
        :param  types:      (optional) kinds of contents to index (currently just
                            dataset, but dataset_collection will be added shortly).
        :type   types:      str

        :rtype:     list
        :returns:   dictionaries containing summary or detailed HDA information
        .. seealso::
            :func:`_summary_hda_dict` and
            :func:`galaxy.web.base.controller.UsesHistoryDatasetAssociationMixin.get_hda_dict`
        """
        rval = []

        # get the history, if anon user and requesting current history - allow it
        if( ( trans.user == None )
        and ( history_id == trans.security.encode_id( trans.history.id ) ) ):
            history = trans.history
        # otherwise, check permissions for the history first
        else:
            history = self.mgrs.histories.get( trans, self._decode_id( trans, history_id ),
                check_ownership=False, check_accessible=True )

        # Allow passing in type or types - for continuity rest of methods
        # take in type - but this one can be passed multiple types and
        # type=dataset,dataset_collection is a bit silly.
        types = kwd.get( 'type', kwd.get( 'types', None ) ) or []
        if types:
            types = util.listify(types)
        else:
            types = [ 'dataset' ]

        contents_kwds = {'types': types}
        if ids:
            ids = map( lambda id: trans.security.decode_id( id ), ids.split( ',' ) )
            contents_kwds[ 'ids' ] = ids
            # If explicit ids given, always used detailed result.
            details = 'all'
        else:
            contents_kwds[ 'deleted' ] = kwd.get( 'deleted', None )
            contents_kwds[ 'visible' ] = kwd.get( 'visible', None )
            # details param allows a mixed set of summary and detailed hdas
            #TODO: this is getting convoluted due to backwards compat
            details = kwd.get( 'details', None ) or []
            if details and details != 'all':
                details = util.listify( details )

        for content in history.contents_iter( **contents_kwds ):
            if isinstance(content, trans.app.model.HistoryDatasetAssociation):
                encoded_content_id = trans.security.encode_id( content.id )
                detailed = details == 'all' or ( encoded_content_id in details )
                if detailed:
                    rval.append( self._detailed_hda_dict( trans, content ) )
                else:
                    rval.append( self._summary_hda_dict( trans, history_id, content ) )

        return rval

    #TODO: move to model or Mixin
    def _summary_hda_dict( self, trans, encoded_history_id, hda ):
        """
        Returns a dictionary based on the HDA in summary form::
            {
                'id'    : < the encoded dataset id >,
                'name'  : < currently only returns 'file' >,
                'type'  : < name of the dataset >,
                'url'   : < api url to retrieve this datasets full data >,
            }
        """
        api_type = "file"
        encoded_id = trans.security.encode_id( hda.id )
        return {
            'id'    : encoded_id,
            'history_id' : encoded_history_id,
            'name'  : hda.name,
            'type'  : api_type,
            'state'  : hda.state,
            'deleted': hda.deleted,
            'visible': hda.visible,
            'purged': hda.purged,
            'hid'   : hda.hid,
            'url'   : url_for( 'history_content', history_id=encoded_history_id, id=encoded_id, ),
        }

    def _detailed_hda_dict( self, trans, hda ):
        """
        Detailed dictionary of hda values.
        """
        try:
            hda_dict = self.get_hda_dict( trans, hda )
            hda_dict[ 'display_types' ] = self.get_old_display_applications( trans, hda )
            hda_dict[ 'display_apps' ] = self.get_display_apps( trans, hda )
            return hda_dict
        except Exception, exc:
            # catch error here - returning a briefer hda_dict with an error attribute
            log.exception( "Error in history API at listing contents with history %s, hda %s: (%s) %s",
                hda.history_id, hda.id, type( exc ), str( exc ) )
            return self.get_hda_dict_with_error( trans, hda=hda, error_msg=str( exc ) )

    @expose_api_anonymous
    def show( self, trans, id, history_id, **kwd ):
        """
        show( self, trans, id, history_id, **kwd )
        * GET /api/histories/{history_id}/contents/{id}
            return detailed information about an HDA within a history
        .. note:: Anonymous users are allowed to get their current history contents

        :type   id:         str
        :param  ids:        the encoded id of the HDA to return
        :type   history_id: str
        :param  history_id: encoded id string of the HDA's History

        :rtype:     dict
        :returns:   dictionary containing detailed HDA information
        .. seealso:: :func:`galaxy.web.base.controller.UsesHistoryDatasetAssociationMixin.get_hda_dict`
        """
        contents_type = kwd.get('type', 'dataset')
        if contents_type == 'dataset':
            return self.__show_dataset( trans, id, **kwd )
        else:
            return self.__handle_unknown_contents_type( trans, contents_type )

    def __show_dataset( self, trans, id, **kwd ):
        hda = self.mgrs.hdas.get( trans, self._decode_id( trans, id ), check_ownership=False, check_accessible=True )
        #if hda.history.id != self._decode_id( trans, history_id ):
        #    raise exceptions.ObjectNotFound( 'dataset was not found in this history' )
        hda_dict = self.get_hda_dict( trans, hda )
        hda_dict[ 'display_types' ] = self.get_old_display_applications( trans, hda )
        hda_dict[ 'display_apps' ] = self.get_display_apps( trans, hda )
        return hda_dict

    #TODO: allow anon users to copy hdas, ldas
    @expose_api
    def create( self, trans, history_id, payload, **kwd ):
        """
        create( self, trans, history_id, payload, **kwd )
        * POST /api/histories/{history_id}/contents
            create a new HDA by copying an accessible LibraryDataset

        :type   history_id: str
        :param  history_id: encoded id string of the new HDA's History
        :type   payload:    dict
        :param  payload:    dictionary structure containing::
            copy from library:
            'source'    = 'library'
            'content'   = [the encoded id from the library dataset]

            copy from HDA:
            'source'    = 'hda'
            'content'   = [the encoded id from the HDA]

        ..note:
            Currently, a user can only copy an HDA from a history that the user owns.

        :rtype:     dict
        :returns:   dictionary containing detailed information for the new HDA
        """
        #TODO: convert existing, accessible hda - model.DatasetInstance(or hda.datatype).get_converter_types
        history = self.mgrs.histories.get( trans, self._decode_id( trans, history_id ),
            check_ownership=True, check_accessible=False )

        type = payload.get('type', 'dataset')
        if type == 'dataset':
            return self.__create_dataset( trans, history, payload, **kwd )
        else:
            return self.__handle_unknown_contents_type( trans, type )

    def __create_dataset( self, trans, history, payload, **kwd ):
        source = payload.get( 'source', None )
        if source not in ( 'library', 'hda' ):
            raise exceptions.RequestParameterInvalidException(
                "'source' must be either 'library' or 'hda': %s" %( source ) )
        content = payload.get( 'content', None )
        if content is None:
            raise exceptions.RequestParameterMissingException( "'content' id of lda or hda is missing" )

        # copy from library dataset
        hda = None
        if source == 'library':
            ld = self.get_library_dataset( trans, content, check_ownership=False, check_accessible=False )
            #TODO: why would get_library_dataset NOT return a library dataset?
            if type( ld ) is not trans.app.model.LibraryDataset:
                raise exceptions.RequestParameterInvalidException(
                    "Library content id ( %s ) is not a dataset" % content )
            # insert into history
            hda = ld.library_dataset_dataset_association.to_history_dataset_association( history, add_to_history=True )

        # copy an existing, accessible hda
        elif source == 'hda':
            unencoded_hda_id = self._decode_id( trans, content )
            original = self.mgrs.hdas.get( trans, unencoded_hda_id, check_ownership=False, check_accessible=True )
            data_copy = original.copy( copy_children=True )
            hda = history.add_dataset( data_copy )

        trans.sa_session.flush()
        if not hda:
            return None
        #TODO: duplicate code - use a serializer with a view
        hda_dict = self.get_hda_dict( trans, hda )
        hda_dict[ 'display_types' ] = self.get_old_display_applications( trans, hda )
        hda_dict[ 'display_apps' ] = self.get_display_apps( trans, hda )
        return hda_dict

    @expose_api_anonymous
    def update( self, trans, history_id, id, payload, **kwd ):
        """
        update( self, trans, history_id, id, payload, **kwd )
        * PUT /api/histories/{history_id}/contents/{id}
            updates the values for the HDA with the given ``id``

        :type   history_id: str
        :param  history_id: encoded id string of the HDA's History
        :type   id:         str
        :param  id:         the encoded id of the history to undelete
        :type   payload:    dict
        :param  payload:    a dictionary containing any or all the
            fields in :func:`galaxy.model.HistoryDatasetAssociation.to_dict`
            and/or the following:

            * annotation: an annotation for the HDA

        :rtype:     dict
        :returns:   an error object if an error occurred or a dictionary containing
            any values that were different from the original and, therefore, updated
        """
        #TODO: PUT /api/histories/{encoded_history_id} payload = { rating: rating } (w/ no security checks)
        contents_type = kwd.get('type', 'dataset')
        if contents_type == "dataset":
            return self.__update_dataset( trans, history_id, id, payload, **kwd )
        else:
            return self.__handle_unknown_contents_type( trans, contents_type )

    def __update_dataset( self, trans, history_id, id, payload, **kwd ):
        changed = {}
        # anon user
        if trans.user == None:
            if history_id != trans.security.encode_id( trans.history.id ):
                raise exceptions.AuthenticationRequired( 'You must be logged in to update this history' )
            anon_allowed_payload = {}
            if 'deleted' in payload:
                anon_allowed_payload[ 'deleted' ] = payload[ 'deleted' ]
            if 'visible' in payload:
                anon_allowed_payload[ 'visible' ] = payload[ 'visible' ]
            payload = self._validate_and_parse_update_payload( anon_allowed_payload )

            hda = self.mgrs.hdas.get( trans, self._decode_id( trans, id ),
                check_ownership=False, check_accessible=False )
            hda = self.mgrs.hdas.err_if_uploading( trans, hda )
            if hda.history != trans.history:
                raise exceptions.AuthenticationRequired( 'You must be logged in to update this dataset' )

        else:
            payload = self._validate_and_parse_update_payload( payload )
            # only check_state if not deleting, otherwise cannot delete uploading files
            check_state = not payload.get( 'deleted', False )
            hda = self.mgrs.hdas.get( trans, self._decode_id( trans, id ),
                check_ownership=True, check_accessible=True )
            if check_state:
                hda = self.mgrs.hdas.err_if_uploading( trans, hda )
            #hda = self.get_dataset( trans, id, check_ownership=True, check_accessible=True, check_state=check_state )

        if hda and isinstance( hda, trans.model.HistoryDatasetAssociation ):
            changed = self.set_hda_from_dict( trans, hda, payload )
            if payload.get( 'deleted', False ):
                self.stop_hda_creating_job( hda )

        return changed

    #TODO: allow anonymous del/purge and test security on this
    @expose_api
    def delete( self, trans, history_id, id, purge=False, **kwd ):
        """
        delete( self, trans, history_id, id, **kwd )
        * DELETE /api/histories/{history_id}/contents/{id}
            delete the HDA with the given ``id``
        .. note:: Currently does not stop any active jobs for which this dataset is an output.

        :type   id:     str
        :param  id:     the encoded id of the history to delete
        :type   purge:  bool
        :param  purge:  if True, purge the HDA
        :type   kwd:    dict
        :param  kwd:    (optional) dictionary structure containing:

            * payload:     a dictionary itself containing:
                * purge:   if True, purge the HDA

        .. note:: that payload optionally can be placed in the query string of the request.
            This allows clients that strip the request body to still purge the dataset.

        :rtype:     dict
        :returns:   an error object if an error occurred or a dictionary containing:
            * id:         the encoded id of the history,
            * deleted:    if the history was marked as deleted,
            * purged:     if the history was purged
        """
        contents_type = kwd.get('type', 'dataset')
        if contents_type == "dataset":
            return self.__delete_dataset( trans, history_id, id, purge=purge, **kwd )
        else:
            return self.__handle_unknown_contents_type( trans, contents_type )

    def __delete_dataset( self, trans, history_id, id, purge, **kwd ):
        # get purge from the query or from the request body payload (a request body is optional here)
        purge = util.string_as_bool( purge )
        if kwd.get( 'payload', None ):
            # payload takes priority
            purge = util.string_as_bool( kwd['payload'].get( 'purge', purge ) )

        hda = self.mgrs.hdas.get( trans, self._decode_id( trans, id ),
            check_ownership=True, check_accessible=True )
        self.mgrs.hdas.err_if_uploading( trans, hda )

        rval = { 'id' : id }
        hda.deleted = True
        if purge:
            if not trans.app.config.allow_user_dataset_purge:
                raise exceptions.ConfigDoesNotAllowException( 'This instance does not allow user dataset purging' )
            hda.purged = True
            trans.sa_session.add( hda )
            trans.sa_session.flush()
            if hda.dataset.user_can_purge:
                try:
                    hda.dataset.full_delete()
                    trans.sa_session.add( hda.dataset )
                except:
                    pass
                # flush now to preserve deleted state in case of later interruption
                trans.sa_session.flush()
            rval[ 'purged' ] = True

        self.stop_hda_creating_job( hda )
        trans.sa_session.flush()

        rval[ 'deleted' ] = True
        return rval

    def _validate_and_parse_update_payload( self, payload ):
        """
        Validate and parse incomming data payload for an HDA.
        """
        # This layer handles (most of the stricter idiot proofing):
        #   - unknown/unallowed keys
        #   - changing data keys from api key to attribute name
        #   - protection against bad data form/type
        #   - protection against malicious data content
        # all other conversions and processing (such as permissions, etc.) should happen down the line

        # keys listed here don't error when attempting to set, but fail silently
        #   this allows PUT'ing an entire model back to the server without attribute errors on uneditable attrs
        valid_but_uneditable_keys = (
            'id', 'name', 'type', 'api_type', 'model_class', 'history_id', 'hid',
            'accessible', 'purged', 'state', 'data_type', 'file_ext', 'file_size', 'misc_blurb',
            'download_url', 'visualizations', 'display_apps', 'display_types',
            'metadata_dbkey', 'metadata_column_names', 'metadata_column_types', 'metadata_columns',
            'metadata_comment_lines', 'metadata_data_lines'
        )
        validated_payload = {}
        for key, val in payload.items():
            if val is None:
                continue
            if key in ( 'name', 'genome_build', 'misc_info', 'annotation' ):
                val = self.validate_and_sanitize_basestring( key, val )
                #TODO: need better remap system or eliminate the need altogether
                key = 'dbkey' if key == 'genome_build' else key
                key = 'info'  if key == 'misc_info' else key
                validated_payload[ key ] = val
            if key in ( 'deleted', 'visible' ):
                validated_payload[ key ] = self.validate_boolean( key, val )
            elif key == 'tags':
                validated_payload[ key ] = self.validate_and_sanitize_basestring_list( key, val )
            elif key not in valid_but_uneditable_keys:
                pass
                #log.warn( 'unknown key: %s', str( key ) )
        return validated_payload

    def __handle_unknown_contents_type( self, trans, contents_type ):
        # TODO: raise a message exception instead of setting status and returning dict.
        trans.response.status = 400
        return { 'error': 'Unknown contents type %s' % type }


class HDAManager( object ):

    def __init__( self ):
        self.histories_mgr = histories.HistoryManager()

    def get( self, trans, unencoded_id, check_ownership=True, check_accessible=True ):
        """
        """
        # this is a replacement for UsesHistoryDatasetAssociationMixin because mixins are a bad soln/structure
        hda = trans.sa_session.query( trans.app.model.HistoryDatasetAssociation ).get( unencoded_id )
        if hda is None:
            raise exceptions.ObjectNotFound()
        hda = self.secure( trans, hda, check_ownership, check_accessible )
        return hda

    def secure( self, trans, hda, check_ownership=True, check_accessible=True ):
        """
        checks if (a) user owns item or (b) item is accessible to user.
        """
        # all items are accessible to an admin
        if trans.user and trans.user_is_admin():
            return hda
        if check_ownership:
            hda = self.check_ownership( trans, hda )
        if check_accessible:
            hda = self.check_accessible( trans, hda )
        return hda

    def can_access_dataset( self, trans, hda ):
        current_user_roles = trans.get_current_user_roles()
        return trans.app.security_agent.can_access_dataset( current_user_roles, hda.dataset )

    #TODO: is_owner, is_accessible

    def check_ownership( self, trans, hda ):
        if not trans.user:
            #if hda.history == trans.history:
            #    return hda
            raise exceptions.AuthenticationRequired( "Must be logged in to manage Galaxy datasets", type='error' )
        if trans.user_is_admin():
            return hda
        # check for ownership of the containing history and accessibility of the underlying dataset
        if( self.histories_mgr.is_owner( trans, hda.history )
        and self.can_access_dataset( trans, hda ) ):
            return hda
        raise exceptions.ItemOwnershipException(
            "HistoryDatasetAssociation is not owned by the current user", type='error' )

    def check_accessible( self, trans, hda ):
        if trans.user and trans.user_is_admin():
            return hda
        # check for access of the containing history...
        self.histories_mgr.check_accessible( trans, hda.history )
        # ...then the underlying dataset
        if self.can_access_dataset( trans, hda ):
            return hda
        raise exceptions.ItemAccessibilityException(
            "HistoryDatasetAssociation is not accessible to the current user", type='error' )

    def err_if_uploading( self, trans, hda ):
        if hda.state == trans.model.Dataset.states.UPLOAD:
            raise exceptions.Conflict( "Please wait until this dataset finishes uploading" )
        return hda
