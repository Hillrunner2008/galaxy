define(["mvc/dataset/states","mvc/dataset/dataset-li","mvc/tags","mvc/annotations","jq-plugins/ui/fa-icon-button","mvc/base-mvc","utils/localization"],function(g,d,e,b,a,i,c){var f=d.DatasetListItemView;var h=f.extend({initialize:function(j){f.prototype.initialize.call(this,j);this.hasUser=j.hasUser;this.purgeAllowed=j.purgeAllowed||false;this.tagsEditorShown=j.tagsEditorShown||false;this.annotationEditorShown=j.annotationEditorShown||false},_renderPrimaryActions:function(){var j=f.prototype._renderPrimaryActions.call(this);if(this.model.get("state")===g.NOT_VIEWABLE){return j}return f.prototype._renderPrimaryActions.call(this).concat([this._renderEditButton(),this._renderDeleteButton()])},_renderEditButton:function(){if((this.model.get("state")===g.DISCARDED)||(!this.model.get("accessible"))){return null}var l=this.model.get("purged"),j=this.model.get("deleted"),k={title:c("Edit attributes"),href:this.model.urls.edit,target:this.linkTarget,faIcon:"fa-pencil",classes:"edit-btn"};if(j||l){k.disabled=true;if(l){k.title=c("Cannot edit attributes of datasets removed from disk")}else{if(j){k.title=c("Undelete dataset to edit attributes")}}}else{if(_.contains([g.UPLOAD,g.NEW],this.model.get("state"))){k.disabled=true;k.title=c("This dataset is not yet editable")}}return a(k)},_renderDeleteButton:function(){if((!this.model.get("accessible"))){return null}var j=this,k=this.model.isDeletedOrPurged();return a({title:!k?c("Delete"):c("Dataset is already deleted"),disabled:k,faIcon:"fa-times",classes:"delete-btn",onclick:function(){j.$el.find(".icon-btn.delete-btn").trigger("mouseout");j.model["delete"]()}})},_renderDetails:function(){var j=f.prototype._renderDetails.call(this),k=this.model.get("state");if(!this.model.isDeletedOrPurged()&&_.contains([g.OK,g.FAILED_METADATA],k)){this._renderTags(j);this._renderAnnotation(j);this._makeDbkeyEditLink(j)}this._setUpBehaviors(j);return j},_renderSecondaryActions:function(){var j=f.prototype._renderSecondaryActions.call(this);switch(this.model.get("state")){case g.UPLOAD:case g.NEW:case g.NOT_VIEWABLE:return j;case g.ERROR:j.unshift(this._renderErrButton());return j.concat([this._renderRerunButton()]);case g.OK:case g.FAILED_METADATA:return j.concat([this._renderRerunButton(),this._renderVisualizationsButton()])}return j.concat([this._renderRerunButton()])},_renderErrButton:function(){return a({title:c("View or report this error"),href:this.model.urls.report_error,classes:"report-error-btn",target:this.linkTarget,faIcon:"fa-bug"})},_renderRerunButton:function(){return a({title:c("Run this job again"),href:this.model.urls.rerun,classes:"rerun-btn",target:this.linkTarget,faIcon:"fa-refresh"})},_renderVisualizationsButton:function(){var j=this.model.get("visualizations");if((this.model.isDeletedOrPurged())||(!this.hasUser)||(!this.model.hasData())||(_.isEmpty(j))){return null}if(!_.isObject(j[0])){this.warn("Visualizations have been switched off");return null}var k=$(this.templates.visualizations(j,this));k.find('[target="galaxy_main"]').attr("target",this.linkTarget);this._addScratchBookFn(k.find(".visualization-link").addBack(".visualization-link"));return k},_addScratchBookFn:function(k){var j=this;k.click(function(l){if(Galaxy.frame&&Galaxy.frame.active){Galaxy.frame.add({title:"Visualization",type:"url",content:$(this).attr("href")});l.preventDefault();l.stopPropagation()}})},_renderTags:function(j){if(!this.hasUser){return}var k=this;this.tagsEditor=new e.TagsEditor({model:this.model,el:j.find(".tags-display"),onshowFirstTime:function(){this.render()},onshow:function(){k.tagsEditorShown=true},onhide:function(){k.tagsEditorShown=false},$activator:a({title:c("Edit dataset tags"),classes:"tag-btn",faIcon:"fa-tags"}).appendTo(j.find(".actions .right"))});if(this.tagsEditorShown){this.tagsEditor.toggle(true)}},_renderAnnotation:function(j){if(!this.hasUser){return}var k=this;this.annotationEditor=new b.AnnotationEditor({model:this.model,el:j.find(".annotation-display"),onshowFirstTime:function(){this.render()},onshow:function(){k.annotationEditorShown=true},onhide:function(){k.annotationEditorShown=false},$activator:a({title:c("Edit dataset annotation"),classes:"annotate-btn",faIcon:"fa-comment"}).appendTo(j.find(".actions .right"))});if(this.annotationEditorShown){this.annotationEditor.toggle(true)}},_makeDbkeyEditLink:function(j){if(this.model.get("metadata_dbkey")==="?"&&!this.model.isDeletedOrPurged()){var k=$('<a class="value">?</a>').attr("href",this.model.urls.edit).attr("target",this.linkTarget);j.find(".dbkey .value").replaceWith(k)}},events:_.extend(_.clone(f.prototype.events),{"click .undelete-link":"_clickUndeleteLink","click .purge-link":"_clickPurgeLink","click .edit-btn":function(j){this.trigger("edit",this,j)},"click .delete-btn":function(j){this.trigger("delete",this,j)},"click .rerun-btn":function(j){this.trigger("rerun",this,j)},"click .report-err-btn":function(j){this.trigger("report-err",this,j)},"click .visualization-btn":function(j){this.trigger("visualize",this,j)},"click .dbkey a":function(j){this.trigger("edit",this,j)}}),_clickUndeleteLink:function(j){this.model.undelete();return false},_clickPurgeLink:function(j){this.model.purge();return false},toString:function(){var j=(this.model)?(this.model+""):("(no model)");return"HDAEditView("+j+")"}});h.prototype.templates=(function(){var k=_.extend({},f.prototype.templates.warnings,{failed_metadata:i.wrapTemplate(['<% if( dataset.state === "failed_metadata" ){ %>','<div class="failed_metadata-warning warningmessagesmall">',c("An error occurred setting the metadata for this dataset"),'<br /><a href="<%= dataset.urls.edit %>" target="<%= view.linkTarget %>">',c("Set it manually or retry auto-detection"),"</a>","</div>","<% } %>"],"dataset"),deleted:i.wrapTemplate(["<% if( dataset.deleted && !dataset.purged ){ %>",'<div class="deleted-msg warningmessagesmall">',c("This dataset has been deleted"),'<br /><a class="undelete-link" href="javascript:void(0);">',c("Undelete it"),"</a>","<% if( view.purgeAllowed ){ %>",'<br /><a class="purge-link" href="javascript:void(0);">',c("Permanently remove it from disk"),"</a>","<% } %>","</div>","<% } %>"],"dataset")});var j=i.wrapTemplate(["<% if( visualizations.length === 1 ){ %>",'<a class="visualization-btn visualization-link icon-btn" href="<%= visualizations[0].href %>"',' target="<%= visualizations[0].target %>" title="',c("Visualize in"),' <%= visualizations[0].html %>">','<span class="fa fa-bar-chart-o"></span>',"</a>","<% } else { %>",'<div class="visualizations-dropdown dropdown">','<a class="visualization-btn icon-btn" data-toggle="dropdown" title="',c("Visualize"),'">','<span class="fa fa-bar-chart-o"></span>',"</a>",'<ul class="dropdown-menu" role="menu">',"<% _.each( visualizations, function( visualization ){ %>",'<li><a class="visualization-link" href="<%= visualization.href %>"',' target="<%= visualization.target %>">',"<%= visualization.html %>","</a></li>","<% }); %>","</ul>","</div>","<% } %>"],"visualizations");return _.extend({},f.prototype.templates,{warnings:k,visualizations:j})}());return{DatasetListItemEdit:h}});