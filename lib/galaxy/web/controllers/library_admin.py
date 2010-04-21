import sys
from galaxy import model, util
from galaxy.web.base.controller import *
from galaxy.web.framework.helpers import time_ago, iff, grids
from galaxy.model.orm import *
# Older py compatibility
try:
    set()
except:
    from sets import Set as set

import logging
log = logging.getLogger( __name__ )

class LibraryListGrid( grids.Grid ):
    class NameColumn( grids.TextColumn ):
        def get_value( self, trans, grid, library ):
            return library.name
    class DescriptionColumn( grids.TextColumn ):
        def get_value( self, trans, grid, library ):
            if library.description:
                return library.description
            return ''
    class StatusColumn( grids.GridColumn ):
        def get_value( self, trans, grid, library ):
            if library.purged:
                return "purged"
            elif library.deleted:
                return "deleted"
            return ""
    # Grid definition
    title = "Data Libraries"
    model_class = model.Library
    template='/admin/library/grid.mako'
    default_sort_key = "name"
    columns = [
        NameColumn( "Name",
                    key="name",
                    model_class=model.Library,
                    link=( lambda library: dict( operation="browse", id=library.id ) ),
                    attach_popup=False,
                    filterable="advanced" ),
        DescriptionColumn( "Description",
                           key="description",
                           model_class=model.Library,
                           attach_popup=False,
                           filterable="advanced" ),
        grids.GridColumn( "Created", key="create_time", format=time_ago ),
        grids.GridColumn( "Last Updated", key="update_time", format=time_ago ),
        StatusColumn( "Status", attach_popup=False ),
        # Columns that are valid for filtering but are not visible.
        grids.DeletedColumn( "Deleted", key="deleted", visible=False, filterable="advanced" )
    ]
    columns.append( grids.MulticolFilterColumn( "Search", 
                                                cols_to_filter=[ columns[0], columns[1] ], 
                                                key="free-text-search",
                                                visible=False,
                                                filterable="standard" ) )
    global_actions = [
        grids.GridAction( "Create new data library", dict( controller='library_admin', action='create_library' ) )
    ]
    standard_filters = [
        grids.GridColumnFilter( "Active", args=dict( deleted=False ) ),
        grids.GridColumnFilter( "Deleted", args=dict( deleted=True, purged=False ) ),
        grids.GridColumnFilter( "Purged", args=dict( purged=True ) ),
        grids.GridColumnFilter( "All", args=dict( deleted='All' ) )
    ]
    default_filter = dict( name="All", description="All", deleted="False", purged="False" )
    num_rows_per_page = 50
    preserve_state = False
    use_paging = True
    def build_initial_query( self, session ):
        return session.query( self.model_class )

class LibraryAdmin( BaseController ):

    library_list_grid = LibraryListGrid()

    @web.expose
    @web.require_admin
    def browse_libraries( self, trans, **kwargs ):
        if 'operation' in kwargs:
            operation = kwargs['operation'].lower()
            if operation == "browse":
                return trans.response.send_redirect( web.url_for( controller='library_common',
                                                                  action='browse_library',
                                                                  cntrller='library_admin',
                                                                  **kwargs ) )
        # Render the list view
        return self.library_list_grid( trans, **kwargs )
    @web.expose
    @web.require_admin
    def create_library( self, trans, **kwd ):
        params = util.Params( kwd )
        message = util.restore_text( params.get( 'message', ''  ) )
        status = params.get( 'status', 'done' )
        if params.get( 'create_library_button', False ):
            name = util.restore_text( params.get( 'name', 'No name' ) )
            description = util.restore_text( params.get( 'description', '' ) )
            synopsis = util.restore_text( params.get( 'synopsis', '' ) )
            if synopsis in [ 'None', None ]:
                synopsis = ''
            library = trans.app.model.Library( name=name, description=description, synopsis=synopsis )
            root_folder = trans.app.model.LibraryFolder( name=name, description='' )
            library.root_folder = root_folder
            trans.sa_session.add_all( ( library, root_folder ) )
            trans.sa_session.flush()
            message = "The new library named '%s' has been created" % library.name
            return trans.response.send_redirect( web.url_for( controller='library_common',
                                                              action='browse_library',
                                                              cntrller='library_admin',
                                                              id=trans.security.encode_id( library.id ),
                                                              message=util.sanitize_text( message ),
                                                              status='done' ) )
        return trans.fill_template( '/admin/library/new_library.mako', message=message, status=status )
    @web.expose
    @web.require_admin
    def purge_library( self, trans, **kwd ):
        # TODO: change this function to purge_library_item, behaving similar to delete_library_item
        # assuming we want the ability to purge libraries.
        # This function is currently only used by the functional tests.
        params = util.Params( kwd )
        library = trans.sa_session.query( trans.app.model.Library ).get( trans.security.decode_id( params.id ) )
        def purge_folder( library_folder ):
            for lf in library_folder.folders:
                purge_folder( lf )
            trans.sa_session.refresh( library_folder )
            for library_dataset in library_folder.datasets:
                trans.sa_session.refresh( library_dataset )
                ldda = library_dataset.library_dataset_dataset_association
                if ldda:
                    trans.sa_session.refresh( ldda )
                    dataset = ldda.dataset
                    trans.sa_session.refresh( dataset )
                    # If the dataset is not associated with any additional undeleted folders, then we can delete it.
                    # We don't set dataset.purged to True here because the cleanup_datasets script will do that for
                    # us, as well as removing the file from disk.
                    #if not dataset.deleted and len( dataset.active_library_associations ) <= 1: # This is our current ldda
                    dataset.deleted = True
                    ldda.deleted = True
                    trans.sa_session.add_all( ( dataset, ldda ) )
                library_dataset.deleted = True
                trans.sa_session.add( library_dataset )
            library_folder.deleted = True
            library_folder.purged = True
            trans.sa_session.add( library_folder )
            trans.sa_session.flush()
        if not library.deleted:
            message = "Library '%s' has not been marked deleted, so it cannot be purged" % ( library.name )
            return trans.response.send_redirect( web.url_for( controller='library_admin',
                                                              action='browse_libraries',
                                                              message=util.sanitize_text( message ),
                                                              status='error' ) )
        else:
            purge_folder( library.root_folder )
            library.purged = True
            trans.sa_session.add( library )
            trans.sa_session.flush()
            message = "Library '%s' and all of its contents have been purged, datasets will be removed from disk via the cleanup_datasets script" % library.name
            return trans.response.send_redirect( web.url_for( controller='library_admin',
                                                              action='browse_libraries',
                                                              message=util.sanitize_text( message ),
                                                              status='done' ) )   
