import os, os.path, shutil, urllib, StringIO, re, gzip, tempfile, shutil, zipfile
from galaxy.web.base.controller import *
from galaxy import util, jobs
from galaxy.datatypes import sniff
from galaxy.security import RBACAgent
from galaxy.util.json import to_json_string
from galaxy.tools.actions import upload_common
from galaxy.web.controllers.forms import get_all_forms
from galaxy.model.orm import *
from galaxy.util.streamball import StreamBall
import logging, tempfile, zipfile, tarfile, os, sys

if sys.version_info[:2] < ( 2, 6 ):
    zipfile.BadZipFile = zipfile.error
if sys.version_info[:2] < ( 2, 5 ):
    zipfile.LargeZipFile = zipfile.error

log = logging.getLogger( __name__ )

# Test for available compression types
tmpd = tempfile.mkdtemp()
comptypes = []
for comptype in ( 'gz', 'bz2' ):
    tmpf = os.path.join( tmpd, 'compression_test.tar.' + comptype )
    try:
        archive = tarfile.open( tmpf, 'w:' + comptype )
        archive.close()
        comptypes.append( comptype )
    except tarfile.CompressionError:
        log.exception( "Compression error when testing %s compression.  This option will be disabled for library downloads." % comptype )
    try:
        os.unlink( tmpf )
    except OSError:
        pass
ziptype = '32'
tmpf = os.path.join( tmpd, 'compression_test.zip' )
try:
    archive = zipfile.ZipFile( tmpf, 'w', zipfile.ZIP_DEFLATED, True )
    archive.close()
    comptypes.append( 'zip' )
    ziptype = '64'
except RuntimeError:
    log.exception( "Compression error when testing zip compression. This option will be disabled for library downloads." )
except (TypeError, zipfile.LargeZipFile):
    # ZIP64 is only in Python2.5+.  Remove TypeError when 2.4 support is dropped
    log.warning( 'Max zip file size is 2GB, ZIP64 not supported' )
    comptypes.append( 'zip' )
try:
    os.unlink( tmpf )
except OSError:
    pass
os.rmdir( tmpd )

