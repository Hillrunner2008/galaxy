define(["utils/utils","mvc/ui/ui-portlet","mvc/ui/ui-misc","mvc/citation/citation-model","mvc/citation/citation-view","mvc/tools","mvc/tools/tools-template","mvc/tools/tools-content","mvc/tools/tools-section","mvc/tools/tools-tree","mvc/tools/tools-jobs"],function(i,h,l,j,a,e,d,f,k,c,g){var b=Backbone.View.extend({container:"body",initialize:function(n){console.debug(n);var m=this;if(parent.Galaxy&&parent.Galaxy.modal){this.modal=parent.Galaxy.modal}else{this.modal=new l.Modal.View()}this.options=n;this.setElement("<div/>");$(this.container).append(this.$el);this.tree=new c(this);this.job_handler=new g(this);this.content=new f({history_id:m.options.history_id,success:function(){m._buildForm(m.options)}})},message:function(m){$(this.container).empty();$(this.container).append(m)},reset:function(){for(var m in this.element_list){this.element_list[m].reset()}},rebuild:function(){this.tree.refresh();console.debug("tools-form::refresh() - Refreshed form structure.")},refresh:function(){var m=this;if(!this.is_dynamic){return}var n=this.tree.finalize({data:function(o){if(o.values.length>0&&o.values[0]&&o.values[0].src==="hda"){return m.content.get({id:o.values[0].id}).dataset_id}return null}});console.debug("tools-form::_refreshForm() - Refreshing states.");console.debug(n);i.request({type:"GET",url:galaxy_config.root+"api/tools/"+this.options.id+"/build",data:n,success:function(o){m._rebuildForm(o);console.debug("tools-form::_refreshForm() - States refreshed.");console.debug(o)},error:function(o){console.debug("tools-form::_refreshForm() - Refresh request failed.");console.debug(o)}})},_buildModel:function(){var m=this;var n=galaxy_config.root+"api/tools/"+this.options.id+"/build?";if(this.options.job_id){n+="job_id="+this.options.job_id}else{if(this.options.dataset_id){n+="dataset_id="+this.options.dataset_id}else{var o=top.location.href;var p=o.indexOf("?");if(o.indexOf("tool_id=")!=-1&&p!==-1){n+=o.slice(p+1)}}}i.request({type:"GET",url:n,success:function(q){m.options=$.extend(m.options,q);m.model=q;m.inputs=q.inputs;console.debug("tools-form::initialize() - Initial tool model ready.");console.debug(q);m._buildForm()},error:function(q){console.debug("tools-form::initialize() - Initial tool model request failed.");console.debug(q)}})},_rebuildForm:function(m){var n=this;this.tree.matchModel(m,function(p,t){var o=n.input_list[p];if(o&&o.options){if(JSON.stringify(o.options)!=JSON.stringify(t.options)){o.options=t.options;var u=n.field_list[p];if(u.update&&o.type!="data"){var s=[];for(var r in t.options){var q=t.options[r];if(q.length>2){s.push({label:q[0],value:q[1]})}}u.update(s);console.debug("Updating options for "+p)}}}})},_buildForm:function(o){var n=this;this.field_list={};this.input_list={};this.element_list={};this.model=o;this.inputs=o.inputs;var q=new l.ButtonMenu({icon:"fa-gear",tooltip:"Click to see a list of options."});if(o.biostar_url){q.addMenu({icon:"fa-question-circle",title:"Question?",tooltip:"Ask a question about this tool (Biostar)",onclick:function(){window.open(n.options.biostar_url+"/p/new/post/")}});q.addMenu({icon:"fa-search",title:"Search",tooltip:"Search help for this tool (Biostar)",onclick:function(){window.open(n.options.biostar_url+"/t/"+n.options.id+"/")}})}q.addMenu({icon:"fa-share",title:"Share",tooltip:"Share this tool",onclick:function(){prompt("Copy to clipboard: Ctrl+C, Enter",window.location.origin+galaxy_config.root+"root?tool_id="+n.options.id)}});if(Galaxy.currUser.get("is_admin")){q.addMenu({icon:"fa-download",title:"Download",tooltip:"Download this tool",onclick:function(){window.location.href=galaxy_config.root+"api/tools/"+n.options.id+"/download"}})}this.section=new k.View(n,{inputs:this.inputs,cls:"ui-table-plain"});if(this.incompatible){this.$el.hide();$("#tool-form-classic").show();return}this.portlet=new h.View({icon:"fa-wrench",title:"<b>"+this.model.name+"</b> "+this.model.description,operations:{menu:q},buttons:{execute:new l.Button({icon:"fa-check",tooltip:"Execute the tool",title:"Execute",cls:"btn btn-primary",floating:"clear",onclick:function(){n.job_handler.submit()}})}});this.$el.empty();this.$el.append(this.portlet.$el);if(o.help!=""){this.$el.append(d.help(o.help))}if(o.citations){var m=new j.ToolCitationCollection();m.tool_id=o.id;var p=new a.CitationListView({collection:m});p.render();m.fetch();this.$el.append(p.$el)}this.portlet.append(this.section.$el);this.rebuild()}});return{View:b}});