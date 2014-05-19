define(["mvc/dataset/hda-edit","mvc/history/history-panel","mvc/base-mvc","utils/localization"],function(b,g,c,e){var d=c.SessionStorageModel.extend({defaults:{searching:false,tagsEditorShown:false,annotationEditorShown:false},toString:function(){return"HistoryPanelPrefs("+JSON.stringify(this.toJSON())+")"}});d.storageKey=function f(){return("history-panel")};var a=g.HistoryPanel.extend({HDAViewClass:b.HDAEditView,emptyMsg:e("This history is empty. Click 'Get Data' on the left tool menu to start"),noneFoundMsg:e("No matching datasets found"),initialize:function(h){h=h||{};this.preferences=new d(_.extend({id:d.storageKey()},_.pick(h,_.keys(d.prototype.defaults))));g.HistoryPanel.prototype.initialize.call(this,h)},loadCurrentHistory:function(i){var h=this;return this.loadHistoryWithHDADetails("current",i).then(function(k,j){h.trigger("current-history",h)})},switchToHistory:function(k,j){var h=this,i=function(){return jQuery.ajax({url:galaxy_config.root+"api/histories/"+k+"/set_as_current",method:"PUT"})};return this.loadHistoryWithHDADetails(k,j,i).then(function(m,l){h.trigger("switched-history",h)})},createNewHistory:function(j){if(!Galaxy||!Galaxy.currUser||Galaxy.currUser.isAnonymous()){this.displayMessage("error",e("You must be logged in to create histories"));return $.when()}var h=this,i=function(){return jQuery.post(galaxy_config.root+"api/histories",{current:true})};return this.loadHistory(undefined,j,i).then(function(l,k){h.trigger("new-history",h)})},setModel:function(i,h,j){g.HistoryPanel.prototype.setModel.call(this,i,h,j);if(this.model){this.log("checking for updates");this.model.checkForUpdates()}return this},_setUpModelEventHandlers:function(){g.HistoryPanel.prototype._setUpModelEventHandlers.call(this);if(Galaxy&&Galaxy.quotaMeter){this.listenTo(this.model,"change:nice_size",function(){Galaxy.quotaMeter.update()})}this.model.hdas.on("state:ready",function(i,j,h){if((!i.get("visible"))&&(!this.storage.get("show_hidden"))){this.removeHdaView(this.hdaViews[i.id])}},this)},render:function(j,k){this.log("render:",j,k);j=(j===undefined)?(this.fxSpeed):(j);var h=this,i;if(this.model){i=this.renderModel()}else{i=this.renderWithoutModel()}$(h).queue("fx",[function(l){if(j&&h.$el.is(":visible")){h.$el.fadeOut(j,l)}else{l()}},function(l){h.$el.empty();if(i){h.$el.append(i.children());h.renderBasedOnPrefs()}l()},function(l){if(j&&!h.$el.is(":visible")){h.$el.fadeIn(j,l)}else{l()}},function(l){if(k){k.call(this)}h.trigger("rendered",this);l()}]);return this},renderBasedOnPrefs:function(){if(this.preferences.get("searching")){this.toggleSearchControls(0,true)}},_renderEmptyMsg:function(j){var i=this,h=i.$emptyMessage(j),k=$(".toolMenuContainer");if((_.isEmpty(i.hdaViews)&&!i.searchFor)&&(Galaxy&&Galaxy.upload&&k.size())){h.empty();h.html([e("This history is empty"),". ",e("You can "),'<a class="uploader-link" href="javascript:void(0)">',e("load your own data"),"</a>",e(" or "),'<a class="get-data-link" href="javascript:void(0)">',e("get data from an external source"),"</a>"].join(""));h.find(".uploader-link").click(function(l){Galaxy.upload._eventShow(l)});h.find(".get-data-link").click(function(l){k.parent().scrollTop(0);k.find('span:contains("Get Data")').click()});h.show()}else{g.HistoryPanel.prototype._renderEmptyMsg.call(this,j)}return this},toggleSearchControls:function(i,h){var j=g.HistoryPanel.prototype.toggleSearchControls.call(this,i,h);this.preferences.set("searching",j)},_renderTags:function(h){var i=this;g.HistoryPanel.prototype._renderTags.call(this,h);if(this.preferences.get("tagsEditorShown")){this.tagsEditor.toggle(true)}this.tagsEditor.on("hiddenUntilActivated:shown hiddenUntilActivated:hidden",function(j){i.preferences.set("tagsEditorShown",j.hidden)})},_renderAnnotation:function(h){var i=this;g.HistoryPanel.prototype._renderAnnotation.call(this,h);if(this.preferences.get("annotationEditorShown")){this.annotationEditor.toggle(true)}this.annotationEditor.on("hiddenUntilActivated:shown hiddenUntilActivated:hidden",function(j){i.preferences.set("annotationEditorShown",j.hidden)})},connectToQuotaMeter:function(h){if(!h){return this}this.listenTo(h,"quota:over",this.showQuotaMessage);this.listenTo(h,"quota:under",this.hideQuotaMessage);this.on("rendered rendered:initial",function(){if(h&&h.isOverQuota()){this.showQuotaMessage()}});return this},showQuotaMessage:function(){var h=this.$el.find(".quota-message");if(h.is(":hidden")){h.slideDown(this.fxSpeed)}},hideQuotaMessage:function(){var h=this.$el.find(".quota-message");if(!h.is(":hidden")){h.slideUp(this.fxSpeed)}},connectToOptionsMenu:function(h){if(!h){return this}this.on("new-storage",function(j,i){if(h&&j){h.findItemByHtml(e("Include Deleted Datasets")).checked=j.get("show_deleted");h.findItemByHtml(e("Include Hidden Datasets")).checked=j.get("show_hidden")}});return this},toString:function(){return"CurrentHistoryPanel("+((this.model)?(this.model.get("name")):(""))+")"}});return{CurrentHistoryPanel:a}});