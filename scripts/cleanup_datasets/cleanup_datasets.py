#!/usr/bin/env python

import sys, os, time, ConfigParser
from datetime import datetime, timedelta
from time import strftime
from optparse import OptionParser

new_path = [ os.path.join( os.getcwd(), "lib" ) ]
new_path.extend( sys.path[1:] ) # remove scripts/ from the path
sys.path = new_path

from galaxy import eggs
import galaxy.model.mapping
import pkg_resources
        
pkg_resources.require( "SQLAlchemy >= 0.4" )
from sqlalchemy.orm import eagerload

assert sys.version_info[:2] >= ( 2, 4 )

def main():
    parser = OptionParser()
    parser.add_option( "-d", "--days", dest="days", action="store", type="int", help="number of days (60)", default=60 )
    parser.add_option( "-r", "--remove_from_disk", action="store_true", dest="remove_from_disk", help="remove datasets from disk when purged", default=False )
    parser.add_option( "-1", "--info_delete_userless_histories", action="store_true", dest="info_delete_userless_histories", default=False, help="info about the histories and datasets that will be affected by delete_userless_histories()" )
    parser.add_option( "-2", "--delete_userless_histories", action="store_true", dest="delete_userless_histories", default=False, help="delete userless histories and datasets" )
    parser.add_option( "-3", "--info_purge_histories", action="store_true", dest="info_purge_histories", default=False, help="info about histories and datasets that will be affected by purge_histories()" )
    parser.add_option( "-4", "--purge_histories", action="store_true", dest="purge_histories", default=False, help="purge deleted histories" )
    parser.add_option( "-5", "--info_purge_datasets", action="store_true", dest="info_purge_datasets", default=False, help="info about the datasets that will be affected by purge_datasets()" )
    parser.add_option( "-6", "--purge_datasets", action="store_true", dest="purge_datasets", default=False, help="purge deleted datasets" )
    ( options, args ) = parser.parse_args()
    ini_file = args[0]
    
    if not ( options.info_delete_userless_histories ^ options.delete_userless_histories ^ \
             options.info_purge_histories ^ options.purge_histories ^ \
             options.info_purge_datasets ^ options.purge_datasets ):
        parser.print_help()
        sys.exit(0)
    
    conf_parser = ConfigParser.ConfigParser( {'here':os.getcwd()} )
    conf_parser.read( ini_file )
    configuration = {}
    for key, value in conf_parser.items( "app:main" ):
        configuration[key] = value
    database_connection = configuration['database_connection']
    file_path = configuration['file_path']
    app = CleanupDatasetsApplication( database_connection=database_connection, file_path=file_path )
    h = app.model.History
    d = app.model.Dataset
    m = app.model.MetadataFile
    cutoff_time = datetime.utcnow() - timedelta( days=options.days )
    now = strftime( "%Y-%m-%d %H:%M:%S" )

    print "\n# %s - Handling stuff older than %i days\n" % ( now, options.days )

    if options.info_delete_userless_histories:
        info_delete_userless_histories( h, cutoff_time )
    elif options.delete_userless_histories:
        delete_userless_histories( h, d, cutoff_time )
    if options.info_purge_histories:
        info_purge_histories( h, d, cutoff_time )
    elif options.purge_histories:
        if options.remove_from_disk:
            print "# Datasets will be removed from disk...\n"
        else:
            print "# Datasets will NOT be removed from disk...\n"
        purge_histories( h, d, m, cutoff_time, options.remove_from_disk )
    elif options.info_purge_datasets:
        info_purge_datasets( d, cutoff_time )
    elif options.purge_datasets:
        if options.remove_from_disk:
            print "# Datasets will be removed from disk...\n"
        else:
            print "# Datasets will NOT be removed from disk...\n"
        purge_datasets( d, m, cutoff_time, options.remove_from_disk )
    sys.exit(0)

def info_delete_userless_histories( h, cutoff_time ):
    # Provide info about the histories and datasets that will be affected if the delete_userless_histories function is executed.
    history_count = 0
    dataset_count = 0
    where = ( h.table.c.user_id==None ) & ( h.table.c.deleted==False ) & ( h.table.c.update_time < cutoff_time )
    histories = h.query().filter( where ).options( eagerload( 'active_datasets' ) ).all()

    print '# The following datasets and associated userless histories will be deleted'
    start = time.clock()
    for history in histories:
        for dataset_assoc in history.active_datasets:
            if not dataset_assoc.deleted:
                # This check is not necessary since 'active_datasets' are not
                # deleted, but just being cautious
                print "dataset_%d" %dataset_assoc.dataset_id
                dataset_count += 1
        print "%d" % history.id
        history_count += 1
    stop = time.clock()
    print "# %d histories ( including a total of %d datasets ) will be deleted\n" %( history_count, dataset_count )
    print "Elapsed time: ", stop - start, "\n"

