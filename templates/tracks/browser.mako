<%inherit file="/webapps/galaxy/base_panels.mako"/>

<%def name="init()">
<%
    self.has_left_panel=False
    self.has_right_panel=False
    self.active_view="visualization"
    self.message_box_visible=False
%>
</%def>

<%def name="stylesheets()">
${parent.stylesheets()}

${h.css( "history", "autocomplete_tagging", "trackster", "overcast/jquery-ui-1.8.5.custom" )}

<style type="text/css">
    #center {
        overflow: auto;
    }
    ul#sortable-ul {
        list-style: none;
        padding: 0;
        margin: 5px;
    }
    ul#sortable-ul li {
        display: block;
        margin: 5px 0;
        background: #eee;
    }
    .nav-container {
        position: fixed;
        width: 100%;
        left: 0;
        bottom: 0;
    }
    # Styles for filters.
    .filter-name {
        float: left;
    }
    table.filters {
        border-collapse: separate;
        border-spacing: 7px 0px;
    }
    .values {
        padding-right: 1em;
    }
</style>
</%def>

<%def name="center_panel()">
<div class="unified-panel-header" unselectable="on">
    <div class="unified-panel-header-inner">
        <div style="float:left;" id="title"></div>
        <a class="panel-header-button right-float" href="${h.url_for( controller='visualization', action='list' )}">Close</a>
        <a id="save-button" class="panel-header-button right-float" href="javascript:void(0);">Save</a>
        <a id="add-track" class="panel-header-button right-float" href="javascript:void(0);">Add Tracks</a>
    </div>
</div>

</%def>

<%def name="javascripts()">
${parent.javascripts()}
${h.js( "galaxy.base", "galaxy.panels", "json2", "jquery", "jquery.event.drag", "jquery.autocomplete", "trackster", "jquery.ui.sortable.slider" )}

