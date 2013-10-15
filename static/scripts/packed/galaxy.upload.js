define(["galaxy.modal","galaxy.master","utils/galaxy.utils","utils/galaxy.uploadbox","libs/backbone/backbone-relational"],function(b,d,c){var a=Backbone.View.extend({modal:null,button_show:null,uploadbox:null,select_extension:{auto:"Auto-detect"},state:{init:"fa-icon-trash",queued:"fa-icon-spinner fa-icon-spin",running:"__running__",success:"fa-icon-ok",error:"fa-icon-warning-sign"},counter:{announce:0,success:0,error:0,running:0,reset:function(){this.announce=this.success=this.error=this.running=0}},initialize:function(){if(!Galaxy.currHistoryPanel){var e=this;window.setTimeout(function(){e.initialize()},500);return}var e=this;this.button_show=new d.GalaxyMasterIcon({icon:"fa-icon-upload",tooltip:"Upload Files",on_click:function(f){e.event_show(f)},with_number:true});Galaxy.master.prepend(this.button_show);var e=this;c.jsonFromUrl(galaxy_config.root+"api/datatypes",function(g){for(key in g){var f=g[key];e.select_extension[f]=f}})},event_dragover:function(f){},event_dragleave:function(f){},event_announce:function(f,g,i){var j="#upload-"+f;$(this.el).find("tbody:last").append(this.template_row(j,this.select_extension));var h=this.get_upload_item(f);h.fadeIn();h.find("#title").html(g.name);h.find("#size").html(this.size_to_string(g.size));var e=this;h.find("#symbol").on("click",function(){e.event_remove(f)});this.event_progress(f,g,0);this.counter.announce++;this.update_screen()},event_initialize:function(g,h,k){this.button_show.number(this.counter.announce);var i=this.get_upload_item(g);var l=i.find("#symbol");l.addClass(this.state.running);var e=Galaxy.currHistoryPanel.model.get("id");var f=i.find("#extension").val();var j=i.find("#space_to_tabs").is(":checked");this.uploadbox.configure({url:galaxy_config.root+"api/tools/",paramname:"files_0|file_data"});tool_input={};tool_input.dbkey="?";tool_input.file_type=f;tool_input["files_0|NAME"]=h.name;tool_input["files_0|type"]="upload_dataset";tool_input.space_to_tabs=j;data={};data.history_id=e;data.tool_id="upload1";data.inputs=JSON.stringify(tool_input);return data},event_progress:function(f,g,i){var h=this.get_upload_item(f);var e=parseInt(i);h.find(".progress-bar").css({width:e+"%"});if(e!=100){h.find("#percentage").html(e+"%")}else{h.find("#percentage").html("Adding to history...")}},event_success:function(e,f,h){this.event_progress(e,f,100);this.button_show.number("");this.counter.announce--;this.counter.success++;this.update_screen();var g=this.get_upload_item(e);g.addClass("success");g.find("#percentage").html("100%");var i=g.find("#symbol");i.removeClass(this.state.running);i.removeClass(this.state.queued);i.addClass(this.state.success);Galaxy.currHistoryPanel.refresh()},event_error:function(e,f,h){this.event_progress(e,f,0);this.button_show.number("");this.counter.announce--;this.counter.error++;this.update_screen();var g=this.get_upload_item(e);g.addClass("danger");g.find(".progress").remove();g.find("#info").html("<strong>Failed: </strong>"+h).show();var i=g.find("#symbol");i.removeClass(this.state.running);i.removeClass(this.state.queued);i.addClass(this.state.error)},event_upload:function(){if(this.counter.announce==0||this.counter.running>0){return}var f=$(this.el).find(".upload-item");var e=this;f.each(function(){var g=$(this).find("#symbol");if(g.hasClass(e.state.init)){g.removeClass(e.state.init);g.addClass(e.state.queued);$(this).find("#extension").attr("disabled",true);$(this).find("#space_to_tabs").attr("disabled",true)}});this.counter.running=this.counter.announce;this.update_screen();this.uploadbox.upload()},event_pause:function(){if(this.counter.running==0){return}this.uploadbox.pause();$("#upload-info").html("Queueing will pause after completing the current file...")},event_complete:function(){this.counter.running=0;this.update_screen();var f=$(this.el).find(".upload-item");var e=this;f.each(function(){var g=$(this).find("#symbol");if(g.hasClass(e.state.queued)&&!g.hasClass(e.state.running)){g.removeClass(e.state.queued);g.addClass(e.state.init);$(this).find("#extension").attr("disabled",false);$(this).find("#space_to_tabs").attr("disabled",false)}})},event_reset:function(){if(this.counter.running==0){var e=$(this.el).find(".upload-item");$(this.el).find("table").fadeOut({complete:function(){e.remove()}});this.counter.reset();this.update_screen();this.uploadbox.reset()}},event_remove:function(e){var f=this.get_upload_item(e);var g=f.find("#symbol");if(g.hasClass(this.state.init)||g.hasClass(this.state.success)||g.hasClass(this.state.error)){if(f.hasClass("success")){this.counter.success--}else{if(f.hasClass("danger")){this.counter.error--}else{this.counter.announce--}}this.update_screen();this.uploadbox.remove(e);f.remove()}},event_show:function(g){g.preventDefault();if(!this.modal){var f=this;this.modal=new b.GalaxyModal({title:"Upload files from your local drive",body:this.template("upload-box","upload-info"),buttons:{Select:function(){f.uploadbox.select()},Upload:function(){f.event_upload()},Pause:function(){f.event_pause()},Reset:function(){f.event_reset()},Close:function(){f.modal.hide()}},height:"350"});this.setElement("#upload-box");var f=this;this.uploadbox=this.$el.uploadbox({dragover:function(){f.event_dragover()},dragleave:function(){f.event_dragleave()},announce:function(e,h,i){f.event_announce(e,h,i)},initialize:function(e,h,i){return f.event_initialize(e,h,i)},success:function(e,h,i){f.event_success(e,h,i)},progress:function(e,h,i){f.event_progress(e,h,i)},error:function(e,h,i){f.event_error(e,h,i)},complete:function(){f.event_complete()},});this.update_screen()}this.modal.show()},get_upload_item:function(e){return $(this.el).find("#upload-"+e)},size_to_string:function(e){var f="";if(e>=100000000000){e=e/100000000000;f="TB"}else{if(e>=100000000){e=e/100000000;f="GB"}else{if(e>=100000){e=e/100000;f="MB"}else{if(e>=100){e=e/100;f="KB"}else{e=e*10;f="b"}}}}return"<strong>"+(Math.round(e)/10)+"</strong> "+f},update_screen:function(){if(this.counter.announce==0){if(this.uploadbox.compatible){message="Drag&drop files into this box or click 'Select' to select files!"}else{message="Unfortunately, your browser does not support multiple file uploads or drag&drop.<br>Please upgrade to i.e. Firefox 4+, Chrome 7+, IE 10+, Opera 12+ or Safari 6+."}}else{if(this.counter.running==0){message="You added "+this.counter.announce+" file(s) to the queue. Add more files or click 'Upload' to proceed."}else{message="Please wait..."+this.counter.announce+" out of "+this.counter.running+" remaining."}}$("#upload-info").html(message);if(this.counter.running==0&&this.counter.announce+this.counter.success+this.counter.error>0){this.modal.enableButton("Reset")}else{this.modal.disableButton("Reset")}if(this.counter.running==0&&this.counter.announce>0){this.modal.enableButton("Upload")}else{this.modal.disableButton("Upload")}if(this.counter.running>0){this.modal.enableButton("Pause")}else{this.modal.disableButton("Pause")}if(this.counter.running==0){this.modal.enableButton("Select")}else{this.modal.disableButton("Select")}if(this.counter.announce+this.counter.success+this.counter.error>0){$(this.el).find("table").show()}else{$(this.el).find("table").hide()}},template:function(f,e){return'<div id="'+f+'" class="upload-box"><table class="table table-striped" style="display: none;"><thead><tr><th>Name</th><th>Size</th><th>Type</th><th>Space&#8594;Tab</th><th>Status</th><th></th></tr></thead><tbody></tbody></table></div><h6 id="'+e+'" class="upload-info"></h6>'},template_row:function(g,f){var e='<tr id="'+g.substr(1)+'" class="upload-item"><td><div id="title" class="title"></div></td><td><div id="size" class="size"></div></td><td><select id="extension" class="extension">';for(key in f){e+='<option value="'+key+'">'+f[key]+"</option>"}e+='</select></td><td><input id="space_to_tabs" type="checkbox"></input></td><td><div id="info" class="info"><div class="progress"><div class="progress-bar progress-bar-success"></div><div id="percentage" class="percentage">0%</div></div></div></td><td><div id="symbol" class="symbol '+this.state.init+'"></div></td></tr>';return e}});return{GalaxyUpload:a}});