def delete_userless_histories( h, d, cutoff_time ):
    # Deletes userless histories whose update_time value is older than the cutoff_time.
    # The datasets associated with each history are also deleted.  Nothing is removed from disk.
    history_count = 0
    dataset_count = 0
    h_where = ( h.table.c.user_id==None ) & ( h.table.c.deleted==False ) & ( h.table.c.update_time < cutoff_time )

    print '# The following datasets and associated userless histories have been deleted'
    start = time.clock()
    histories = h.query().filter( h_where ).options( eagerload( 'active_datasets' ) ).all()
    for history in histories:
        for dataset_assoc in history.active_datasets:
            if not dataset_assoc.deleted:
                # Mark all datasets as deleted
                d_where = ( d.table.c.id==dataset_assoc.dataset_id )
                datasets = d.query().filter( d_where ).all()
                for dataset in datasets:
                    if not dataset.deleted:
                        dataset.deleted = True
                        dataset.flush()
                # Mark the history_dataset_association as deleted
                dataset_assoc.deleted = True
                dataset_assoc.clear_associated_files()
                dataset_assoc.flush()
                print "dataset_%d" % dataset_assoc.dataset_id
                dataset_count += 1
        history.deleted = True
        history.flush()
        print "%d" % history.id
        history_count += 1
    stop = time.clock()
    print "# Deleted %d histories ( including a total of %d datasets )\n" %( history_count, dataset_count )
    print "Elapsed time: ", stop - start, "\n"
    
def info_purge_histories( h, d, cutoff_time ):
    # Provide info about the histories and datasets that will be affected if the purge_histories function is executed.
    history_count = 0
    dataset_count = 0
    disk_space = 0
    h_where = ( h.table.c.deleted==True ) & ( h.table.c.purged==False ) & ( h.table.c.update_time < cutoff_time )

    print '# The following datasets and associated deleted histories will be purged'
    start = time.clock()
    histories = h.query().filter( h_where ).options( eagerload( 'datasets' ) ).all()
    for history in histories:
        for dataset_assoc in history.datasets:
            # Datasets can only be purged if their HistoryDatasetAssociation has been deleted.
            if dataset_assoc.deleted:
                d_where = ( d.table.c.id==dataset_assoc.dataset_id )
                datasets = d.query().filter( d_where ).all()
                for dataset in datasets:
                    if dataset.purgable and not dataset.purged:
                        print "%s" % dataset.file_name
                        dataset_count += 1
                        try:
                            disk_space += dataset.file_size
                        except:
                            pass
        print "%d" % history.id
        history_count += 1
    stop = time.clock()
    print '# %d histories ( including a total of %d datasets ) will be purged.  Freed disk space: ' %( history_count, dataset_count ), disk_space, '\n'
    print "Elapsed time: ", stop - start, "\n"

def purge_histories( h, d, m, cutoff_time, remove_from_disk ):
    # Purges deleted histories whose update_time is older than the cutoff_time.
    # The datasets associated with each history are also purged.
    history_count = 0
    dataset_count = 0
    disk_space = 0
    file_size = 0
    errors = False
    h_where = ( h.table.c.deleted==True ) & ( h.table.c.purged==False ) & ( h.table.c.update_time < cutoff_time )

    print '# The following datasets and associated deleted histories have been purged'
    start = time.clock()
    histories = h.query().filter( h_where ).options( eagerload( 'datasets' ) ).all()    
    for history in histories:
        errors = False
        for dataset_assoc in history.datasets:
            if dataset_assoc.deleted:
                d_where = ( d.table.c.id==dataset_assoc.dataset_id )
                datasets = d.query().filter( d_where ).all()
                for dataset in datasets:
                    if dataset.purgable and not dataset.purged:
                        file_size = dataset.file_size
                        dataset.deleted = True
                        dataset.file_size = 0
                        if remove_from_disk:
                            dataset.flush()
                            errmsg = purge_dataset( dataset, d, m )
                            if errmsg:
                                errors = True
                                print errmsg
                        else:
                            dataset.purged = True
                            dataset.flush()
                            print "%s" % dataset.file_name
                            # Mark all associated MetadataFiles as deleted and purged
                            print "The following metadata files associated with dataset '%s' have been marked purged" % dataset.file_name
                            for hda in dataset.history_associations:
                                for metadata_file in m.filter( m.table.c.hda_id==hda.id ).all():
                                    metadata_file.deleted = True
                                    metadata_file.purged = True
                                    metadata_file.flush()
                                    print "%s" % metadata_file.file_name()
                            for lda in dataset.library_associations:
                                for metadata_file in m.filter( m.table.c.lda_id==lda.id ).all():
                                    metadata_file.deleted = True
                                    metadata_file.purged = True
                                    metadata_file.flush()
                                    print "%s" % metadata_file.file_name()
                        dataset_count += 1
                        try:
                            disk_space += file_size
                        except:
                            pass
        if not errors:
            history.purged = True
            history.flush()
            print "%d" % history.id
            history_count += 1
    stop = time.clock()
    print '# Purged %d histories ( including a total of %d datasets ).  Freed disk space: ' %( history_count, dataset_count ), disk_space, '\n'
    print "Elapsed time: ", stop - start, "\n"