<script type="text/javascript">

    var data_url = "${h.url_for( action='data' )}",
    	reference_url = "${h.url_for( action='reference' )}",
		chrom_url = "${h.url_for( action='chroms' )}",
    	view;
    
    $(function() {
        
        %if config:
            view = new View( $("#center"), "${config.get('title') | h}", "${config.get('vis_id')}", "${config.get('dbkey')}" );
            view.editor = true;
            %for track in config.get('tracks'):
                view.add_track(
                    new ${track["track_type"]}( "${track['name'] | h}", view, ${track['dataset_id']}, ${track['filters']}, ${track['prefs']} )
                );
            %endfor
            init();
        %else:
            var continue_fn = function() {
                view = new View( $("#center"), $("#new-title").val(), undefined, $("#new-dbkey").val() );
                view.editor = true;
                init();
                hide_modal();
            };
            $.ajax({
                url: "${h.url_for( action='new_browser', default_dbkey=default_dbkey )}",
                data: {},
                error: function() { alert( "Couldn't create new browser" ) },
                success: function(form_html) {
                    show_modal("New Track Browser", form_html, {
                        "Cancel": function() { window.location = "${h.url_for( controller='visualization', action='list' )}"; },
                        "Continue": function() { $(document).trigger("convert_dbkeys"); continue_fn(); }
                    });
                    $("#new-title").focus();
                    replace_big_select_inputs();
                }
            });
        %endif
		
		$(document).bind( "redraw", function() {
			view.redraw();
        });

        // To adjust the size of the viewport to fit the fixed-height footer
        var refresh = function() {
            if (view !== undefined) {
                view.viewport_container.height( $("#center").height() - $(".nav-container").height() - 40 );
                view.nav_container.width( $("#center").width() );
                view.redraw();
            }
        };
        $(window).bind( "resize", function() { refresh(); } );
        $("#right-border").bind( "click dragend", function() { refresh(); } );
        $(window).trigger( "resize" );
        
        // Execute initializer for EDITOR specific javascript
        function init() {
            if (view.num_tracks === 0) {
                $("#no-tracks").show();
            }
            $("#title").text(view.title + " (" + view.dbkey + ")");
            $(".viewport-container").sortable({
                start: function(e, ui) {
                    view.in_reordering = true;
                },
                stop: function(e, ui) {
                    view.in_reordering = false;
                },
                handle: ".draghandle",
            });
            
            window.onbeforeunload = function() {
                if ( view.has_changes ) {
                    return "There are unsaved changes to your visualization which will be lost.";
                }
            };
            
            var add_async_success = function(track_data) {
                var td = track_data,
					track_types = { "LineTrack": LineTrack, "FeatureTrack": FeatureTrack, "ReadTrack": ReadTrack },
					new_track = new track_types[track_data.track_type]( track_data.name, view, track_data.dataset_id, track_data.filters, track_data.prefs);
					
                view.add_track(new_track);
                view.has_changes = true;
                $("#no-tracks").hide();
                sidebar_box(new_track);
            };
            
            %if add_dataset is not None:
                $.ajax( {
                    url: "${h.url_for( action='add_track_async' )}",
                    data: { id: "${add_dataset}" },
                    dataType: "json",
                    success: add_async_success
                });
                
            %endif

            // Use a popup grid to add more tracks
            $("#add-track").bind( "click", function(e) {
                $.ajax({
                    url: "${h.url_for( action='list_datasets' )}",
                    data: { "f-dbkey": view.dbkey },
                    error: function() { alert( "Grid refresh failed" ); },
                    success: function(table_html) {
                        show_modal("Add Track &mdash; Select Dataset(s)", table_html, {
                            "Cancel": function() {
                                hide_modal();
                            },
                            "Insert": function() {
                                $('input[name=id]:checked').each(function() {
                                    var item_id = $(this).val();
                                    $.ajax( {
                                        url: "${h.url_for( action='add_track_async' )}",
                                        data: { id: item_id },
                                        dataType: "json",
                                        success: add_async_success
                                    });

                                });
                                hide_modal();
                            }
                        });
                    }
                });
            });
            
            $("#save-button").bind("click", function(e) {
                var sorted = $(".viewport-container").sortable('toArray'),
                    payload = [];
                    
                for (var i in sorted) {
                    var track_id = parseInt(sorted[i].split("track_")[1]),
                        track = view.tracks[track_id];
                    
                    payload.push( {
                        "track_type": track.track_type,
                        "name": track.name,
                        "dataset_id": track.dataset_id,
                        "prefs": track.prefs
                    });
                }
                // Show saving dialog box
                show_modal("Saving...", "<img src='${h.url_for('/static/images/yui/rel_interstitial_loading.gif')}'/>");
                
                $.ajax({
                    url: "${h.url_for( action='save' )}",
                    type: "POST",
                    data: {
                        'vis_id': view.vis_id,
                        'vis_title': view.title,
                        'dbkey': view.dbkey,
                        'payload': JSON.stringify(payload)
                    },
                    success: function(vis_id) {
                        view.vis_id = vis_id;
                        view.has_changes = false;
                        hide_modal();
                    },
                    error: function() { alert("Could not save visualization"); }
                });
            });
            
            function sidebar_box(track) {
                if (!track.hidden) {
                    var track_id = track.track_id,
                        label = $('<label for="track_' + track_id + 'title">' + track.name + '</label>'),
                        title = $('<div class="historyItemTitle"></div>'),
                        icon_div = $('<div class="historyItemButtons"></div>');
                        del_icon = $('<a href="#" class="icon-button delete" />'),
                        edit_icon = $('<a href="#" class="icon-button edit" />'),
                        body = $('<div class="historyItemBody"></div>'),
                        li = $('<li class="sortable"></li>').attr("id", "track_" + track_id + "_li"),
                        div = $('<div class="historyItemContainer historyItem"></div>'),
                        editable = $('<div style="display:none"></div>').attr("id", "track_" + track_id + "_editable");
                    
                    edit_icon.bind("click", function() {
                        $("#track_" + track_id + "_editable").toggle();
                    });
                    del_icon.bind("click", function() {
                        $("#track_" + track_id + "_li").fadeOut('slow', function() { $("#track_" + track_id + "_li").remove(); });
                        view.remove_track(track);
                        if (view.num_tracks === 0) {
                            $("#no-tracks").show();
                        }
                    });
                    icon_div.append(edit_icon).append(del_icon);
                    title.append(label).prepend(icon_div);
                    if (track.gen_options) {
                        editable.append(track.gen_options(track_id)).appendTo(body);
                    }
                    div.append(title).append(body).appendTo(li);
                    $("ul#sortable-ul").append(li);
                }
            };
            
            // Populate sort/move ul
            for (var track_id in view.tracks) {
                var track = view.tracks[track_id];
                sidebar_box(track);
            }
            
            $(window).trigger("resize");
        };
        
    });

</script>
</%def>