class LibraryCommon( BaseController ):
    @web.json
    def library_item_updates( self, trans, ids=None, states=None ):
        # Avoid caching
        trans.response.headers['Pragma'] = 'no-cache'
        trans.response.headers['Expires'] = '0'
        # Create new HTML for any that have changed
        rval = {}
        if ids is not None and states is not None:
            ids = map( int, ids.split( "," ) )
            states = states.split( "," )
            for id, state in zip( ids, states ):
                data = trans.sa_session.query( self.app.model.LibraryDatasetDatasetAssociation ).get( id )
                if data.state != state:
                    job_ldda = data
                    while job_ldda.copied_from_library_dataset_dataset_association:
                        job_ldda = job_ldda.copied_from_library_dataset_dataset_association
                    force_history_refresh = False
                    rval[id] = {
                        "state": data.state,
                        "html": unicode( trans.fill_template( "library/common/library_item_info.mako", ldda=data ), 'utf-8' )
                        #"force_history_refresh": force_history_refresh
                    }
        return rval
    @web.expose
    def browse_library( self, trans, cntrller, **kwd ):
        params = util.Params( kwd )
        msg = util.restore_text( params.get( 'msg', ''  ) )
        messagetype = params.get( 'messagetype', 'done' )
        library_id = params.get( 'id', None )
        if not library_id:
            # To handle bots
            msg = "You must specify a library id."
            return trans.response.send_redirect( web.url_for( controller=cntrller,
                                                              action='browse_libraries',
                                                              default_action=params.get( 'default_action', None ),
                                                              msg=util.sanitize_text( msg ),
                                                              messagetype='error' ) )
        library = trans.sa_session.query( trans.app.model.Library ).get( trans.security.decode_id( library_id ) )
        if not library:
            # To handle bots
            msg = "Invalid library id ( %s )." % str( library_id )
            return trans.response.send_redirect( web.url_for( controller=cntrller,
                                                              action='browse_libraries',
                                                              default_action=params.get( 'default_action', None ),
                                                              msg=util.sanitize_text( msg ),
                                                              messagetype='error' ) )
        show_deleted = util.string_as_bool( params.get( 'show_deleted', False ) )
        created_ldda_ids = params.get( 'created_ldda_ids', '' )
        hidden_folder_ids = util.listify( params.get( 'hidden_folder_ids', '' ) )
        current_user_roles = trans.get_current_user_roles()
        if created_ldda_ids and not msg:
            msg = "%d datasets are uploading in the background to the library '%s' (each is selected).  "  % \
                ( len( created_ldda_ids.split( ',' ) ), library.name )
            msg += "Don't navigate away from Galaxy or use the browser's \"stop\" or \"reload\" buttons (on this tab) until the "
            msg += "message \"This dataset is uploading\" is cleared from the \"Information\" column below for each selected dataset."
            messagetype = "info"
        return trans.fill_template( '/library/common/browse_library.mako',
                                    cntrller=cntrller,
                                    library=library,
                                    created_ldda_ids=created_ldda_ids,
                                    hidden_folder_ids=hidden_folder_ids,
                                    default_action=params.get( 'default_action', None ),
                                    show_deleted=show_deleted,
                                    comptypes=comptypes,
                                    current_user_roles=current_user_roles,
                                    msg=msg,
                                    messagetype=messagetype )
    @web.expose
    def library_info( self, trans, cntrller, **kwd ):
        params = util.Params( kwd )
        msg = util.restore_text( params.get( 'msg', ''  ) )
        messagetype = params.get( 'messagetype', 'done' )
        library_id = params.get( 'id', None )
        library = trans.sa_session.query( trans.app.model.Library ).get( trans.security.decode_id( library_id ) )
        # See if we have any associated templates
        widgets = library.get_template_widgets( trans )
        current_user_roles = trans.get_current_user_roles()
        if params.get( 'rename_library_button', False ):
            old_name = library.name
            new_name = util.restore_text( params.name )
            new_description = util.restore_text( params.description )
            if not new_name:
                msg = 'Enter a valid name'
                messagetype='error'
            else:
                library.name = new_name
                library.description = new_description
                # Rename the root_folder
                library.root_folder.name = new_name
                library.root_folder.description = new_description
                trans.sa_session.add_all( ( library, library.root_folder ) )
                trans.sa_session.flush()
                msg = "Library '%s' has been renamed to '%s'" % ( old_name, new_name )
                return trans.response.send_redirect( web.url_for( controller='library_common',
                                                                  action='library_info',
                                                                  cntrller=cntrller,
                                                                  id=trans.security.encode_id( library.id ),
                                                                  msg=util.sanitize_text( msg ),
                                                                  messagetype='done' ) )
        return trans.fill_template( '/library/common/library_info.mako',
                                    cntrller=cntrller,
                                    library=library,
                                    widgets=widgets,
                                    current_user_roles=current_user_roles,
                                    msg=msg,
                                    messagetype=messagetype )
    @web.expose
    def library_permissions( self, trans, cntrller, **kwd ):
        params = util.Params( kwd )
        msg = util.restore_text( params.get( 'msg', ''  ) )
        messagetype = params.get( 'messagetype', 'done' )
        library_id = params.get( 'id', None )
        library = trans.sa_session.query( trans.app.model.Library ).get( trans.security.decode_id( library_id ) )
        current_user_roles = trans.get_current_user_roles()
        if params.get( 'update_roles_button', False ):
            # The user clicked the Save button on the 'Associate With Roles' form
            permissions = {}
            for k, v in trans.app.model.Library.permitted_actions.items():
                in_roles = [ trans.sa_session.query( trans.app.model.Role ).get( x ) for x in util.listify( params.get( k + '_in', [] ) ) ]
                permissions[ trans.app.security_agent.get_action( v.action ) ] = in_roles
            trans.app.security_agent.set_all_library_permissions( library, permissions )
            trans.sa_session.refresh( library )
            # Copy the permissions to the root folder
            trans.app.security_agent.copy_library_permissions( library, library.root_folder )
            msg = "Permissions updated for library '%s'" % library.name
            return trans.response.send_redirect( web.url_for( controller='library_common',
                                                              action='library_permissions',
                                                              cntrller=cntrller,
                                                              id=trans.security.encode_id( library.id ),
                                                              msg=util.sanitize_text( msg ),
                                                              messagetype='done' ) )
        roles = trans.app.security_agent.get_legitimate_roles( trans, library )
        return trans.fill_template( '/library/common/library_permissions.mako',
                                    cntrller=cntrller,
                                    library=library,
                                    current_user_roles=current_user_roles,
                                    roles=roles,
                                    msg=msg,
                                    messagetype=messagetype )
    @web.expose
    def create_folder( self, trans, cntrller, parent_id, library_id, **kwd ):
        params = util.Params( kwd )
        msg = util.restore_text( params.get( 'msg', ''  ) )
        messagetype = params.get( 'messagetype', 'done' )
        folder = trans.sa_session.query( trans.app.model.LibraryFolder ).get( trans.security.decode_id( parent_id ) )
        if not folder:
            msg = "Invalid parent folder id (%s) specified" % str( parent_id )
            return trans.response.send_redirect( web.url_for( controller='library_common',
                                                              action='browse_library',
                                                              cntrller=cntrller,
                                                              id=library_id,
                                                              msg=util.sanitize_text( msg ),
                                                              messagetype='error' ) )
        if params.new == 'submitted':
            new_folder = trans.app.model.LibraryFolder( name=util.restore_text( params.name ),
                                                        description=util.restore_text( params.description ) )
            # We are associating the last used genome build with folders, so we will always
            # initialize a new folder with the first dbkey in util.dbnames which is currently
            # ?    unspecified (?)
            new_folder.genome_build = util.dbnames.default_value
            folder.add_folder( new_folder )
            trans.sa_session.add( new_folder )
            trans.sa_session.flush()
            # New folders default to having the same permissions as their parent folder
            trans.app.security_agent.copy_library_permissions( folder, new_folder )
            msg = "New folder named '%s' has been added to the library" % new_folder.name
            return trans.response.send_redirect( web.url_for( controller='library_common',
                                                              action='browse_library',
                                                              cntrller=cntrller,
                                                              id=library_id,
                                                              msg=util.sanitize_text( msg ),
                                                              messagetype='done' ) )
        return trans.fill_template( '/library/common/new_folder.mako',
                                    cntrller=cntrller,
                                    library_id=library_id,
                                    folder=folder,
                                    msg=msg,
                                    messagetype=messagetype )
    @web.expose
    def folder_info( self, trans, cntrller, id, library_id, **kwd ):
        params = util.Params( kwd )
        msg = util.restore_text( params.get( 'msg', ''  ) )
        messagetype = params.get( 'messagetype', 'done' )
        folder = trans.sa_session.query( trans.app.model.LibraryFolder ).get( trans.security.decode_id( id ) )
        current_user_roles = trans.get_current_user_roles()
        # See if we have any associated templates
        widgets = folder.get_template_widgets( trans )
        if params.get( 'rename_folder_button', False ):
            if cntrller=='library_admin' or trans.app.security_agent.can_modify_library_item( current_user_roles, folder ):
                old_name = folder.name
                new_name = util.restore_text( params.name )
                new_description = util.restore_text( params.description )
                if not new_name:
                    msg = 'Enter a valid name'
                    messagetype='error'
                else:
                    folder.name = new_name
                    folder.description = new_description
                    trans.sa_session.add( folder )
                    trans.sa_session.flush()
                    msg = "Folder '%s' has been renamed to '%s'" % ( old_name, new_name )
                    messagetype='done'
            else:
                msg = "You are not authorized to edit this folder"
                messagetype='error'
        return trans.fill_template( '/library/common/folder_info.mako',
                                    cntrller=cntrller,
                                    folder=folder,
                                    library_id=library_id,
                                    widgets=widgets,
                                    current_user_roles=current_user_roles,
                                    msg=util.sanitize_text( msg ),
                                    messagetype=messagetype )
    @web.expose
    def folder_permissions( self, trans, cntrller, id, library_id, **kwd ):
        params = util.Params( kwd )
        msg = util.restore_text( params.get( 'msg', ''  ) )
        messagetype = params.get( 'messagetype', 'done' )
        folder = trans.sa_session.query( trans.app.model.LibraryFolder ).get( trans.security.decode_id( id ) )
        if not folder:
            msg = "Invalid folder specified, id: %s" % str( id )
            return trans.response.send_redirect( web.url_for( controller='library_common',
                                                              action='browse_library',
                                                              cntrller=cntrller,
                                                              id=library_id,
                                                              msg=util.sanitize_text( msg ),
                                                              messagetype='error' ) )
        current_user_roles = trans.get_current_user_roles()
        if params.get( 'update_roles_button', False ):
            # The user clicked the Save button on the 'Associate With Roles' form
            if cntrller == 'library_admin' or trans.app.security_agent.can_manage_library_item( current_user_roles, folder ):
                permissions = {}
                for k, v in trans.app.model.Library.permitted_actions.items():
                    if k != 'LIBRARY_ACCESS':
                        # LIBRARY_ACCESS is a special permission set only at the library level
                        # and it is not inherited.
                        in_roles = [ trans.sa_session.query( trans.app.model.Role ).get( int( x ) ) for x in util.listify( params.get( k + '_in', [] ) ) ]
                        permissions[ trans.app.security_agent.get_action( v.action ) ] = in_roles
                trans.app.security_agent.set_all_library_permissions( folder, permissions )
                trans.sa_session.refresh( folder )
                msg = 'Permissions updated for folder %s' % folder.name
                messagetype='done'
            else:
                msg = "You are not authorized to manage permissions on this folder"
                messagetype = "error"
            return trans.response.send_redirect( web.url_for( controller='library_common',
                                                              action='folder_permissions',
                                                              cntrller=cntrller,
                                                              id=trans.security.encode_id( folder.id ),
                                                              library_id=library_id,
                                                              msg=util.sanitize_text( msg ),
                                                              messagetype=messagetype ) )
        # If the library is public all roles are legitimate, but if the library is restricted, only those
        # roles associated with the LIBRARY_ACCESS permission are legitimate.
        library = trans.sa_session.query( trans.app.model.Library ).get( trans.security.decode_id( library_id ) )
        roles = trans.app.security_agent.get_legitimate_roles( trans, library )
        return trans.fill_template( '/library/common/folder_permissions.mako',
                                    cntrller=cntrller,
                                    folder=folder,
                                    library_id=library_id,
                                    current_user_roles=current_user_roles,
                                    roles=roles,
                                    msg=msg,
                                    messagetype=messagetype )
    @web.expose
    def ldda_edit_info( self, trans, cntrller, library_id, folder_id, id, **kwd ):
        params = util.Params( kwd )
        msg = util.restore_text( params.get( 'msg', ''  ) )
        messagetype = params.get( 'messagetype', 'done' )
        ldda = trans.sa_session.query( trans.app.model.LibraryDatasetDatasetAssociation ).get( trans.security.decode_id( id ) )
        if not ldda:
            msg = "Invalid LibraryDatasetDatasetAssociation specified, id: %s" % str( id )
            return trans.response.send_redirect( web.url_for( controller='library_common',
                                                              action='browse_library',
                                                              cntrller=cntrller,
                                                              id=library_id,
                                                              msg=util.sanitize_text( msg ),
                                                              messagetype='error' ) )
        dbkey = params.get( 'dbkey', '?' )
        if isinstance( dbkey, list ):
            dbkey = dbkey[0]
        current_user_roles = trans.get_current_user_roles()
        file_formats = [ dtype_name for dtype_name, dtype_value in trans.app.datatypes_registry.datatypes_by_extension.iteritems() if dtype_value.allow_datatype_change ]
        file_formats.sort()
        # See if we have any associated templates
        widgets = ldda.get_template_widgets( trans )
        if params.get( 'change', False ):
            # The user clicked the Save button on the 'Change data type' form
            if cntrller=='library_admin' or trans.app.security_agent.can_modify_library_item( current_user_roles, ldda ):
                if ldda.datatype.allow_datatype_change and trans.app.datatypes_registry.get_datatype_by_extension( params.datatype ).allow_datatype_change:
                    trans.app.datatypes_registry.change_datatype( ldda, params.datatype )
                    trans.sa_session.flush()
                    msg = "Data type changed for library dataset '%s'" % ldda.name
                    messagetype = 'done'
                else:
                    msg = "You are unable to change datatypes in this manner. Changing %s to %s is not allowed." % ( ldda.extension, params.datatype )
                    messagetype = 'error'
            else:
                msg = "You are not authorized to change the data type of dataset '%s'" % ldda.name
                messagetype = 'error'
            return trans.fill_template( "/library/common/ldda_edit_info.mako",
                                        cntrller=cntrller,
                                        ldda=ldda,
                                        library_id=library_id,
                                        file_formats=file_formats,
                                        widgets=widgets,
                                        current_user_roles=current_user_roles,
                                        msg=msg,
                                        messagetype=messagetype )
        elif params.get( 'save', False ):
            # The user clicked the Save button on the 'Edit Attributes' form
            if cntrller=='library_admin' or trans.app.security_agent.can_modify_library_item( current_user_roles, ldda ):
                old_name = ldda.name
                new_name = util.restore_text( params.get( 'name', '' ) )
                new_info = util.restore_text( params.get( 'info', '' ) )
                new_message = util.restore_text( params.get( 'message', '' ) )
                if not new_name:
                    msg = 'Enter a valid name'
                    messagetype = 'error'
                else:
                    ldda.name = new_name
                    ldda.info = new_info
                    ldda.message = new_message
                    # The following for loop will save all metadata_spec items
                    for name, spec in ldda.datatype.metadata_spec.items():
                        if spec.get("readonly"):
                            continue
                        optional = params.get( "is_" + name, None )
                        if optional and optional == 'true':
                            # optional element... == 'true' actually means it is NOT checked (and therefore ommitted)
                            setattr( ldda.metadata, name, None )
                        else:
                            setattr( ldda.metadata, name, spec.unwrap( params.get ( name, None ) ) )
                    ldda.metadata.dbkey = dbkey
                    ldda.datatype.after_setting_metadata( ldda )
                    trans.sa_session.flush()
                    msg = 'Attributes updated for library dataset %s' % ldda.name
                    messagetype = 'done'
            else:
                msg = "You are not authorized to edit the attributes of dataset '%s'" % ldda.name
                messagetype = 'error'
            return trans.fill_template( "/library/common/ldda_edit_info.mako",
                                        cntrller=cntrller,
                                        ldda=ldda,
                                        library_id=library_id,
                                        file_formats=file_formats,
                                        widgets=widgets,
                                        current_user_roles=current_user_roles,
                                        msg=msg,
                                        messagetype=messagetype )
        elif params.get( 'detect', False ):
            # The user clicked the Auto-detect button on the 'Edit Attributes' form
            if cntrller=='library_admin' or trans.app.security_agent.can_modify_library_item( current_user_roles, ldda ):
                for name, spec in ldda.datatype.metadata_spec.items():
                    # We need to be careful about the attributes we are resetting
                    if name not in [ 'name', 'info', 'dbkey' ]:
                        if spec.get( 'default' ):
                            setattr( ldda.metadata, name, spec.unwrap( spec.get( 'default' ) ) )
                ldda.datatype.set_meta( ldda )
                ldda.datatype.after_setting_metadata( ldda )
                trans.sa_session.flush()
                msg = 'Attributes updated for library dataset %s' % ldda.name
                messagetype = 'done'
            else:
                msg = "You are not authorized to edit the attributes of dataset '%s'" % ldda.name
                messagetype = 'error'
            return trans.fill_template( "/library/common/ldda_edit_info.mako",
                                        cntrller=cntrller,
                                        ldda=ldda,
                                        library_id=library_id,
                                        file_formats=file_formats,
                                        widgets=widgets,
                                        current_user_roles=current_user_roles,
                                        msg=msg,
                                        messagetype=messagetype )
        if cntrller=='library_admin' or trans.app.security_agent.can_modify_library_item( current_user_roles, ldda ):
            if "dbkey" in ldda.datatype.metadata_spec and not ldda.metadata.dbkey:
                # Copy dbkey into metadata, for backwards compatability
                # This looks like it does nothing, but getting the dbkey
                # returns the metadata dbkey unless it is None, in which
                # case it resorts to the old dbkey.  Setting the dbkey
                # sets it properly in the metadata
                ldda.metadata.dbkey = ldda.dbkey
        return trans.fill_template( "/library/common/ldda_edit_info.mako",
                                    cntrller=cntrller,
                                    ldda=ldda,
                                    library_id=library_id,
                                    file_formats=file_formats,
                                    widgets=widgets,
                                    current_user_roles=current_user_roles,
                                    msg=msg,
                                    messagetype=messagetype )
    @web.expose
    def ldda_display_info( self, trans, cntrller, library_id, folder_id, id, **kwd ):
        params = util.Params( kwd )
        msg = util.restore_text( params.get( 'msg', ''  ) )
        messagetype = params.get( 'messagetype', 'done' )
        show_deleted = util.string_as_bool( params.get( 'show_deleted', False ) )
        ldda = trans.sa_session.query( trans.app.model.LibraryDatasetDatasetAssociation ).get( trans.security.decode_id( id ) )
        if not ldda:
            msg = "Invalid LibraryDatasetDatasetAssociation specified, id: %s" % str( id )
            return trans.response.send_redirect( web.url_for( controller='library_common',
                                                              action='browse_library',
                                                              cntrller=cntrller,
                                                              id=library_id,
                                                              msg=util.sanitize_text( msg ),
                                                              messagetype='error' ) )
        library = trans.sa_session.query( trans.app.model.Library ).get( trans.security.decode_id( library_id ) )
        # See if we have any associated templates
        widgets = ldda.get_template_widgets( trans )
        current_user_roles = trans.get_current_user_roles()
        return trans.fill_template( '/library/common/ldda_info.mako',
                                    cntrller=cntrller,
                                    ldda=ldda,
                                    library=library,
                                    show_deleted=show_deleted,
                                    widgets=widgets,
                                    msg=msg,
                                    messagetype=messagetype )
    @web.expose
    def ldda_permissions( self, trans, cntrller, library_id, folder_id, id, **kwd ):
        params = util.Params( kwd )
        msg = util.restore_text( params.get( 'msg', ''  ) )
        messagetype = params.get( 'messagetype', 'done' )
        ids = util.listify( id )
        lddas = []
        for id in [ trans.security.decode_id( id ) for id in ids ]:
            ldda = trans.sa_session.query( trans.app.model.LibraryDatasetDatasetAssociation ).get( id )
            if ldda is None:
                msg = 'You specified an invalid LibraryDatasetDatasetAssociation id: %s' %str( id )
                trans.response.send_redirect( web.url_for( controller='library_common',
                                                           action='browse_library',
                                                           cntrller=cntrller,
                                                           id=library_id,
                                                           msg=util.sanitize_text( msg ),
                                                           messagetype='error' ) )
            lddas.append( ldda )
        # If the library is public all roles are legitimate, but if the library is restricted, only those
        # roles associated with the LIBRARY_ACCESS permission are legitimate.
        library = trans.sa_session.query( trans.app.model.Library ).get( trans.security.decode_id( library_id ) )
        roles = trans.app.security_agent.get_legitimate_roles( trans, library )
        if params.get( 'update_roles_button', False ):
            current_user_roles = trans.get_current_user_roles()
            if cntrller=='library_admin' or ( trans.app.security_agent.can_manage_library_item( current_user_roles, ldda ) and \
                                              trans.app.security_agent.can_manage_dataset( current_user_roles, ldda.dataset ) ):
                permissions, in_roles, error, msg = \
                    trans.app.security_agent.check_library_dataset_access( trans, trans.app.security.decode_id( library_id ), **kwd )
                for ldda in lddas:
                    # Set the DATASET permissions on the Dataset.
                    if error == trans.app.security_agent.IN_ACCESSIBLE:
                        # If the check_library_dataset_access() returned a "in_accessible" error, then we keep the original role
                        # associations for the DATASET_ACCESS permission on each ldda.
                        a = trans.app.security_agent.get_action( trans.app.security_agent.permitted_actions.DATASET_ACCESS.action )
                        permissions[ a ] = ldda.get_access_roles( trans )
                    trans.app.security_agent.set_all_dataset_permissions( ldda.dataset, permissions )
                    trans.sa_session.refresh( ldda.dataset )
                # Set the LIBRARY permissions on the LibraryDataset
                # NOTE: the LibraryDataset and LibraryDatasetDatasetAssociation will be set with the same permissions
                permissions = {}
                for k, v in trans.app.model.Library.permitted_actions.items():
                    if k != 'LIBRARY_ACCESS':
                        # LIBRARY_ACCESS is a special permission set only at the library level and it is not inherited.
                        in_roles = [ trans.sa_session.query( trans.app.model.Role ).get( x ) for x in util.listify( kwd.get( k + '_in', [] ) ) ]
                        permissions[ trans.app.security_agent.get_action( v.action ) ] = in_roles
                for ldda in lddas:
                    trans.app.security_agent.set_all_library_permissions( ldda.library_dataset, permissions )
                    trans.sa_session.refresh( ldda.library_dataset )
                    # Set the LIBRARY permissions on the LibraryDatasetDatasetAssociation
                    trans.app.security_agent.set_all_library_permissions( ldda, permissions )
                    trans.sa_session.refresh( ldda )
                if error:
                    messagetype = 'error'
                else:
                    msg = 'Permissions have been updated on %d datasets.' % len( lddas )
                    messagetype= 'done'
            else:
                msg = "You are not authorized to change the permissions of dataset '%s'" % ldda.name
                messagetype = 'error'
            return trans.fill_template( "/library/common/ldda_permissions.mako",
                                        cntrller=cntrller,
                                        lddas=lddas,
                                        library_id=library_id,
                                        roles=roles,
                                        msg=msg,
                                        messagetype=messagetype )
        if len( ids ) > 1:
            # Ensure that the permissions across all library items are identical, otherwise we can't update them together.
            check_list = []
            for ldda in lddas:
                permissions = []
                # Check the library level permissions - the permissions on the LibraryDatasetDatasetAssociation
                # will always be the same as the permissions on the associated LibraryDataset.
                for library_permission in trans.app.security_agent.get_permissions( ldda.library_dataset ):
                    if library_permission.action not in permissions:
                        permissions.append( library_permission.action )
                for dataset_permission in trans.app.security_agent.get_permissions( ldda.dataset ):
                    if dataset_permission.action not in permissions:
                        permissions.append( dataset_permission.action )
                permissions.sort()
                if not check_list:
                    check_list = permissions
                if permissions != check_list:
                    msg = 'The datasets you selected do not have identical permissions, so they can not be updated together'
                    trans.response.send_redirect( web.url_for( controller='library_common',
                                                               action='browse_library',
                                                               cntrller=cntrller,
                                                               id=library_id,
                                                               msg=util.sanitize_text( msg ),
                                                               messagetype='error' ) )
        # Display permission form, permissions will be updated for all lddas simultaneously.
        return trans.fill_template( "/library/common/ldda_permissions.mako",
                                    cntrller=cntrller,
                                    lddas=lddas,
                                    library_id=library_id,
                                    roles=roles,
                                    msg=msg,
                                    messagetype=messagetype )
    @web.expose
    def upload_library_dataset( self, trans, cntrller, library_id, folder_id, **kwd ):
        params = util.Params( kwd )
        msg = util.restore_text( params.get( 'msg', ''  ) )
        messagetype = params.get( 'messagetype', 'done' )
        deleted = util.string_as_bool( params.get( 'deleted', False ) )
        show_deleted = util.string_as_bool( params.get( 'show_deleted', False ) )
        dbkey = params.get( 'dbkey', '?' )
        if isinstance( dbkey, list ):
            last_used_build = dbkey[0]
        else:
            last_used_build = dbkey
        folder = trans.sa_session.query( trans.app.model.LibraryFolder ).get( trans.security.decode_id( folder_id ) )
        if folder and last_used_build in [ 'None', None, '?' ]:
            last_used_build = folder.genome_build
        replace_id = params.get( 'replace_id', None )
        if replace_id not in [ None, 'None' ]:
            replace_dataset = trans.sa_session.query( trans.app.model.LibraryDataset ).get( trans.security.decode_id( replace_id ) )
            # The name is separately - by the time the new ldda is created,
            # replace_dataset.name will point to the new ldda, not the one it's
            # replacing.
            replace_dataset_name = replace_dataset.name
            if not last_used_build:
                last_used_build = replace_dataset.library_dataset_dataset_association.dbkey
            # Don't allow multiple datasets to be uploaded when replacing a dataset with a new version
            upload_option = 'upload_file'
        else:
            replace_dataset = None
            upload_option = params.get( 'upload_option', 'upload_file' )
        if cntrller == 'library':
            current_user_roles = trans.get_current_user_roles()
        if cntrller == 'library_admin' or \
            ( trans.app.security_agent.can_add_library_item( current_user_roles, folder ) or \
              ( replace_dataset and trans.app.security_agent.can_modify_library_item( current_user_roles, replace_dataset ) ) ):
            if params.get( 'runtool_btn', False ) or params.get( 'ajax_upload', False ):
                # Check to see if the user selected roles to associate with the DATASET_ACCESS permission
                # on the dataset that would make the dataset in-accessible to everyone.
                roles = params.get( 'roles', False )
                error = None
                if roles:
                    vars = dict( DATASET_ACCESS_in=roles )
                    permissions, in_roles, error, msg = \
                        trans.app.security_agent.check_library_dataset_access( trans, trans.app.security.decode_id( library_id ), **vars )
                    if error:
                        if error == trans.app.security_agent.IN_ACCESSIBLE:
                            msg = "At least 1 user must have every role associated with accessing datasets.  The roles you "
                            msg += "attempted to associate for access would make the datasets in-accessible by everyone."
                        messagetype = 'error'
                if not error:
                    # See if we have any inherited templates, but do not inherit contents.
                    info_association, inherited = folder.get_info_association( inherited=True )
                    if info_association:
                        template_id = str( info_association.template.id )
                        widgets = folder.get_template_widgets( trans, get_contents=False )
                    else:
                        template_id = 'None'
                        widgets = []
                    created_outputs = trans.webapp.controllers[ 'library_common' ].upload_dataset( trans,
                                                                                                   cntrller=cntrller,
                                                                                                   library_id=library_id,
                                                                                                   folder_id=folder_id,
                                                                                                   template_id=template_id,
                                                                                                   widgets=widgets,
                                                                                                   replace_dataset=replace_dataset,
                                                                                                   **kwd )
                    if created_outputs:
                        total_added = len( created_outputs.values() )
                        ldda_id_list = [ str( v.id ) for v in created_outputs.values() ]
                        if replace_dataset:
                            msg = "Added %d dataset versions to the library dataset '%s' in the folder '%s'." % ( total_added, replace_dataset_name, folder.name )
                        else:
                            if not folder.parent:
                                # Libraries have the same name as their root_folder
                                msg = "Added %d datasets to the library '%s' (each is selected).  " % ( total_added, folder.name )
                            else:
                                msg = "Added %d datasets to the folder '%s' (each is selected).  " % ( total_added, folder.name )
                            if cntrller == 'library_admin':
                                msg += "Click the Go button at the bottom of this page to edit the permissions on these datasets if necessary."
                                messagetype='done'
                            else:
                                # Since permissions on all LibraryDatasetDatasetAssociations must be the same at this point, we only need
                                # to check one of them to see if the current user can manage permissions on them.
                                check_ldda = trans.sa_session.query( trans.app.model.LibraryDatasetDatasetAssociation ).get( ldda_id_list[0] )
                                if trans.app.security_agent.can_manage_library_item( current_user_roles, check_ldda ):
                                    if replace_dataset:
                                        default_action = ''
                                    else:
                                        msg += "Click the Go button at the bottom of this page to edit the permissions on these datasets if necessary."
                                        default_action = 'manage_permissions'
                                else:
                                    default_action = 'add'
                                trans.response.send_redirect( web.url_for( controller='library_common',
                                                                           action='browse_library',
                                                                           cntrller=cntrller,
                                                                           id=library_id,
                                                                           default_action=default_action,
                                                                           created_ldda_ids=",".join( ldda_id_list ), 
                                                                           msg=util.sanitize_text( msg ), 
                                                                           messagetype='done' ) )
                        
                    else:
                        msg = "Upload failed"
                        messagetype='error'
                    trans.response.send_redirect( web.url_for( controller='library_common',
                                                               action='browse_library',
                                                               cntrller=cntrller,
                                                               id=library_id,
                                                               created_ldda_ids=",".join( [ str( v.id ) for v in created_outputs.values() ] ),
                                                               msg=util.sanitize_text( msg ),
                                                               messagetype=messagetype ) )
        # See if we have any inherited templates, but do not inherit contents.
        widgets = folder.get_template_widgets( trans, get_contents=False )
        upload_option = params.get( 'upload_option', 'upload_file' )
        # No dataset(s) specified, so display the upload form.  Send list of data formats to the form
        # so the "extension" select list can be populated dynamically
        file_formats = trans.app.datatypes_registry.upload_file_formats
        # Send list of genome builds to the form so the "dbkey" select list can be populated dynamically
        def get_dbkey_options( last_used_build ):
            for dbkey, build_name in util.dbnames:
                yield build_name, dbkey, ( dbkey==last_used_build )
        dbkeys = get_dbkey_options( last_used_build )
        # Send list of legitimate roles to the form so the dataset can be associated with 1 or more of them.
        # If the library is public, all active roles are legitimate.  If the library is restricted by the
        # LIBRARY_ACCESS permission, only those roles associated with that permission are legitimate.
        library = trans.sa_session.query( trans.app.model.Library ).get( trans.security.decode_id( library_id ) )
        roles = trans.app.security_agent.get_legitimate_roles( trans, library )
        # Send the current history to the form to enable importing datasets from history to library
        history = trans.get_history()
        trans.sa_session.refresh( history )
        # If we're using nginx upload, override the form action
        action = web.url_for( controller='library_common', action='upload_library_dataset', cntrller=cntrller )
        if upload_option == 'upload_file' and trans.app.config.nginx_upload_path:
            # url_for is intentionally not used on the base URL here -
            # nginx_upload_path is expected to include the proxy prefix if the
            # administrator intends for it to be part of the URL.  We also
            # redirect to the library or library_admin controller rather than
            # library_common because GET arguments can't be used in conjunction
            # with nginx upload (nginx can't do percent decoding without a
            # bunch of hacky rewrite rules).
            action = trans.app.config.nginx_upload_path + '?nginx_redir=' + web.url_for( controller=cntrller, action='upload_library_dataset' )
        return trans.fill_template( '/library/common/upload.mako',
                                    cntrller=cntrller,
                                    upload_option=upload_option,
                                    action=action,
                                    library_id=library_id,
                                    folder_id=folder_id,
                                    replace_dataset=replace_dataset,
                                    file_formats=file_formats,
                                    dbkeys=dbkeys,
                                    last_used_build=last_used_build,
                                    roles=roles,
                                    history=history,
                                    widgets=widgets,
                                    msg=msg,
                                    messagetype=messagetype )
    def upload_dataset( self, trans, cntrller, library_id, folder_id, replace_dataset=None, **kwd ):
        # Set up the traditional tool state/params
        tool_id = 'upload1'
        tool = trans.app.toolbox.tools_by_id[ tool_id ]
        state = tool.new_state( trans )
        errors = tool.update_state( trans, tool.inputs_by_page[0], state.inputs, kwd )
        tool_params = state.inputs
        dataset_upload_inputs = []
        for input_name, input in tool.inputs.iteritems():
            if input.type == "upload_dataset":
                dataset_upload_inputs.append( input )
        # Library-specific params
        params = util.Params( kwd ) # is this filetoolparam safe?
        library_bunch = upload_common.handle_library_params( trans, params, folder_id, replace_dataset )
        msg = util.restore_text( params.get( 'msg', ''  ) )
        messagetype = params.get( 'messagetype', 'done' )
        server_dir = util.restore_text( params.get( 'server_dir', '' ) )
        if replace_dataset not in [ None, 'None' ]:
            replace_id = trans.security.encode_id( replace_dataset.id )
        else:
            replace_id = None
        upload_option = params.get( 'upload_option', 'upload_file' )
        err_redirect = False
        if upload_option == 'upload_directory':
            if server_dir in [ None, 'None', '' ]:
                err_redirect = True
            if cntrller == 'library_admin':
                import_dir = trans.app.config.library_import_dir
                import_dir_desc = 'library_import_dir'
                full_dir = os.path.join( import_dir, server_dir )
            else:
                import_dir = trans.app.config.user_library_import_dir
                import_dir_desc = 'user_library_import_dir'
                if server_dir == trans.user.email:
                    full_dir = os.path.join( import_dir, server_dir )
                else:
                    full_dir = os.path.join( import_dir, trans.user.email, server_dir )
            if import_dir:
                msg = 'Select a directory'
            else:
                msg = '"%s" is not defined in the Galaxy configuration file' % import_dir_desc
        # Proceed with (mostly) regular upload processing
        precreated_datasets = upload_common.get_precreated_datasets( trans, tool_params, trans.app.model.LibraryDatasetDatasetAssociation, controller=cntrller )
        if upload_option == 'upload_file':
            tool_params = upload_common.persist_uploads( tool_params )
            uploaded_datasets = upload_common.get_uploaded_datasets( trans, tool_params, precreated_datasets, dataset_upload_inputs, library_bunch=library_bunch )
        elif upload_option == 'upload_directory':
            uploaded_datasets, err_redirect, msg = self.get_server_dir_uploaded_datasets( trans, params, full_dir, import_dir_desc, library_bunch, err_redirect, msg )
        elif upload_option == 'upload_paths':
            uploaded_datasets, err_redirect, msg = self.get_path_paste_uploaded_datasets( trans, params, library_bunch, err_redirect, msg )
        upload_common.cleanup_unused_precreated_datasets( precreated_datasets )
        if upload_option == 'upload_file' and not uploaded_datasets:
            msg = 'Select a file, enter a URL or enter text'
            err_redirect = True
        if err_redirect:
            trans.response.send_redirect( web.url_for( controller='library_common',
                                                       action='upload_library_dataset',
                                                       cntrller=cntrller,
                                                       library_id=library_id,
                                                       folder_id=folder_id,
                                                       replace_id=replace_id,
                                                       upload_option=upload_option,
                                                       msg=util.sanitize_text( msg ),
                                                       messagetype='error' ) )
        json_file_path = upload_common.create_paramfile( trans, uploaded_datasets )
        data_list = [ ud.data for ud in uploaded_datasets ]
        return upload_common.create_job( trans, tool_params, tool, json_file_path, data_list, folder=library_bunch.folder )
    def make_library_uploaded_dataset( self, trans, params, name, path, type, library_bunch, in_folder=None ):
        library_bunch.replace_dataset = None # not valid for these types of upload
        uploaded_dataset = util.bunch.Bunch()
        uploaded_dataset.name = name
        uploaded_dataset.path = path
        uploaded_dataset.type = type
        uploaded_dataset.ext = None
        uploaded_dataset.file_type = params.file_type
        uploaded_dataset.dbkey = params.dbkey
        uploaded_dataset.space_to_tab = params.space_to_tab
        if in_folder:
            uploaded_dataset.in_folder = in_folder
        uploaded_dataset.data = upload_common.new_upload( trans, uploaded_dataset, library_bunch )
        if params.get( 'link_data_only', False ):
            uploaded_dataset.link_data_only = True
            uploaded_dataset.data.file_name = os.path.abspath( path )
            trans.sa_session.add( uploaded_dataset.data )
            trans.sa_session.flush()
        return uploaded_dataset
    def get_server_dir_uploaded_datasets( self, trans, params, full_dir, import_dir_desc, library_bunch, err_redirect, msg ):
        files = []
        try:
            for entry in os.listdir( full_dir ):
                # Only import regular files
                path = os.path.join( full_dir, entry )
                if os.path.islink( path ) and os.path.isfile( path ) and params.get( 'link_data_only', False ):
                    # If we're linking instead of copying, link the file the link points to, not the link itself.
                    link_path = os.readlink( path )
                    if os.path.isabs( link_path ):
                        path = link_path
                    else:
                        path = os.path.abspath( os.path.join( os.path.dirname( path ), link_path ) )
                if os.path.isfile( path ):
                    files.append( path )
        except Exception, e:
            msg = "Unable to get file list for configured %s, error: %s" % ( import_dir_desc, str( e ) )
            err_redirect = True
            return None, err_redirect, msg
        if not files:
            msg = "The directory '%s' contains no valid files" % full_dir
            err_redirect = True
            return None, err_redirect, msg
        uploaded_datasets = []
        for file in files:
            name = os.path.basename( file )
            uploaded_datasets.append( self.make_library_uploaded_dataset( trans, params, name, file, 'server_dir', library_bunch ) )
        return uploaded_datasets, None, None
    def get_path_paste_uploaded_datasets( self, trans, params, library_bunch, err_redirect, msg ):
        if params.get( 'filesystem_paths', '' ) == '':
            msg = "No paths entered in the upload form"
            err_redirect = True
            return None, err_redirect, msg
        preserve_dirs = True
        if params.get( 'dont_preserve_dirs', False ):
            preserve_dirs = False
        # locate files
        bad_paths = []
        uploaded_datasets = []
        for line in [ l.strip() for l in params.filesystem_paths.splitlines() if l.strip() ]:
            path = os.path.abspath( line )
            if not os.path.exists( path ):
                bad_paths.append( path )
                continue
            # don't bother processing if we're just going to return an error
            if not bad_paths:
                if os.path.isfile( path ):
                    name = os.path.basename( path )
                    uploaded_datasets.append( self.make_library_uploaded_dataset( trans, params, name, path, 'path_paste', library_bunch ) )
                for basedir, dirs, files in os.walk( line ):
                    for file in files:
                        file_path = os.path.abspath( os.path.join( basedir, file ) )
                        if preserve_dirs:
                            in_folder = os.path.dirname( file_path.replace( path, '', 1 ).lstrip( '/' ) )
                        else:
                            in_folder = None
                        uploaded_datasets.append( self.make_library_uploaded_dataset( trans, params, file, file_path, 'path_paste', library_bunch, in_folder ) )
        if bad_paths:
            msg = "Invalid paths:<br><ul><li>%s</li></ul>" % "</li><li>".join( bad_paths )
            err_redirect = True
            return None, err_redirect, msg
        return uploaded_datasets, None, None
    @web.expose
    def add_history_datasets_to_library( self, trans, cntrller, library_id, folder_id, hda_ids='', **kwd ):
        params = util.Params( kwd )
        msg = util.restore_text( params.get( 'msg', ''  ) )
        messagetype = params.get( 'messagetype', 'done' )
        try:
            folder = trans.sa_session.query( trans.app.model.LibraryFolder ).get( trans.security.decode_id( folder_id ) )
        except:
            msg = "Invalid folder id: %s" % str( folder_id )
            return trans.response.send_redirect( web.url_for( controller='library_common',
                                                              action='browse_library',
                                                              cntrller=cntrller,
                                                              id=library_id,
                                                              msg=util.sanitize_text( msg ),
                                                              messagetype='error' ) )
        replace_id = params.get( 'replace_id', None )
        if replace_id:
            replace_dataset = trans.sa_session.query( trans.app.model.LibraryDataset ).get( trans.security.decode_id( replace_id ) )
        else:
            replace_dataset = None
        # See if the current history is empty
        history = trans.get_history()
        trans.sa_session.refresh( history )
        if not history.active_datasets:
            msg = 'Your current history is empty'
            return trans.response.send_redirect( web.url_for( controller='library_common',
                                                              action='browse_library',
                                                              cntrller=cntrller,
                                                              id=library_id,
                                                              msg=util.sanitize_text( msg ),
                                                              messagetype='error' ) )
        if params.get( 'add_history_datasets_to_library_button', False ):
            hda_ids = util.listify( hda_ids )
            if hda_ids:
                dataset_names = []
                created_ldda_ids = ''
                for hda_id in hda_ids:
                    hda = trans.sa_session.query( trans.app.model.HistoryDatasetAssociation ).get( trans.security.decode_id( hda_id ) )
                    if hda:
                        ldda = hda.to_library_dataset_dataset_association( target_folder=folder, replace_dataset=replace_dataset )
                        created_ldda_ids = '%s,%s' % ( created_ldda_ids, str( ldda.id ) )
                        dataset_names.append( ldda.name )
                        if not replace_dataset:
                            # If replace_dataset is None, the Library level permissions will be taken from the folder and applied to the new 
                            # LDDA and LibraryDataset.
                            trans.app.security_agent.copy_library_permissions( folder, ldda )
                            trans.app.security_agent.copy_library_permissions( folder, ldda.library_dataset )
                        # Permissions must be the same on the LibraryDatasetDatasetAssociation and the associated LibraryDataset
                        trans.app.security_agent.copy_library_permissions( ldda.library_dataset, ldda )
                    else:
                        msg = "The requested HistoryDatasetAssociation id %s is invalid" % str( hda_id )
                        return trans.response.send_redirect( web.url_for( controller='library_common',
                                                                          action='browse_library',
                                                                          cntrller=cntrller,
                                                                          id=library_id,
                                                                          msg=util.sanitize_text( msg ),
                                                                          messagetype='error' ) )
                if created_ldda_ids:
                    created_ldda_ids = created_ldda_ids.lstrip( ',' )
                    ldda_id_list = created_ldda_ids.split( ',' )
                    total_added = len( ldda_id_list )
                    if replace_dataset:
                        msg = "Added %d dataset versions to the library dataset '%s' in the folder '%s'." % ( total_added, replace_dataset.name, folder.name )
                    else:
                        if not folder.parent:
                            # Libraries have the same name as their root_folder
                            msg = "Added %d datasets to the library '%s' (each is selected).  " % ( total_added, folder.name )
                        else:
                            msg = "Added %d datasets to the folder '%s' (each is selected).  " % ( total_added, folder.name )
                        if cntrller == 'library_admin':
                            msg += "Click the Go button at the bottom of this page to edit the permissions on these datasets if necessary."
                        else:
                            # Since permissions on all LibraryDatasetDatasetAssociations must be the same at this point, we only need
                            # to check one of them to see if the current user can manage permissions on them.
                            check_ldda = trans.sa_session.query( trans.app.model.LibraryDatasetDatasetAssociation ).get( trans.security.decode_id( ldda_id_list[0] ) )
                            current_user_roles = trans.get_current_user_roles()
                            if trans.app.security_agent.can_manage_library_item( current_user_roles, check_ldda ):
                                if replace_dataset:
                                    default_action = ''
                                else:
                                    msg += "Click the Go button at the bottom of this page to edit the permissions on these datasets if necessary."
                                    default_action = 'manage_permissions'
                            else:
                                default_action = 'add'
                    return trans.response.send_redirect( web.url_for( controller='library_common',
                                                                      action='browse_library',
                                                                      cntrller=cntrller,
                                                                      id=library_id,
                                                                      created_ldda_ids=created_ldda_ids,
                                                                      msg=util.sanitize_text( msg ),
                                                                      messagetype='done' ) )
            else:
                msg = 'Select at least one dataset from the list of active datasets in your current history'
                messagetype = 'error'
                last_used_build = folder.genome_build
                upload_option = params.get( 'upload_option', 'import_from_history' )
                # Send list of data formats to the form so the "extension" select list can be populated dynamically
                file_formats = trans.app.datatypes_registry.upload_file_formats
                # Send list of genome builds to the form so the "dbkey" select list can be populated dynamically
                def get_dbkey_options( last_used_build ):
                    for dbkey, build_name in util.dbnames:
                        yield build_name, dbkey, ( dbkey==last_used_build )
                dbkeys = get_dbkey_options( last_used_build )
                # Send list of legitimate roles to the form so the dataset can be associated with 1 or more of them.
                library = trans.sa_session.query( trans.app.model.Library ).get( trans.security.decode_id( library_id ) )
                roles = trans.app.security_agent.get_legitimate_roles( trans, library )
                return trans.fill_template( "/library/common/upload.mako",
                                            upload_option=upload_option,
                                            library_id=library_id,
                                            folder_id=folder_id,
                                            replace_dataset=replace_dataset,
                                            file_formats=file_formats,
                                            dbkeys=dbkeys,
                                            last_used_build=last_used_build,
                                            roles=roles,
                                            history=history,
                                            widgets=[],
                                            msg=msg,
                                            messagetype=messagetype )
    @web.expose
    def download_dataset_from_folder( self, trans, cntrller, id, library_id=None, **kwd ):
        """Catches the dataset id and displays file contents as directed"""
        # id must refer to a LibraryDatasetDatasetAssociation object
        ldda = trans.sa_session.query( trans.app.model.LibraryDatasetDatasetAssociation ).get( id )
        if not ldda.dataset:
            msg = 'Invalid LibraryDatasetDatasetAssociation id %s received for file downlaod' % str( id )
            return trans.response.send_redirect( web.url_for( controller='library_common',
                                                              action='browse_library',
                                                              cntrller=cntrller,
                                                              id=library_id,
                                                              msg=util.sanitize_text( msg ),
                                                              messagetype='error' ) )
        mime = trans.app.datatypes_registry.get_mimetype_by_extension( ldda.extension.lower() )
        trans.response.set_content_type( mime )
        fStat = os.stat( ldda.file_name )
        trans.response.headers[ 'Content-Length' ] = int( fStat.st_size )
        valid_chars = '.,^_-()[]0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        fname = ldda.name
        fname = ''.join( c in valid_chars and c or '_' for c in fname )[ 0:150 ]
        trans.response.headers[ "Content-Disposition" ] = "attachment; filename=GalaxyLibraryDataset-%s-[%s]" % ( str( id ), fname )
        try:
            return open( ldda.file_name )
        except: 
            msg = 'This dataset contains no content'
            return trans.response.send_redirect( web.url_for( controller='library_common',
                                                              action='browse_library',
                                                              cntrller=cntrller,
                                                              id=library_id,
                                                              msg=util.sanitize_text( msg ),
                                                              messagetype='error' ) )
    @web.expose
    def library_dataset_info( self, trans, cntrller, id, library_id, **kwd ):
        params = util.Params( kwd )
        msg = util.restore_text( params.get( 'msg', ''  ) )
        messagetype = params.get( 'messagetype', 'done' )
        library_dataset = trans.sa_session.query( trans.app.model.LibraryDataset ).get( trans.security.decode_id( id ) )
        if not library_dataset:
            msg = "Invalid library dataset specified, id: %s" %str( id )
            return trans.response.send_redirect( web.url_for( controller='library_common',
                                                              action='browse_library',
                                                              cntrller=cntrller,
                                                              id=library_id,
                                                              msg=util.sanitize_text( msg ),
                                                              messagetype='error' ) )
        current_user_roles = trans.get_current_user_roles()
        if params.get( 'edit_attributes_button', False ):
            if cntrller=='library_admin' or trans.app.security_agent.can_modify_library_item( current_user_roles, library_dataset ):
                if params.get( 'edit_attributes_button', False ):
                    old_name = library_dataset.name
                    new_name = util.restore_text( params.get( 'name', '' ) )
                    new_info = util.restore_text( params.get( 'info', '' ) )
                    if not new_name:
                        msg = 'Enter a valid name'
                        messagetype = 'error'
                    else:
                        library_dataset.name = new_name
                        library_dataset.info = new_info
                        trans.sa_session.add( library_dataset )
                        trans.sa_session.flush()
                        msg = "Dataset '%s' has been renamed to '%s'" % ( old_name, new_name )
                        messagetype = 'done'
            else:
                msg = "You are not authorized to change the attributes of this dataset"
                messagetype = "error"
        return trans.fill_template( '/library/common/library_dataset_info.mako',
                                    cntrller=cntrller,
                                    library_dataset=library_dataset,
                                    library_id=library_id,
                                    current_user_roles=current_user_roles,
                                    msg=msg,
                                    messagetype=messagetype )
    @web.expose
    def library_dataset_permissions( self, trans, cntrller, id, library_id, **kwd ):
        params = util.Params( kwd )
        msg = util.restore_text( params.get( 'msg', ''  ) )
        messagetype = params.get( 'messagetype', 'done' )
        library_dataset = trans.sa_session.query( trans.app.model.LibraryDataset ).get( id )
        if not library_dataset:
            msg = "Invalid library dataset specified, id: %s" %str( id )
            return trans.response.send_redirect( web.url_for( controller='library_common',
                                                              action='browse_library',
                                                              cntrller=cntrller,
                                                              id=library_id,
                                                              msg=util.sanitize_text( msg ),
                                                              messagetype='error' ) )
        current_user_roles = trans.get_current_user_roles()
        if params.get( 'update_roles_button', False ):
            if cntrller == 'library_admin' or trans.app.security_agent.can_manage_library_item( current_user_roles, library_dataset ):
                # The user clicked the Save button on the 'Associate With Roles' form
                permissions = {}
                for k, v in trans.app.model.Library.permitted_actions.items():
                    if k != 'LIBRARY_ACCESS':
                        # LIBRARY_ACCESS is a special permission set only at the library level
                        # and it is not inherited.
                        in_roles = [ trans.sa_session.query( trans.app.model.Role ).get( x ) for x in util.listify( kwd.get( k + '_in', [] ) ) ]
                        permissions[ trans.app.security_agent.get_action( v.action ) ] = in_roles
                # Set the LIBRARY permissions on the LibraryDataset
                # NOTE: the LibraryDataset and LibraryDatasetDatasetAssociation will be set with the same permissions
                trans.app.security_agent.set_all_library_permissions( library_dataset, permissions )
                trans.sa_session.refresh( library_dataset )
                # Set the LIBRARY permissions on the LibraryDatasetDatasetAssociation
                trans.app.security_agent.set_all_library_permissions( library_dataset.library_dataset_dataset_association, permissions )
                trans.sa_session.refresh( library_dataset.library_dataset_dataset_association )
                msg = 'Permissions and roles have been updated for library dataset %s' % library_dataset.name
                messagetype = 'done'
            else:
                msg = "You are not authorized to managed the permissions of this dataset"
                messagetype = "error"
        library = trans.sa_session.query( trans.app.model.Library ).get( trans.security.decode_id( library_id ) )
        roles = trans.app.security_agent.get_legitimate_roles( trans, library )
        return trans.fill_template( '/library/common/library_dataset_permissions.mako',
                                    cntrller=cntrller,
                                    library_dataset=library_dataset,
                                    library_id=library_id,
                                    roles=roles,
                                    current_user_roles=current_user_roles,
                                    msg=msg,
                                    messagetype=messagetype )
    @web.expose
    def act_on_multiple_datasets( self, trans, cntrller, library_id, ldda_ids='', **kwd ):
        # This method is used by the select list labeled "Perform action on selected datasets"
        # on the analysis library browser
        params = util.Params( kwd )
        msg = util.restore_text( params.get( 'msg', ''  ) )
        messagetype = params.get( 'messagetype', 'done' )
        if not ldda_ids:
            msg = "You must select at least one dataset"
            return trans.response.send_redirect( web.url_for( controller='library_common',
                                                              action='browse_library',
                                                              cntrller=cntrller,
                                                              id=library_id,
                                                              msg=util.sanitize_text( msg ),
                                                              messagetype='error' ) )
        if not params.do_action:
            msg = "You must select an action to perform on selected datasets"
            return trans.response.send_redirect( web.url_for( controller='library_common',
                                                              action='browse_library',
                                                              cntrller=cntrller,
                                                              id=library_id,
                                                              msg=util.sanitize_text( msg ),
                                                              messagetype='error' ) )
        ldda_ids = util.listify( ldda_ids )
        if params.do_action == 'add':
            history = trans.get_history()
            total_imported_lddas = 0
            msg = ''
            messagetype = 'done'
            for ldda_id in ldda_ids:
                ldda = trans.sa_session.query( trans.app.model.LibraryDatasetDatasetAssociation ).get( trans.security.decode_id( ldda_id ) )
                if ldda.dataset.state in [ 'new', 'upload', 'queued', 'running', 'empty', 'discarded' ]:
                    msg += "Cannot import dataset (%s) since it's state is (%s).  " % ( ldda.name, ldda.dataset.state )
                    messagetype = 'error'
                elif ldda.dataset.state in [ 'ok', 'error' ]:
                    hda = ldda.to_history_dataset_association( target_history=history, add_to_history=True )
                    total_imported_lddas += 1
            if total_imported_lddas:
                trans.sa_session.add( history )
                trans.sa_session.flush()
                msg += "%i dataset(s) have been imported into your history.  " % total_imported_lddas
            return trans.response.send_redirect( web.url_for( controller='library_common',
                                                              action='browse_library',
                                                              cntrller=cntrller,
                                                              id=library_id,
                                                              msg=util.sanitize_text( msg ),
                                                              messagetype=messagetype ) )
        elif params.do_action == 'manage_permissions':
            # We need the folder containing the LibraryDatasetDatasetAssociation(s)
            ldda = trans.sa_session.query( trans.app.model.LibraryDatasetDatasetAssociation ).get( trans.security.decode_id( ldda_ids[0] ) )
            trans.response.send_redirect( web.url_for( controller='library_common',
                                                       action='ldda_permissions',
                                                       cntrller=cntrller,
                                                       library_id=library_id,
                                                       folder_id=trans.security.encode_id( ldda.library_dataset.folder.id ),
                                                       id=",".join( ldda_ids ),
                                                       msg=util.sanitize_text( msg ),
                                                       messagetype=messagetype ) )
        elif params.do_action == 'delete':
            for ldda_id in ldda_ids:
                ldda = trans.sa_session.query( trans.app.model.LibraryDatasetDatasetAssociation ).get( trans.security.decode_id( ldda_id ) )
                ldda.deleted = True
                trans.sa_session.add( ldda )
                trans.sa_session.flush()
            msg = "The selected datasets have been removed from this data library"
            trans.response.send_redirect( web.url_for( controller='library_common',
                                                       action='browse_library',
                                                       cntrller=cntrller,
                                                       id=library_id,
                                                       show_deleted=False,
                                                       msg=util.sanitize_text( msg ),
                                                       messagetype='done' ) )
        else:
            try:
                if params.do_action == 'zip':
                    # Can't use mkstemp - the file must not exist first
                    tmpd = tempfile.mkdtemp()
                    tmpf = os.path.join( tmpd, 'library_download.' + params.do_action )
                    if ziptype == '64':
                        archive = zipfile.ZipFile( tmpf, 'w', zipfile.ZIP_DEFLATED, True )
                    else:
                        archive = zipfile.ZipFile( tmpf, 'w', zipfile.ZIP_DEFLATED )
                    archive.add = lambda x, y: archive.write( x, y.encode('CP437') )
                elif params.do_action == 'tgz':
                    archive = util.streamball.StreamBall( 'w|gz' )
                elif params.do_action == 'tbz':
                    archive = util.streamball.StreamBall( 'w|bz2' )
            except (OSError, zipfile.BadZipFile):
                log.exception( "Unable to create archive for download" )
                msg = "Unable to create archive for download, please report this error"
                return trans.response.send_redirect( web.url_for( controller='library_common',
                                                                  action='browse_library',
                                                                  cntrller=cntrller,
                                                                  id=library_id,
                                                                  msg=util.sanitize_text( msg ),
                                                                  messagetype='error' ) )
            seen = []
            current_user_roles = trans.get_current_user_roles()
            for ldda_id in ldda_ids:
                ldda = trans.sa_session.query( trans.app.model.LibraryDatasetDatasetAssociation ).get( trans.security.decode_id( ldda_id ) )
                if not ldda \
                    or not trans.app.security_agent.can_access_dataset( current_user_roles, ldda.dataset ) \
                    or ldda.dataset.state in [ 'new', 'upload', 'queued', 'running', 'empty', 'discarded' ]:
                    continue
                path = ""
                parent_folder = ldda.library_dataset.folder
                while parent_folder is not None:
                    # Exclude the now-hidden "root folder"
                    if parent_folder.parent is None:
                        path = os.path.join( parent_folder.library_root[0].name, path )
                        break
                    path = os.path.join( parent_folder.name, path )
                    parent_folder = parent_folder.parent
                path += ldda.name
                while path in seen:
                    path += '_'
                seen.append( path )
                try:
                    archive.add( ldda.dataset.file_name, path )
                except IOError:
                    log.exception( "Unable to write to temporary library download archive" )
                    msg = "Unable to create archive for download, please report this error"
                    return trans.response.send_redirect( web.url_for( controller='library_common',
                                                                      action='browse_library',
                                                                      cntrller=cntrller,
                                                                      id=library_id,
                                                                      msg=util.sanitize_text( msg ),
                                                                      messagetype='error' ) )
            if params.do_action == 'zip':
                archive.close()
                tmpfh = open( tmpf )
                # clean up now
                try:
                    os.unlink( tmpf )
                    os.rmdir( tmpd )
                except OSError:
                    log.exception( "Unable to remove temporary library download archive and directory" )
                    msg = "Unable to create archive for download, please report this error"
                    return trans.response.send_redirect( web.url_for( controller='library_common',
                                                                      action='browse_library',
                                                                      cntrller=cntrller,
                                                                      id=library_id,
                                                                      msg=util.sanitize_text( msg ),
                                                                      messagetype='error' ) )
                trans.response.set_content_type( "application/x-zip-compressed" )
                trans.response.headers[ "Content-Disposition" ] = "attachment; filename=GalaxyLibraryFiles.%s" % params.do_action
                return tmpfh
            else:
                trans.response.set_content_type( "application/x-tar" )
                trans.response.headers[ "Content-Disposition" ] = "attachment; filename=GalaxyLibraryFiles.%s" % params.do_action
                archive.wsgi_status = trans.response.wsgi_status()
                archive.wsgi_headeritems = trans.response.wsgi_headeritems()
                return archive.stream
    @web.expose
    def info_template( self, trans, cntrller, library_id, response_action='library_info', id=None, folder_id=None, ldda_id=None, **kwd ):
        # Only adding a new template to a library or folder is currently allowed.  Editing an existing template is
        # a future enhancement.  The response_action param is the name of the method to which this method will redirect
        # if a new template is being added to a library or folder.
        params = util.Params( kwd )
        msg = util.restore_text( params.get( 'msg', ''  ) )
        messagetype = params.get( 'messagetype', 'done' )
        if id:
            library_item = trans.sa_session.query( trans.app.model.FormDefinition ).get( int( id ) )
            library_item_desc = 'information template'
            response_id = id
        elif folder_id:
            library_item = trans.sa_session.query( trans.app.model.LibraryFolder ).get( trans.security.decode_id( folder_id ) )
            library_item_desc = 'folder'
            response_id = folder_id
        elif ldda_id:
            library_item = trans.sa_session.query( trans.app.model.LibraryDatasetDatasetAssociation ).get( trans.security.decode_id( ldda_id ) )
            library_item_desc = 'library dataset'
            response_id = ldda_id
        else:
            library_item = trans.sa_session.query( trans.app.model.Library ).get( trans.security.decode_id( library_id ) )
            library_item_desc = 'library'
            response_id = library_id
        forms = get_all_forms( trans,
                               filter=dict( deleted=False ),
                               form_type=trans.app.model.FormDefinition.types.LIBRARY_INFO_TEMPLATE )
        if not forms:
            msg = "There are no forms on which to base the template, so create a form and "
            msg += "try again to add the information template to the %s." % library_item_desc
            trans.response.send_redirect( web.url_for( controller='forms',
                                                       action='new',
                                                       msg=msg,
                                                       messagetype='done',
                                                       form_type=trans.app.model.FormDefinition.types.LIBRARY_INFO_TEMPLATE ) )
        if params.get( 'add_info_template_button', False ):
            form_id = params.get( 'form_id', None )
            # TODO: add error handling here
            form = trans.sa_session.query( trans.app.model.FormDefinition ).get( int( form_id ) )
            #fields = list( copy.deepcopy( form.fields ) )
            form_values = trans.app.model.FormValues( form, [] )
            trans.sa_session.add( form_values )
            trans.sa_session.flush()
            if folder_id:
                assoc = trans.app.model.LibraryFolderInfoAssociation( library_item, form, form_values )
            elif ldda_id:
                assoc = trans.app.model.LibraryDatasetDatasetInfoAssociation( library_item, form, form_values )
            else:
                assoc = trans.app.model.LibraryInfoAssociation( library_item, form, form_values )
            trans.sa_session.add( assoc )
            trans.sa_session.flush()
            msg = 'An information template based on the form "%s" has been added to this %s.' % ( form.name, library_item_desc )
            trans.response.send_redirect( web.url_for( controller='library_common',
                                                       action=response_action,
                                                       cntrller=cntrller,
                                                       id=response_id,
                                                       library_id=library_id,
                                                       msg=msg,
                                                       messagetype='done' ) )
        return trans.fill_template( '/library/common/select_info_template.mako',
                                    cntrller=cntrller,
                                    library_item_name=library_item.name,
                                    library_item_desc=library_item_desc,
                                    library_id=library_id,
                                    folder_id=folder_id,
                                    ldda_id=ldda_id,
                                    id=response_id,
                                    forms=forms,
                                    msg=msg,
                                    messagetype=messagetype )
    @web.expose
    def edit_template_info( self, trans, cntrller, library_id, response_action, num_widgets, library_item_id=None, library_item_type=None, **kwd ):
        params = util.Params( kwd )
        msg = util.restore_text( params.get( 'msg', ''  ) )
        messagetype = params.get( 'messagetype', 'done' )
        folder_id = None
        if library_item_type == 'library':
            library_item = trans.sa_session.query( trans.app.model.Library ).get( trans.security.decode_id( library_id ) )
            # Make sure library_item_id is encoded if we have a library
            library_item_id = library_id
        elif library_item_type == 'library_dataset':
            library_item = trans.sa_session.query( trans.app.model.LibraryDataset ).get( trans.security.decode_id( library_item_id ) )
        elif library_item_type == 'folder':
            library_item = trans.sa_session.query( trans.app.model.LibraryFolder ).get( trans.security.decode_id( library_item_id ) )
        elif library_item_type == 'library_dataset_dataset_association':
            library_item = trans.sa_session.query( trans.app.model.LibraryDatasetDatasetAssociation ).get( trans.security.decode_id( library_item_id ) )
            # This response_action method requires a folder_id
            folder_id = trans.security.encode_id( library_item.library_dataset.folder.id )
        else:
            msg = "Invalid library item type ( %s ) specified, id ( %s )" % ( str( library_item_type ), str( trans.security.decode_id( library_item_id ) ) )
            return trans.response.send_redirect( web.url_for( controller='library_common',
                                                              action='browse_library',
                                                              cntrller=cntrller,
                                                              id=library_id,
                                                              msg=util.sanitize_text( msg ),
                                                              messagetype='error' ) )
        # Save updated template field contents
        field_contents = []
        for index in range( int( num_widgets ) ):
            field_contents.append( util.restore_text( params.get( 'field_%i' % ( index ), ''  ) ) )
        if field_contents:
            # Since information templates are inherited, the template fields can be displayed on the information
            # page for a folder or library dataset when it has no info_association object.  If the user has added
            # field contents on an inherited template via a parent's info_association, we'll need to create a new
            # form_values and info_association for the current object.  The value for the returned inherited variable
            # is not applicable at this level.
            info_association, inherited = library_item.get_info_association( restrict=True )
            if info_association:
                template = info_association.template
                info = info_association.info
                form_values = trans.sa_session.query( trans.app.model.FormValues ).get( info.id )
                # Update existing content only if it has changed
                if form_values.content != field_contents:
                    form_values.content = field_contents
                    trans.sa_session.add( form_values )
                    trans.sa_session.flush()
            else:
                # Inherit the next available info_association so we can get the template
                info_association, inherited = library_item.get_info_association()
                template = info_association.template
                # Create a new FormValues object
                form_values = trans.app.model.FormValues( template, field_contents )
                trans.sa_session.add( form_values )
                trans.sa_session.flush()
                # Create a new info_association between the current library item and form_values
                if library_item_type == 'folder':
                    info_association = trans.app.model.LibraryFolderInfoAssociation( library_item, template, form_values )
                    trans.sa_session.add( info_association )
                    trans.sa_session.flush()
                elif library_item_type == 'library_dataset_dataset_association':
                    info_association = trans.app.model.LibraryDatasetDatasetInfoAssociation( library_item, template, form_values )
                    trans.sa_session.add( info_association )
                    trans.sa_session.flush()
        msg = 'The information has been updated.'
        return trans.response.send_redirect( web.url_for( controller='library_common',
                                                          action=response_action,
                                                          cntrller=cntrller,
                                                          library_id=library_id,
                                                          folder_id=folder_id,
                                                          id=library_item_id,
                                                          msg=util.sanitize_text( msg ),
                                                          messagetype='done' ) )

