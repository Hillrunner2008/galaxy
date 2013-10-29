define(["mvc/dataset/hda-model","mvc/dataset/hda-base"],function(d,a){var f=a.HDABaseView.extend(LoggableMixin).extend({initialize:function(g){a.HDABaseView.prototype.initialize.call(this,g);this.hasUser=g.hasUser;this.defaultPrimaryActionButtonRenderers=[this._render_showParamsButton,this._render_rerunButton]},_render_titleButtons:function(){return a.HDABaseView.prototype._render_titleButtons.call(this).concat([this._render_editButton(),this._render_deleteButton()])},_render_editButton:function(){if((this.model.get("state")===d.HistoryDatasetAssociation.STATES.NEW)||(this.model.get("state")===d.HistoryDatasetAssociation.STATES.UPLOAD)||(this.model.get("state")===d.HistoryDatasetAssociation.STATES.DISCARDED)||(this.model.get("state")===d.HistoryDatasetAssociation.STATES.NOT_VIEWABLE)||(!this.model.get("accessible"))){this.editButton=null;return null}var i=this.model.get("purged"),g=this.model.get("deleted"),h={title:_l("Edit Attributes"),href:this.urls.edit,target:"galaxy_main",icon_class:"edit"};if(g||i){h.enabled=false;if(i){h.title=_l("Cannot edit attributes of datasets removed from disk")}else{if(g){h.title=_l("Undelete dataset to edit attributes")}}}return new IconButtonView({model:new IconButton(h)}).render().$el},_render_deleteButton:function(){if((this.model.get("state")===d.HistoryDatasetAssociation.STATES.NEW)||(this.model.get("state")===d.HistoryDatasetAssociation.STATES.NOT_VIEWABLE)||(!this.model.get("accessible"))){this.deleteButton=null;return null}var g=this,h=g.urls["delete"],i={title:_l("Delete"),href:h,icon_class:"delete",on_click:function(){g.$el.find(".menu-button.delete").trigger("mouseout");g.model["delete"]()}};if(this.model.get("deleted")||this.model.get("purged")){i={title:_l("Dataset is already deleted"),icon_class:"delete",enabled:false}}return new IconButtonView({model:new IconButton(i)}).render().$el},_render_errButton:function(){if(this.model.get("state")!==d.HistoryDatasetAssociation.STATES.ERROR){this.errButton=null;return null}return new IconButtonView({model:new IconButton({title:_l("View or report this error"),href:this.urls.report_error,target:"galaxy_main",icon_class:"bug"})}).render().$el},_render_rerunButton:function(){return new IconButtonView({model:new IconButton({title:_l("Run this job again"),href:this.urls.rerun,target:"galaxy_main",icon_class:"arrow-circle"})}).render().$el},_render_visualizationsButton:function(){var g=this.model.get("visualizations");if((!this.model.hasData())||(_.isEmpty(g))){this.visualizationsButton=null;return null}if(_.isObject(g[0])){return this._render_visualizationsFrameworkButton(g)}if(!this.urls.visualization){this.visualizationsButton=null;return null}var i=this.model.get("dbkey"),l=this.urls.visualization,j={},m={dataset_id:this.model.get("id"),hda_ldda:"hda"};if(i){m.dbkey=i}this.visualizationsButton=new IconButtonView({model:new IconButton({title:_l("Visualize"),href:this.urls.visualization,icon_class:"chart_curve"})});var h=this.visualizationsButton.render().$el;h.addClass("visualize-icon");function k(n){switch(n){case"trackster":return b(l,m,i);case"scatterplot":return e(l,m);default:return function(){Galaxy.frame_manager.frame_new({title:"Visualization",type:"url",content:l+"/"+n+"?"+$.param(m)})}}}if(g.length===1){h.attr("title",g[0]);h.click(k(g[0]))}else{_.each(g,function(o){var n=o.charAt(0).toUpperCase()+o.slice(1);j[_l(n)]=k(o)});make_popupmenu(h,j)}return h},_render_visualizationsFrameworkButton:function(g){if(!(this.model.hasData())||!(g&&!_.isEmpty(g))){this.visualizationsButton=null;return null}this.visualizationsButton=new IconButtonView({model:new IconButton({title:_l("Visualize"),icon_class:"chart_curve"})});var i=this.visualizationsButton.render().$el;i.addClass("visualize-icon");if(_.keys(g).length===1){i.attr("title",_.keys(g)[0]);i.attr("href",_.values(g)[0])}else{var j=[];_.each(g,function(k){j.push(k)});var h=new PopupMenu(i,j)}return i},_render_tagButton:function(){if(!this.hasUser||!this.urls.tags.get){this.tagButton=null;return null}return new IconButtonView({model:new IconButton({title:_l("Edit dataset tags"),target:"galaxy_main",href:this.urls.tags.get,icon_class:"tags"})}).render().$el},_render_annotateButton:function(){if(!this.hasUser||!this.urls.annotation.get){this.annotateButton=null;return null}return new IconButtonView({model:new IconButton({title:_l("Edit dataset annotation"),target:"galaxy_main",icon_class:"annotate"})}).render().$el},_render_body_failed_metadata:function(){var h=$("<a/>").attr({href:this.urls.edit,target:"galaxy_main"}).text(_l("set it manually or retry auto-detection")),g=$("<span/>").text(_l("You may be able to")+" ").append(h),i=a.HDABaseView.prototype._render_body_failed_metadata.call(this);i.find(".warningmessagesmall strong").append(g);return i},_render_body_error:function(){var g=a.HDABaseView.prototype._render_body_error.call(this);g.find(".dataset-actions .left").prepend(this._render_errButton());return g},_render_body_ok:function(){var g=a.HDABaseView.prototype._render_body_ok.call(this);if(this.model.isDeletedOrPurged()){return g}this.makeDbkeyEditLink(g);g.find(".dataset-actions .left").append(this._render_visualizationsButton());g.find(".dataset-actions .right").append([this._render_tagButton(),this._render_annotateButton()]);return g},makeDbkeyEditLink:function(g){if(this.model.get("metadata_dbkey")==="?"&&!this.model.isDeletedOrPurged()){g.find(".dataset-dbkey .value").replaceWith($('<a target="galaxy_main">?</a>').attr("href",this.urls.edit))}},events:{"click .dataset-title-bar":"toggleBodyVisibility","click .dataset-undelete":function(g){this.model.undelete();return false},"click .dataset-unhide":function(g){this.model.unhide();return false},"click .dataset-purge":"confirmPurge","click a.icon-button.tags":"loadAndDisplayTags","click a.icon-button.annotate":"loadAndDisplayAnnotation"},confirmPurge:function c(g){this.model.purge();return false},loadAndDisplayTags:function(i){this.log(this+".loadAndDisplayTags",i);var g=this,h=this.$el.find(".tags-display"),j=h.find(".tags");if(h.is(":hidden")){if(!jQuery.trim(j.html())){var k=$.ajax(this.urls.tags.get);k.fail(function(n,l,m){g.log("Tagging failed",n,l,m);g.trigger("error",g,n,{},_l("Tagging failed"))});k.done(function(l){j.html(l);j.find("[title]").tooltip();h.slideDown(g.fxSpeed)})}else{h.slideDown(g.fxSpeed)}}else{h.slideUp(g.fxSpeed)}return false},loadAndDisplayAnnotation:function(k){this.log(this+".loadAndDisplayAnnotation",k);var i=this,h=this.$el.find(".annotation-display"),g=h.find(".annotation"),j=this.urls.annotation.set;if(h.is(":hidden")){if(!jQuery.trim(g.html())){var l=$.ajax(this.urls.annotation.get);l.fail(function(o,m,n){i.log("Annotation failed",o,m,n);i.trigger("error",i,o,{},_l("Annotation failed"))});l.done(function(m){m=m||"<em>"+_l("Describe or add notes to dataset")+"</em>";g.html(m);h.find("[title]").tooltip();g.make_text_editable({use_textarea:true,on_finish:function(n){g.text(n);i.model.save({annotation:n},{silent:true}).fail(function(){g.text(i.model.previous("annotation"))})}});h.slideDown(i.fxSpeed)})}else{h.slideDown(i.fxSpeed)}}else{h.slideUp(i.fxSpeed)}return false},toString:function(){var g=(this.model)?(this.model+""):("(no model)");return"HDAView("+g+")"}});function e(g,h){action=function(){Galaxy.frame_manager.frame_new({title:"Scatterplot",type:"url",content:g+"/scatterplot?"+$.param(h),location:"center"});$("div.popmenu-wrapper").remove();return false};return action}function b(g,i,h){return function(){var j={};if(h){j["f-dbkey"]=h}$.ajax({url:g+"/list_tracks?"+$.param(j),dataType:"html",error:function(){alert(("Could not add this dataset to browser")+".")},success:function(k){var l=window.parent;l.Galaxy.modal.show({title:"View Data in a New or Saved Visualization",buttons:{Cancel:function(){l.Galaxy.modal.hide()},"View in saved visualization":function(){l.Galaxy.modal.show({title:"Add Data to Saved Visualization",body:k,buttons:{Cancel:function(){l.Galaxy.modal.hide()},"Add to visualization":function(){$(l.document).find("input[name=id]:checked").each(function(){l.Galaxy.modal.hide();var m=$(this).val();i.id=m;l.Galaxy.frame_manager.frame_new({title:"Trackster",type:"url",content:g+"/trackster?"+$.param(i)})})}}})},"View in new visualization":function(){l.Galaxy.modal.hide();var m=g+"/trackster?"+$.param(i);l.Galaxy.frame_manager.frame_new({title:"Trackster",type:"url",content:m})}}})}});return false}}return{HDAEditView:f}});