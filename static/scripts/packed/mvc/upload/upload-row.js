define(["utils/utils","mvc/upload/upload-model","mvc/upload/upload-settings","mvc/ui/ui-popover","mvc/ui/ui-select"],function(d,b,a,c,e){return Backbone.View.extend({options:{padding:8},status_classes:{init:"upload-icon-button fa fa-trash-o",queued:"upload-icon fa fa-spinner fa-spin",running:"upload-icon fa fa-spinner fa-spin",success:"upload-icon-button fa fa-check",error:"upload-icon-button fa fa-exclamation-triangle"},settings:null,select_genome:null,select_extension:null,initialize:function(i,g){this.app=i;var f=this;this.model=new b.Model(g);this.setElement(this._template(g));var h=this.$el;this.settings=new c.View({title:"Upload configuration",container:h.find("#settings"),placement:"bottom"});this.select_genome=new e.View({css:"genome",onchange:function(){f.model.set("genome",f.select_genome.value())},data:f.app.list_genomes,container:h.find("#genome"),value:f.model.get("genome")});this.model.set("genome",f.select_genome.value());this.select_extension=new e.View({css:"extension",onchange:function(){f.model.set("extension",f.select_extension.value())},data:f.app.list_extensions,container:h.find("#extension"),value:f.model.get("extension")});this.model.set("extension",f.select_extension.value());h.find("#symbol").on("click",function(){f._removeRow()});h.find("#extension-info").on("click",function(j){f._showExtensionInfo()}).on("mousedown",function(j){j.preventDefault()});h.find("#settings").on("click",function(j){f._showSettings()}).on("mousedown",function(j){j.preventDefault()});h.find("#text-content").on("keyup",function(j){f.model.set("url_paste",$(j.target).val());f.model.set("file_size",$(j.target).val().length)});h.find("#space_to_tabs").on("change",function(j){f.model.set("space_to_tabs",$(j.target).prop("checked"))});this.model.on("change:percentage",function(){f._refreshPercentage()});this.model.on("change:status",function(){f._refreshStatus()});this.model.on("change:info",function(){f._refreshInfo()});this.model.on("change:genome",function(){f._refreshGenome()});this.model.on("change:file_size",function(){f._refreshFileSize()});this.model.on("remove",function(){f.remove()});this.app.collection.on("reset",function(){f.remove()})},render:function(){var m=this.model.get("file_name");var g=this.model.get("file_size");var j=this.model.get("file_mode");var i=this.$el;i.find("#title").html(m);i.find("#size").html(d.bytesToString(g));i.find("#mode").removeClass().addClass("mode");if(j=="new"){var l=i.find("#text");var k=this.options.padding;var h=i.width()-2*k;var f=i.height()-k;l.css("width",h+"px");l.css("top",f+"px");i.height(f+l.height()+2*k);l.show();i.find("#mode").addClass("fa fa-pencil")}if(j=="local"){i.find("#mode").addClass("fa fa-laptop")}if(j=="ftp"){i.find("#mode").addClass("fa fa-code-fork")}},remove:function(){this.select_genome.remove();this.select_extension.remove();Backbone.View.prototype.remove.apply(this)},_refreshGenome:function(){var f=this.model.get("genome");this.select_genome.value(f)},_refreshInfo:function(){var f=this.model.get("info");if(f){this.$el.find("#info").html("<strong>Failed: </strong>"+f).show()}else{this.$el.find("#info").hide()}},_refreshPercentage:function(){var f=parseInt(this.model.get("percentage"));this.$el.find(".progress-bar").css({width:f+"%"});if(f!=100){this.$el.find("#percentage").html(f+"%")}else{this.$el.find("#percentage").html("Adding to history...")}},_refreshStatus:function(){var g=this.$el;var f=this.model.get("status");var i=this.status_classes[f];var h=this.$el.find("#symbol");h.removeClass();h.addClass(i);if(f=="init"){this.select_genome.enable();this.select_extension.enable();g.find("#text-content").attr("disabled",false);g.find("#space_to_tabs").attr("disabled",false)}else{this.select_genome.disable();this.select_extension.disable();g.find("#text-content").attr("disabled",true);g.find("#space_to_tabs").attr("disabled",true)}if(f=="success"){g.addClass("success");g.find("#percentage").html("100%")}if(f=="error"){g.addClass("danger");g.find(".progress").remove()}},_refreshFileSize:function(){var f=this.model.get("file_size");this.$el.find("#size").html(d.bytesToString(f))},_removeRow:function(){var f=this.model.get("status");if(f=="init"||f=="success"||f=="error"){this.app.collection.remove(this.model)}},_showExtensionInfo:function(){var f=$(this.el).find("#extension-info");var i=this.model.get("extension");var h=this.select_extension.text();var g=d.findPair(this.app.list_extensions,"id",i);if(!this.extension_popup){this.extension_popup=new c.View({placement:"bottom",container:f})}if(!this.extension_popup.visible){this.extension_popup.title(h);this.extension_popup.empty();this.extension_popup.append(this._templateDescription(g));this.extension_popup.show()}else{this.extension_popup.hide()}},_showSettings:function(){if(!this.settings.visible){this.settings.empty();this.settings.append((new a(this)).$el);this.settings.show()}else{this.settings.hide()}},_templateDescription:function(g){if(g.description){var f=g.description;if(g.description_url){f+='&nbsp;(<a href="'+g.description_url+'" target="_blank">read more</a>)'}return f}else{return"There is no description available for this file extension."}},_template:function(f){return'<tr id="upload-item-'+f.id+'" class="upload-item"><td><div style="position: relative;"><div id="mode"></div><div id="title" class="title"></div><div id="text" class="text"><div class="text-info">You can tell Galaxy to download data from web by entering URL in this box (one per line). You can also directly paste the contents of a file.</div><textarea id="text-content" class="text-content form-control"></textarea></div></div></td><td><div id="size" class="size"></div></td><td><div id="extension" class="extension" style="float: left;"/>&nbsp;&nbsp<div id="extension-info" class="upload-icon-button fa fa-search"/></td><td><div id="genome" class="genome" /></td><td><div id="settings" class="upload-icon-button fa fa-gear"></div><td><div id="info" class="info"><div class="progress"><div class="progress-bar progress-bar-success"></div><div id="percentage" class="percentage">0%</div></div></div></td><td><div id="symbol" class="'+this.status_classes.init+'"></div></td></tr>'}})});