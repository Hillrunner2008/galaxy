#!/usr/bin/env python
"""
Fetch jobs using gops_intersect, gops_merge, gops_subtract, gops_complement, gops_coverage 
wherein the second dataset doesn't have chr, start and end in standard columns 1, 2 and 3.
"""

from galaxy import eggs
import sys, os, ConfigParser
import galaxy.app
import galaxy.model.mapping
import pkg_resources
        
pkg_resources.require( "SQLAlchemy >= 0.4" )
import sqlalchemy as sa

assert sys.version_info[:2] >= ( 2, 4 )

class TestApplication( object ):
    """Encapsulates the state of a Universe application"""
    def __init__( self, database_connection=None, file_path=None ):
        print >> sys.stderr, "python path is: " + ", ".join( sys.path )
        if database_connection is None:
            raise Exception( "CleanupDatasetsApplication requires a database_connection value" )
        if file_path is None:
            raise Exception( "CleanupDatasetsApplication requires a file_path value" )
        self.database_connection = database_connection
        self.file_path = file_path
        # Setup the database engine and ORM
        self.model = galaxy.model.mapping.init( self.file_path, self.database_connection, engine_options={}, create_tables=False )

def main():
    ini_file = sys.argv[1]
    conf_parser = ConfigParser.ConfigParser( {'here':os.getcwd()} )
    conf_parser.read( ini_file )
    configuration = {}
    for key, value in conf_parser.items( "app:main" ):
        configuration[key] = value
    database_connection = configuration['database_connection']
    file_path = configuration['file_path']
    app = TestApplication( database_connection=database_connection, file_path=file_path )
    jobs = {}
    try:
        for job in app.model.Job.filter( sa.and_( app.model.Job.table.c.create_time.between( '2008-05-23', '2008-11-29' ),
                                                  app.model.Job.table.c.state == 'ok',
                                                  sa.or_( app.model.Job.table.c.tool_id == 'gops_intersect_1',
                                                          app.model.Job.table.c.tool_id == 'gops_subtract_1',
                                                          app.model.Job.table.c.tool_id == 'gops_merge_1',
                                                          app.model.Job.table.c.tool_id == 'gops_coverage_1',
                                                          app.model.Job.table.c.tool_id == 'gops_complement_1',
                                                        ),
                                                  sa.not_( app.model.Job.table.c.command_line.like( '%-2 1,2,3%' ) )
                                                )
                                        ).all():
            print "# processing job id %s" % str( job.id )
            for jtoda in job.output_datasets:
                print "# --> processing JobToOutputDatasetAssociation id %s" % str( jtoda.id )
                hda = app.model.HistoryDatasetAssociation.get( jtoda.dataset_id )
                print "# ----> processing HistoryDatasetAssociation id %s" % str( hda.id )
                if not hda.deleted:
                    # Probably don't need this check, since the job state should suffice, but...
                    if hda.dataset.state == 'ok':
                        history = app.model.History.get( hda.history_id )
                        print "# ------> processing history id %s" % str( history.id )
                        if history.user_id:
                            user = app.model.User.get( history.user_id )
                            jobs[ job.id ] = {}
                            jobs[ job.id ][ 'hda_id' ] = hda.id
                            jobs[ job.id ][ 'hda_name' ] = hda.name
                            jobs[ job.id ][ 'hda_info' ] = hda.info
                            jobs[ job.id ][ 'history_id' ] = history.id 
                            jobs[ job.id ][ 'history_name' ] = history.name 
                            jobs[ job.id ][ 'history_update_time' ] = history.update_time
                            jobs[ job.id ][ 'user_email' ] = user.email
    except Exception, e:
        print "# caught exception: %s" % str( e )
    
    print "\n\n# Number of incorrect Jobs: %d\n\n" % ( len( jobs ) )
    print "#job_id\thda_id\thda_name\thda_info\thistory_id\thistory_name\thistory_update_time\tuser_email"
    for jid in jobs:
        print "%s\t%s\t%s\t%s\t%s\t%s\t%s" % \
            ( jid, jobs[ jid ][ 'hda_id' ], 
              jobs[ jid ][ 'hda_name' ], 
              jobs[ jid ][ 'hda_info' ],
              jobs[ jid ][ 'history_id' ],
              jobs[ jid ][ 'history_name' ],
              jobs[ jid ][ 'history_update_time' ],
              jobs[ jid ][ 'user_email' ]
            )
    sys.exit(0)

if __name__ == "__main__":
    main()
