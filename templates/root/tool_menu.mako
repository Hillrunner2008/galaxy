## Render a tool
<%def name="render_tool( tool, section )">
    %if not tool.hidden:
        %if section:
            <div class="toolTitle">
        %else:
            <div class="toolTitleNoSection">
        %endif
            <%
                if tool.input_required:
                    link = h.url_for( controller='tool_runner', tool_id=tool.id )
                else:
                    link = h.url_for( tool.action, ** tool.get_static_param_values( t ) )
            %>
            ## FIXME: This doesn't look right
            ## %if "[[" in tool.description and "]]" in tool.description:
            ##   ${tool.description.replace( '[[', '<a href="link" target="galaxy_main">' % $tool.id ).replace( "]]", "</a>" )
            %if tool.name:
                <a id="link-${tool.id}" href="${link}" target="galaxy_main" minsizehint="${tool.uihints.get( 'minwidth', -1 )}">${_(tool.name)}</a> ${tool.description} 
            %else:
                <a id="link-${tool.id}" href="${link}" target="galaxy_main" minsizehint="${tool.uihints.get( 'minwidth', -1 )}">${tool.description}</a>
            %endif
        </div>
    %endif
</%def>

## Render a workflow
<%def name="render_workflow( key, workflow, section )">
    %if section:
        <div class="toolTitle">
    %else:
        <div class="toolTitleNoSection">
    %endif
        <% encoded_id = key.lstrip( 'workflow_' ) %>
        <a id="link-${workflow.id}" href="${ h.url_for( controller='workflow', action='run', id=encoded_id, check_user=False )}" target="galaxy_main">${workflow.name}</a>
    </div>
</%def>

## Render a label
<%def name="render_label( label )">
    <div class="toolSectionPad"></div>
    <div class="toolPanelLabel" id="title_${label.id}">
        <span>${label.text}</span>
    </div>
    <div class="toolSectionPad"></div>
</%def>

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
    <head>
        <title>${_('Galaxy Tools')}</title>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <link href="${h.url_for('/static/style/base.css')}" rel="stylesheet" type="text/css" />
        <link href="${h.url_for('/static/style/tool_menu.css')}" rel="stylesheet" type="text/css" />

        <script type="text/javascript" src="${h.url_for('/static/scripts/jquery.js')}"></script>

        <script type="text/javascript">
            var q = jQuery.noConflict();
            q(document).ready(function() { 
                q( "div.toolSectionBody" ).hide();
                q( "div.toolSectionTitle > span" ).wrap( "<a href='#'></a>" )
                var last_expanded = null;
                q( "div.toolSectionTitle" ).each( function() { 
                   var body = q(this).next( "div.toolSectionBody" );
                   q(this).click( function() {
                       if ( body.is( ":hidden" ) ) {
                           if ( last_expanded ) last_expanded.slideUp( "fast" );
                           last_expanded = body;
                           body.slideDown( "fast" );
                       }
                       else {
                           body.slideUp( "fast" );
                           last_expanded = null;
                       }
                       return false;
                   });
                });
                q( "a[@minsizehint]" ).click( function() {
                    if ( parent.handle_minwidth_hint ) {
                        parent.handle_minwidth_hint( q(this).attr( "minsizehint" ) );
                    }
                });
            });
        </script>
    </head>

    <body class="toolMenuPage">
        <div class="toolMenu">
            <div class="toolSectionList">
                %for key, val in toolbox.tool_panel.items():
                    %if key.startswith( 'tool' ):
                        ${render_tool( val, False )}
                        <div class="toolSectionPad"></div>
                    %elif key.startswith( 'workflow' ):
                        ${render_workflow( key, val, False )}
                    %elif key.startswith( 'section' ):
                        <% section = val %>
                        <div class="toolSectionTitle" id="title_${section.id}">
                            <span>${section.name}</span>
                        </div>
                        <div id="${section.id}" class="toolSectionBody">
                            <div class="toolSectionBg">
                                %for section_key, section_val in section.elems.items():
                                    %if section_key.startswith( 'tool' ):
                                        ${render_tool( section_val, True )}
                                    %elif section_key.startswith( 'workflow' ):
                                        ${render_workflow( section_key, section_val, True )}
                                    %elif section_key.startswith( 'label' ):
                                        ${render_label( section_val )}
                                    %endif
                                %endfor
                            </div>
                        </div>
                        <div class="toolSectionPad"></div>
                    %elif key.startswith( 'label' ):
                        ${render_label( val )}
                    %endif
                %endfor

                ## Link to workflow management. The location of this may change, but eventually
                ## at least some workflows will appear here (the user should be able to
                ## configure which of their stored workflows appear in the tools menu). 

                <div class="toolSectionPad"></div>
                <div class="toolSectionPad"></div>
                <div class="toolSectionTitle" id="title_XXinternalXXworkflow">
                    <span>${_('Workflow')} <i>(beta)</i></span>
                </div>
                <div id="XXinternalXXworkflow" class="toolSectionBody">
                    <div class="toolSectionBg">
                        <div class="toolTitle">
                            <a href="${h.url_for( controller='workflow', action='index' )}" target="galaxy_main">${_('Manage')}</a> ${_('workflows')}
                        </div>
                        %if t.user:
                            %for m in t.user.stored_workflow_menu_entries:
                                <div class="toolTitle">
                                    <a href="${h.url_for( controller='workflow', action='run', id=trans.security.encode_id(m.stored_workflow_id) )}" target="galaxy_main">${_(m.stored_workflow.name)}</a>
                                </div>
                            %endfor
                        %endif
                    </div>
                </div>
            </div>
        </div>
        <div style="height: 20px"></div>
    </body>
</html>