# ---- Utility methods -------------------------------------------------------

def active_folders( trans, folder ):
    # Much faster way of retrieving all active sub-folders within a given folder than the
    # performance of the mapper.  This query also eagerloads the permissions on each folder.
    return trans.sa_session.query( trans.app.model.LibraryFolder ) \
                           .filter_by( parent=folder, deleted=False ) \
                           .options( eagerload_all( "actions" ) ) \
                           .order_by( trans.app.model.LibraryFolder.table.c.name ) \
                           .all()
def activatable_folders( trans, folder ):
    return trans.sa_session.query( trans.app.model.LibraryFolder ) \
                           .filter_by( parent=folder, purged=False ) \
                           .options( eagerload_all( "actions" ) ) \
                           .order_by( trans.app.model.LibraryFolder.table.c.name ) \
                           .all()
def active_folders_and_lddas( trans, folder ):
    folders = active_folders( trans, folder )
    # This query is much faster than the folder.active_library_datasets property
    lddas = trans.sa_session.query( trans.app.model.LibraryDatasetDatasetAssociation ) \
                            .filter_by( deleted=False ) \
                            .join( "library_dataset" ) \
                            .filter( trans.app.model.LibraryDataset.table.c.folder_id==folder.id ) \
                            .order_by( trans.app.model.LibraryDatasetDatasetAssociation.table.c.name ) \
                            .all()
    return folders, lddas
def activatable_folders_and_lddas( trans, folder ):
    folders = activatable_folders( trans, folder )
    # This query is much faster than the folder.activatable_library_datasets property
    lddas = trans.sa_session.query( trans.app.model.LibraryDatasetDatasetAssociation ) \
                            .join( "library_dataset" ) \
                            .filter( trans.app.model.LibraryDataset.table.c.folder_id==folder.id ) \
                            .join( "dataset" ) \
                            .filter( trans.app.model.Dataset.table.c.deleted==False ) \
                            .order_by( trans.app.model.LibraryDatasetDatasetAssociation.table.c.name ) \
                            .all()
    return folders, lddas