def info_purge_datasets( d, cutoff_time ):
    # Provide info about the datasets that will be affected if the purge_datasets function is executed.
    dataset_count = 0
    disk_space = 0
    where = ( d.table.c.deleted==True ) & ( d.table.c.purgable==True ) & ( d.table.c.purged==False ) & ( d.table.c.update_time < cutoff_time )

    print '# The following deleted datasets will be purged'    
    start = time.clock()
    datasets = d.query().filter( where ).all()
    for dataset in datasets:
        print "%s" % dataset.file_name
        dataset_count += 1
        try:
            disk_space += dataset.file_size
        except:
            pass
    stop = time.clock()
    print '# %d datasets will be purged.  Freed disk space: ' %dataset_count, disk_space, '\n'
    print "Elapsed time: ", stop - start, "\n"

def purge_datasets( d, m, cutoff_time, remove_from_disk ):
    # Purges deleted datasets whose update_time is older than cutoff_time.  Files may or may
    # not be removed from disk.
    dataset_count = 0
    disk_space = 0
    file_size = 0
    where = ( d.table.c.deleted==True ) & ( d.table.c.purgable==True ) & ( d.table.c.purged==False ) & ( d.table.c.update_time < cutoff_time )

    print '# The following deleted datasets have been purged'
    start = time.clock()
    datasets = d.query().filter( where ).all()
    for dataset in datasets:
        file_size = dataset.file_size
        if remove_from_disk:
            errmsg = purge_dataset( dataset, d, m )
            if errmsg:
               print errmsg
            else:
                dataset_count += 1
        else:
            dataset.purged = True
            dataset.file_size = 0
            dataset.flush()
            print "%s" % dataset.file_name
            # Mark all associated MetadataFiles as deleted and purged
            print "The following metadata files associated with dataset '%s' have been marked purged" % dataset.file_name
            for hda in dataset.history_associations:
                for metadata_file in m.filter( m.table.c.hda_id==hda.id ).all():
                    metadata_file.deleted = True
                    metadata_file.purged = True
                    metadata_file.flush()
                    print "%s" % metadata_file.file_name()
            for lda in dataset.library_associations:
                for metadata_file in m.filter( m.table.c.lda_id==lda.id ).all():
                    metadata_file.deleted = True
                    metadata_file.purged = True
                    metadata_file.flush()
                    print "%s" % metadata_file.file_name()
            dataset_count += 1
        try:
            disk_space += file_size
        except:
            pass
    stop = time.clock()
    print '# %d datasets purged\n' % dataset_count
    if remove_from_disk:
        print '# Freed disk space: ', disk_space, '\n'
    print "Elapsed time: ", stop - start, "\n"

def purge_dataset( dataset, d, m ):
    # Removes the file from disk and updates the database accordingly.
    if dataset.deleted:
        purgable = True
        # Remove files from disk and update the database
        try:
            # See if the dataset has been shared
            if dataset.external_filename:
                # This check handles the pre-history_dataset_association approach to sharing.
                shared_data = d.filter( and_( d.table.c.external_filename==dataset.external_filename, d.table.c.deleted==False ) ).all()
                if shared_data:
                    purgable = False
            if purgable:
                # This check handles the history_dataset_association approach to sharing.
                for shared_data in dataset.history_associations:
                    # Check to see if another dataset is using this file.  This happens when a user shares 
                    # their history with another user.  In this case, a new record is created in the dataset
                    # table for each dataset, but the dataset records point to the same data file on disk.  So
                    # if 1 of the 2 users deletes the dataset from their history but the other doesn't, we need
                    # to keep the dataset on disk for the 2nd user.
                    if not shared_data.deleted:
                        purgable = False
                        break
            if purgable:
                dataset.purged = True
                dataset.file_size = 0
                dataset.flush()
                # Remove dataset file from disk
                os.unlink( dataset.file_name )
                print "%s" % dataset.file_name
                # Mark all associated MetadataFiles as deleted and purged and remove them from disk
                print "The following metadata files associated with dataset '%s' have been purged" % dataset.file_name
                for hda in dataset.history_associations:
                    for metadata_file in m.filter( m.table.c.hda_id==hda.id ).all():
                        os.unlink( metadata_file.file_name() )
                        metadata_file.deleted = True
                        metadata_file.purged = True
                        metadata_file.flush()
                        print "%s" % metadata_file.file_name()
                for lda in dataset.library_associations:
                    for metadata_file in m.filter( m.table.c.lda_id==lda.id ).all():
                        metadata_file.deleted = True
                        metadata_file.purged = True
                        metadata_file.flush()
                        print "%s" % metadata_file.file_name()
                try:
                    # Remove associated extra files from disk if they exist
                    os.unlink( dataset.extra_files_path )
                except:
                    pass
        except Exception, exc:
            return "# Error, exception: %s caught attempting to purge %s\n" %( str( exc ), dataset.file_name )
    else:
        return "# Error: '%s' has not previously been deleted, so it cannot be purged\n" %dataset.file_name
    return ""

class CleanupDatasetsApplication( object ):
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

if __name__ == "__main__":
    main()
