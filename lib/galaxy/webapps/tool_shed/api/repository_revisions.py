import datetime
import logging
from galaxy.web.framework.helpers import time_ago
from tool_shed.util import metadata_util
from galaxy import web
from galaxy import util
from galaxy.model.orm import and_, not_, select
from galaxy.web.base.controller import BaseAPIController, HTTPBadRequest
from tool_shed.util import export_util
import tool_shed.util.shed_util_common as suc

from galaxy import eggs
eggs.require( 'mercurial' )

from mercurial import hg

log = logging.getLogger( __name__ )


class RepositoryRevisionsController( BaseAPIController ):
    """RESTful controller for interactions with tool shed repository revisions."""

    @web.expose_api_anonymous
    def export( self, trans, payload, **kwd ):
        """
        POST /api/repository_revisions/export
        Creates and saves a gzip compressed tar archive of a repository and optionally all of it's repository dependencies.

        The following parameters are included in the payload.
        :param tool_shed_url (required): the base URL of the Tool Shed from which the Repository was installed
        :param name (required): the name of the Repository
        :param owner (required): the owner of the Repository
        :param changset_revision (required): the changset_revision of the RepositoryMetadata object associated with the Repository
        :param export_repository_dependencies (optional): whether to export repository dependencies - defaults to False
        :param download_dir (optional): the local directory to which to download the archive - defaults to /tmp
        """
        tool_shed_url = payload.get( 'tool_shed_url', '' )
        if not tool_shed_url:
            raise HTTPBadRequest( detail="Missing required parameter 'tool_shed_url'." )
        tool_shed_url = tool_shed_url.rstrip( '/' )
        name = payload.get( 'name', '' )
        if not name:
            raise HTTPBadRequest( detail="Missing required parameter 'name'." )
        owner = payload.get( 'owner', '' )
        if not owner:
            raise HTTPBadRequest( detail="Missing required parameter 'owner'." )
        changeset_revision = payload.get( 'changeset_revision', '' )
        if not changeset_revision:
            raise HTTPBadRequest( detail="Missing required parameter 'changeset_revision'." )
        export_repository_dependencies = payload.get( 'export_repository_dependencies', False )
        try:
            # We'll currently support only gzip-compressed tar archives.
            file_type = 'gz'
            export_repository_dependencies = util.string_as_bool( export_repository_dependencies )
            # Get the repository information.
            repository = suc.get_repository_by_name_and_owner( trans.app, name, owner )
            repository_id = trans.security.encode_id( repository.id )
            response = export_util.export_repository( trans,
                                                      tool_shed_url,
                                                      repository_id,
                                                      str( repository.name ),
                                                      changeset_revision,
                                                      file_type,
                                                      export_repository_dependencies,
                                                      api=True )
            return response
        except Exception, e:
            message = "Error in the Tool Shed repository_revisions API in export: %s" % str( e )
            log.error( message, exc_info=True )
            trans.response.status = 500
            return message

    @web.expose_api_anonymous
    def repository_dependencies( self, trans, id, **kwd ):
        """
        GET /api/repository_revisions/{encoded repository_metadata id}/repository_dependencies
        Displays information about a repository_metadata record in the Tool Shed.

        :param id: the encoded id of the `RepositoryMetadata` object
        """
        # Example URL: http://localhost:9009/api/repository_revisions/repository_dependencies/bb125606ff9ea620
        value_mapper = { 'id' : trans.security.encode_id,
                         'user_id' : trans.security.encode_id }
        repository_dependencies_dicts = []
        try:
            repository_metadata = metadata_util.get_repository_metadata_by_id( trans, id )
            metadata = repository_metadata.metadata
            if metadata and 'repository_dependencies' in metadata:
                rd_tups = metadata[ 'repository_dependencies' ][ 'repository_dependencies' ]
                for rd_tup in rd_tups:
                    tool_shed, name, owner, changeset_revision = rd_tup[ 0:4 ]
                    repository_dependency = suc.get_repository_by_name_and_owner( trans.app, name, owner )
                    repository_dependency_dict = repository_dependency.to_dict( view='element', value_mapper=value_mapper )
                    # We have to add the changeset_revision of of the repository dependency.
                    repository_dependency_dict[ 'changeset_revision' ] = changeset_revision
                    repository_dependency_dict[ 'url' ] = web.url_for( controller='repositories',
                                                                       action='show',
                                                                       id=trans.security.encode_id( repository_dependency.id ) )
                    repository_dependencies_dicts.append( repository_dependency_dict )
            return repository_dependencies_dicts
        except Exception, e:
            message = "Error in the Tool Shed repository_revisions API in repository_dependencies: %s" % str( e )
            log.error( message, exc_info=True )
            trans.response.status = 500
            return message

    @web.expose_api_anonymous
    def index( self, trans, **kwd ):
        """
        GET /api/repository_revisions
        Displays a collection (list) of repository revisions.
        """
        # Example URL: http://localhost:9009/api/repository_revisions
        repository_metadata_dicts = []
        # Build up an anded clause list of filters.
        clause_list = []
        # Filter by downloadable if received.
        downloadable =  kwd.get( 'downloadable', None )
        if downloadable is not None:
            clause_list.append( trans.model.RepositoryMetadata.table.c.downloadable == util.string_as_bool( downloadable ) )
        # Filter by malicious if received.
        malicious =  kwd.get( 'malicious', None )
        if malicious is not None:
            clause_list.append( trans.model.RepositoryMetadata.table.c.malicious == util.string_as_bool( malicious ) )
        # Filter by tools_functionally_correct if received.
        tools_functionally_correct = kwd.get( 'tools_functionally_correct', None )
        if tools_functionally_correct is not None:
            clause_list.append( trans.model.RepositoryMetadata.table.c.tools_functionally_correct == util.string_as_bool( tools_functionally_correct ) )
        # Filter by missing_test_components if received.
        missing_test_components = kwd.get( 'missing_test_components', None )
        if missing_test_components is not None:
            clause_list.append( trans.model.RepositoryMetadata.table.c.missing_test_components == util.string_as_bool( missing_test_components ) )
        # Filter by do_not_test if received.
        do_not_test = kwd.get( 'do_not_test', None )
        if do_not_test is not None:
            clause_list.append( trans.model.RepositoryMetadata.table.c.do_not_test == util.string_as_bool( do_not_test ) )
        # Filter by includes_tools if received.
        includes_tools = kwd.get( 'includes_tools', None )
        if includes_tools is not None:
            clause_list.append( trans.model.RepositoryMetadata.table.c.includes_tools == util.string_as_bool( includes_tools ) )
        # Filter by test_install_error if received.
        test_install_error = kwd.get( 'test_install_error', None )
        if test_install_error is not None:
            clause_list.append( trans.model.RepositoryMetadata.table.c.test_install_error == util.string_as_bool( test_install_error ) )
        # Filter by skip_tool_test if received.
        skip_tool_test = kwd.get( 'skip_tool_test', None )
        if skip_tool_test is not None:
            skip_tool_test = util.string_as_bool( skip_tool_test )
            skipped_metadata_ids_subquery = select( [ trans.app.model.SkipToolTest.table.c.repository_metadata_id ] )
            if skip_tool_test:
                clause_list.append( trans.model.RepositoryMetadata.id.in_( skipped_metadata_ids_subquery ) )
            else:
                clause_list.append( not_( trans.model.RepositoryMetadata.id.in_( skipped_metadata_ids_subquery ) ) )
        # Generate and execute the query.
        try:
            query = trans.sa_session.query( trans.app.model.RepositoryMetadata ) \
                                    .filter( and_( *clause_list ) ) \
                                    .order_by( trans.app.model.RepositoryMetadata.table.c.repository_id ) \
                                    .all()
            for repository_metadata in query:
                repository_metadata_dict = repository_metadata.to_dict( view='collection',
                                                                        value_mapper=self.__get_value_mapper( trans, repository_metadata ) )
                repository_metadata_dict[ 'url' ] = web.url_for( controller='repository_revisions',
                                                                 action='show',
                                                                 id=trans.security.encode_id( repository_metadata.id ) )
                repository_metadata_dicts.append( repository_metadata_dict )
            return repository_metadata_dicts
        except Exception, e:
            message = "Error in the Tool Shed repository_revisions API in index: " + str( e )
            log.error( message, exc_info=True )
            trans.response.status = 500
            return message

    @web.expose_api_anonymous
    def show( self, trans, id, **kwd ):
        """
        GET /api/repository_revisions/{encoded_repository_metadata_id}
        Displays information about a repository_metadata record in the Tool Shed.

        :param id: the encoded id of the `RepositoryMetadata` object
        """
        # Example URL: http://localhost:9009/api/repository_revisions/bb125606ff9ea620
        try:
            repository_metadata = metadata_util.get_repository_metadata_by_id( trans, id )
            repository_metadata_dict = repository_metadata.to_dict( view='element',
                                                                    value_mapper=self.__get_value_mapper( trans, repository_metadata ) )
            repository_metadata_dict[ 'url' ] = web.url_for( controller='repository_revisions',
                                                             action='show',
                                                             id=trans.security.encode_id( repository_metadata.id ) )
            return repository_metadata_dict
        except Exception, e:
            message = "Error in the Tool Shed repository_revisions API in show: %s" % str( e )
            log.error( message, exc_info=True )
            trans.response.status = 500
            return message

    @web.expose_api
    def update( self, trans, payload, **kwd ):
        """
        PUT /api/repository_revisions/{encoded_repository_metadata_id}/{payload}
        Updates the value of specified columns of the repository_metadata table based on the key / value pairs in payload.
        """
        repository_metadata_id = kwd.get( 'id', None )
        try:
            repository_metadata = metadata_util.get_repository_metadata_by_id( trans, repository_metadata_id )
            flush_needed = False
            for key, new_value in payload.items():
                if key == 'time_last_tested':
                    repository_metadata.time_last_tested = datetime.datetime.utcnow()
                    flush_needed = True
                elif hasattr( repository_metadata, key ):
                    setattr( repository_metadata, key, new_value )
                    flush_needed = True
            if flush_needed:
                trans.sa_session.add( repository_metadata )
                trans.sa_session.flush()
        except Exception, e:
            message = "Error in the Tool Shed repository_revisions API in update: %s" % str( e )
            log.error( message, exc_info=True )
            trans.response.status = 500
            return message
        repository_metadata_dict = repository_metadata.to_dict( view='element',
                                                                value_mapper=self.__get_value_mapper( trans, repository_metadata ) )
        repository_metadata_dict[ 'url' ] = web.url_for( controller='repository_revisions',
                                                         action='show',
                                                         id=trans.security.encode_id( repository_metadata.id ) )
        return repository_metadata_dict

    def __get_value_mapper( self, trans, repository_metadata ):
        value_mapper = { 'id' : trans.security.encode_id,
                         'repository_id' : trans.security.encode_id }
        if repository_metadata.time_last_tested is not None:
            # For some reason the Dictifiable.to_dict() method in ~/galaxy/model/item_attrs.py requires
            # a function rather than a mapped value, so just pass the time_ago function here.
            value_mapper[ 'time_last_tested' ] = time_ago
        return value_mapper
