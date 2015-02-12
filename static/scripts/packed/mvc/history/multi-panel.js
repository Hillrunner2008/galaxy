define(["mvc/history/history-model","mvc/history/history-panel-edit","mvc/base-mvc","utils/ajax-queue","ui/mode-button","ui/search-input"],function(d,l,z,a){function g(I,E){E=E||{};if(!(Galaxy&&Galaxy.modal)){return I.copy()}var F=I.get("name"),C="Copy of '"+F+"'";function D(K){if(!K){if(!Galaxy.modal.$("#invalid-title").size()){var J=$("<p/>").attr("id","invalid-title").css({color:"red","margin-top":"8px"}).addClass("bg-danger").text(_l("Please enter a valid history title"));Galaxy.modal.$(".modal-body").append(J)}return false}return K}function G(J){var K=$('<p><span class="fa fa-spinner fa-spin"></span> Copying history...</p>').css("margin-top","8px");Galaxy.modal.$(".modal-body").append(K);I.copy(true,J).fail(function(){alert(_l("History could not be copied. Please contact a Galaxy administrator"))}).always(function(){Galaxy.modal.hide()})}function H(){var J=Galaxy.modal.$("#copy-modal-title").val();if(!D(J)){return}G(J)}Galaxy.modal.show(_.extend({title:_l("Copying history")+' "'+F+'"',body:$(['<label for="copy-modal-title">',_l("Enter a title for the copied history"),":","</label><br />",'<input id="copy-modal-title" class="form-control" style="width: 100%" value="',C,'" />'].join("")),buttons:{Cancel:function(){Galaxy.modal.hide()},Copy:H}},E));$("#copy-modal-title").focus().select();$("#copy-modal-title").on("keydown",function(J){if(J.keyCode===13){H()}})}var B=Backbone.View.extend(z.LoggableMixin).extend({tagName:"div",className:"history-column flex-column flex-row-container",id:function q(){if(!this.model){return""}return"history-column-"+this.model.get("id")},initialize:function c(C){C=C||{};this.panel=C.panel||this.createPanel(C);this.setUpListeners()},createPanel:function u(D){D=_.extend({model:this.model,dragItems:true},D);var C=new l.HistoryPanelEdit(D);C._renderEmptyMessage=this.__patch_renderEmptyMessage;return C},__patch_renderEmptyMessage:function(E){var D=this,F=_.chain(this.model.get("state_ids")).values().flatten().value().length,C=D.$emptyMessage(E);if(!_.isEmpty(D.hdaViews)){C.hide()}else{if(F&&!this.model.contents.length){C.empty().append($('<span class="fa fa-spinner fa-spin"></span> <i>loading datasets...</i>')).show()}else{if(D.searchFor){C.text(D.noneFoundMsg).show()}else{C.text(D.emptyMsg).show()}}}return C},setUpListeners:function f(){var C=this;this.once("rendered",function(){C.trigger("rendered:initial",C)});this.setUpPanelListeners()},setUpPanelListeners:function k(){var C=this;this.listenTo(this.panel,{rendered:function(){C.trigger("rendered",C)}},this)},inView:function(C,D){var F=this.$el.offset().left,E=F+this.$el.width();if(E<C){return false}if(F>D){return false}return true},$panel:function e(){return this.$(".history-panel")},render:function A(D){D=(D!==undefined)?(D):("fast");var C=this.model?this.model.toJSON():{};this.$el.html(this.template(C));this.renderPanel(D);this.setUpBehaviors();return this},setUpBehaviors:function v(){},template:function w(D){D=D||{};var C=['<div class="panel-controls clear flex-row">',this.controlsLeftTemplate(),'<div class="pull-right">','<button class="delete-history btn btn-default">',D.deleted?_l("Undelete"):_l("Delete"),"</button>",'<button class="copy-history btn btn-default">',_l("Copy"),"</button>","</div>","</div>",'<div class="inner flex-row flex-column-container">','<div id="history-',D.id,'" class="history-column history-panel flex-column"></div>',"</div>"].join("");return $(C)},controlsLeftTemplate:function(){return(this.currentHistory)?['<div class="pull-left">','<strong class="current-label">',_l("Current History"),"</strong>","</div>"].join(""):['<div class="pull-left">','<button class="switch-to btn btn-default">',_l("Switch to"),"</button>","</div>"].join("")},renderPanel:function h(C){C=(C!==undefined)?(C):("fast");this.panel.setElement(this.$panel()).render(C);if(this.currentHistory){this.panel.$list().before(this.panel._renderDropTargetHelp())}return this},events:{"click .switch-to.btn":function(){this.model.setAsCurrent()},"click .delete-history.btn":function(){var C=this,D;if(this.model.get("deleted")){D=this.model.undelete()}else{D=this.model._delete()}D.fail(function(G,E,F){alert(_l("Could not delete the history")+":\n"+F)}).done(function(E){C.render()})},"click .copy-history.btn":"copy"},copy:function s(){g(this.model)},toString:function(){return"HistoryPanelColumn("+(this.panel?this.panel:"")+")"}});var m=Backbone.View.extend(z.LoggableMixin).extend({className:"multi-history-columns",initialize:function c(C){C=C||{};this.log(this+".init",C);if(!C.currentHistoryId){throw new Error(this+" requires a currentHistoryId in the options")}this.currentHistoryId=C.currentHistoryId;this.options={columnWidth:312,borderWidth:1,columnGap:8,headerHeight:29,footerHeight:0,controlsHeight:20};this.order=C.order||"update";this.hdaQueue=new a.NamedAjaxQueue([],false);this.collection=null;this.setCollection(C.histories||[]);this.columnMap={};this.createColumns(C.columnOptions);this.setUpListeners()},setUpListeners:function f(){},setCollection:function y(D){var C=this;C.stopListening(C.collection);C.collection=D;C.sortCollection(C.order,{silent:true});C.setUpCollectionListeners();C.trigger("new-collection",C);return C},setUpCollectionListeners:function(){var C=this,D=C.collection;C.listenTo(D,{add:C.addAsCurrentColumn,"set-as-current":C.setCurrentHistory,"change:deleted":C.handleDeletedHistory,sort:function(){C.renderColumns(0)}})},setCurrentHistory:function p(D){var C=this.columnMap[this.currentHistoryId];if(C){C.currentHistory=false;C.$el.height("")}this.currentHistoryId=D.id;var E=this.columnMap[this.currentHistoryId];E.currentHistory=true;this.sortCollection();multipanel._recalcFirstColumnHeight();return E},handleDeletedHistory:function b(D){if(D.get("deleted")){this.log("handleDeletedHistory",this.collection.includeDeleted,D);var C=this;column=C.columnMap[D.id];if(!column){return}if(column.model.id===this.currentHistoryId){}else{if(!C.collection.includeDeleted){C.removeColumn(column)}}}},sortCollection:function(C,D){C=C||this.order;var E=this.currentHistoryId;switch(C){case"name":this.collection.comparator=function(F){return[F.id!==E,F.get("name").toLowerCase()]};break;case"size":this.collection.comparator=function(F){return[F.id!==E,F.get("size")]};break;default:this.collection.comparator=function(F){return[F.id!==E,Date(F.get("update_time"))]}}this.collection.sort(D);return this.collection},setOrder:function(C){if(["update","name","size"].indexOf(C)===-1){C="update"}this.order=C;this.trigger("order:change",C,this);this.$(".current-order").text(C);this.sortCollection();return this},create:function(C){return this.collection.create({current:true})},createColumns:function r(D){D=D||{};var C=this;this.columnMap={};C.collection.each(function(E,F){var G=C.createColumn(E,D);C.columnMap[E.id]=G})},createColumn:function t(E,C){C=_.extend({},C,{model:E});var D=new B(C);if(E.id===this.currentHistoryId){D.currentHistory=true}this.setUpColumnListeners(D);return D},sortedFilteredColumns:function(C){C=C||this.filters;if(!C||!C.length){return this.sortedColumns()}var D=this;return D.sortedColumns().filter(function(G,F){var E=G.currentHistory||_.every(C.map(function(H){return H.call(G)}));return E})},sortedColumns:function(){var D=this;var C=this.collection.map(function(F,E){return D.columnMap[F.id]});return C},addColumn:function o(E,C){C=C!==undefined?C:true;var D=this.createColumn(E);this.columnMap[E.id]=D;if(C){this.renderColumns()}return D},addAsCurrentColumn:function o(E){var D=this,C=this.addColumn(E,false);this.setCurrentHistory(E);C.once("rendered",function(){D.queueHdaFetch(C)});return C},removeColumn:function x(E,D){D=D!==undefined?D:true;this.log("removeColumn",E);if(!E){return}var F=this,C=this.options.columnWidth+this.options.columnGap;E.$el.fadeOut("fast",function(){if(D){$(this).remove();F.$(".middle").width(F.$(".middle").width()-C);F.checkColumnsInView();F._recalcFirstColumnHeight()}F.stopListening(E.panel);F.stopListening(E);delete F.columnMap[E.model.id];E.remove()})},setUpColumnListeners:function n(C){var D=this;D.listenTo(C,{"in-view":D.queueHdaFetch});D.listenTo(C.panel,{"view:draggable:dragstart":function(H,F,E,G){D._dropData=JSON.parse(H.dataTransfer.getData("text"));D.currentColumnDropTargetOn()},"view:draggable:dragend":function(H,F,E,G){D._dropData=null;D.currentColumnDropTargetOff()},"droptarget:drop":function(G,H,F){var I=D._dropData.filter(function(J){return(_.isObject(J)&&J.id&&J.model_class==="HistoryDatasetAssociation")});D._dropData=null;var E=new a.NamedAjaxQueue();I.forEach(function(J){E.add({name:"copy-"+J.id,fn:function(){return F.model.contents.copy(J.id)}})});E.start();E.done(function(J){F.model.fetch()})}})},columnMapLength:function(){return Object.keys(this.columnMap).length},render:function A(D){D=D!==undefined?D:this.fxSpeed;var C=this;C.log(C+".render");C.$el.html(C.mainTemplate(C));C.renderColumns(D);C.setUpBehaviors();C.trigger("rendered",C);return C},renderColumns:function j(F){F=F!==undefined?F:this.fxSpeed;var E=this,C=E.sortedFilteredColumns();E.$(".middle").width(C.length*(this.options.columnWidth+this.options.columnGap)+this.options.columnGap+16);var D=E.$(".middle");D.empty();C.forEach(function(H,G){H.$el.appendTo(D);H.delegateEvents();E.renderColumn(H,F)});if(this.searchFor&&C.length<=1){}else{E.checkColumnsInView();this._recalcFirstColumnHeight()}return C},renderColumn:function(C,D){D=D!==undefined?D:this.fxSpeed;return C.render(D)},queueHdaFetch:function i(E){if(E.model.contents.length===0&&!E.model.get("empty")){var C={},D=_.values(E.panel.storage.get("expandedIds")).join();if(D){C.dataset_details=D}this.hdaQueue.add({name:E.model.id,fn:function(){var F=E.model.contents.fetch({data:C,silent:true});return F.done(function(G){E.panel.renderItems()})}});if(!this.hdaQueue.running){this.hdaQueue.start()}}},queueHdaFetchDetails:function(C){if((C.model.contents.length===0&&!C.model.get("empty"))||(!C.model.contents.haveDetails())){this.hdaQueue.add({name:C.model.id,fn:function(){var D=C.model.contents.fetch({data:{details:"all"},silent:true});return D.done(function(E){C.panel.renderItems()})}});if(!this.hdaQueue.running){this.hdaQueue.start()}}},renderInfo:function(C){this.$(".header .header-info").text(C)},events:{"click .done.btn":"close","click .create-new.btn":"create","click #include-deleted":"_clickToggleDeletedHistories","click .order .order-update":function(C){this.setOrder("update")},"click .order .order-name":function(C){this.setOrder("name")},"click .order .order-size":function(C){this.setOrder("size")},"click #toggle-deleted":"_clickToggleDeletedDatasets","click #toggle-hidden":"_clickToggleHiddenDatasets"},close:function(D){var C="/";if(Galaxy&&Galaxy.options&&Galaxy.options.root){C=Galaxy.options.root}else{if(galaxy_config&&galaxy_config.root){C=galaxy_config.root}}window.location=C},_clickToggleDeletedHistories:function(C){return this.toggleDeletedHistories($(C.currentTarget).is(":checked"))},toggleDeletedHistories:function(C){if(C){window.location=Galaxy.options.root+"history/view_multiple?include_deleted_histories=True"}else{window.location=Galaxy.options.root+"history/view_multiple"}},_clickToggleDeletedDatasets:function(C){return this.toggleDeletedDatasets($(C.currentTarget).is(":checked"))},toggleDeletedDatasets:function(C){C=C!==undefined?C:false;var D=this;D.sortedFilteredColumns().forEach(function(F,E){_.delay(function(){F.panel.toggleShowDeleted(C,false)},E*200)})},_clickToggleHiddenDatasets:function(C){return this.toggleHiddenDatasets($(C.currentTarget).is(":checked"))},toggleHiddenDatasets:function(C){C=C!==undefined?C:false;var D=this;D.sortedFilteredColumns().forEach(function(F,E){_.delay(function(){F.panel.toggleShowHidden(C,false)},E*200)})},setUpBehaviors:function(){var D=this;D._moreOptionsPopover();D.$("#search-histories").searchInput({name:"search-histories",placeholder:_l("search histories"),onsearch:function(E){D.searchFor=E;D.filters=[function(){return this.model.matchesAll(D.searchFor)}];D.renderColumns(0)},onclear:function(E){D.searchFor=null;D.filters=[];D.renderColumns(0)}});D.$("#search-datasets").searchInput({name:"search-datasets",placeholder:_l("search all datasets"),onfirstsearch:function(E){D.hdaQueue.clear();D.$("#search-datasets").searchInput("toggle-loading");D.searchFor=E;D.sortedFilteredColumns().forEach(function(F){F.panel.searchItems(E);D.queueHdaFetchDetails(F)});D.hdaQueue.progress(function(F){D.renderInfo([_l("searching"),(F.curr+1),_l("of"),F.total].join(" "))});D.hdaQueue.deferred.done(function(){D.renderInfo("");D.$("#search-datasets").searchInput("toggle-loading")})},onsearch:function(E){D.searchFor=E;D.sortedFilteredColumns().forEach(function(F){F.panel.searchItems(E)})},onclear:function(E){D.searchFor=null;D.sortedFilteredColumns().forEach(function(F){F.panel.clearSearch()})}});$(window).resize(function(){D._recalcFirstColumnHeight()});var C=_.debounce(_.bind(this.checkColumnsInView,this),100);this.$(".middle").parent().scroll(C)},_moreOptionsPopover:function(){return this.$(".open-more-options.btn").popover({container:".header",placement:"bottom",html:true,content:$(this.optionsPopoverTemplate(this))})},_recalcFirstColumnHeight:function(){var C=this.$(".history-column").first(),E=this.$(".middle").height(),D=C.find(".panel-controls").height();C.height(E).find(".inner").height(E-D)},_viewport:function(){var C=this.$(".middle").parent().offset().left;return{left:C,right:C+this.$(".middle").parent().width()}},columnsInView:function(){var C=this._viewport();return this.sortedFilteredColumns().filter(function(D){return D.currentHistory||D.inView(C.left,C.right)})},checkColumnsInView:function(){this.columnsInView().forEach(function(C){C.trigger("in-view",C)})},currentColumnDropTargetOn:function(){var C=this.columnMap[this.currentHistoryId];if(!C){return}C.panel.dataDropped=function(D){};C.panel.dropTargetOn()},currentColumnDropTargetOff:function(){var C=this.columnMap[this.currentHistoryId];if(!C){return}C.panel.dataDropped=l.HistoryPanelEdit.prototype.dataDrop;C.panel.dropTarget=false;C.panel.$(".history-drop-target").remove()},toString:function(){return"MultiPanelColumns("+(this.columns?this.columns.length:0)+")"},mainTemplate:_.template(['<div class="header flex-column-container">','<div class="control-column control-column-left flex-column">','<button class="create-new btn btn-default">',_l("Create new"),"</button> ",'<div id="search-histories" class="search-control"></div>','<div id="search-datasets" class="search-control"></div>','<button class="open-more-options btn btn-default">','<span class="fa fa-ellipsis-h" title="More options"></span>',"</button>","</div>",'<div class="control-column control-column-center flex-column">','<div class="header-info">',"</div>","</div>",'<div class="control-column control-column-right flex-column">','<button class="done btn btn-default">',_l("Done"),"</button>","</div>","</div>",'<div class="outer-middle flex-row flex-row-container">','<div class="middle flex-column-container flex-row"></div>',"</div>",'<div class="footer flex-column-container">',"</div>"].join(""),{variable:"view"}),optionsPopoverTemplate:_.template(['<div class="more-options">','<div class="checkbox"><label><input id="include-deleted" type="checkbox"','<%= view.collection.includeDeleted? " checked" : "" %>>',_l("Include deleted histories"),"</label></div>",'<div class="order btn-group">','<button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown">',_l("Order histories by")+" ",'<span class="current-order"><%= view.order %></span> ','<span class="caret"></span>',"</button>",'<ul class="dropdown-menu" role="menu">','<li><a href="javascript:void(0);" class="order-update">',_l("Time of last update"),"</a></li>",'<li><a href="javascript:void(0);" class="order-name">',_l("Name"),"</a></li>",'<li><a href="javascript:void(0);" class="order-size">',_l("Size"),"</a></li>","</ul>","</div>",'<div class="checkbox"><label><input id="toggle-deleted" type="checkbox">',_l("Include deleted datasets"),"</label></div>",'<div class="checkbox"><label><input id="toggle-hidden" type="checkbox">',_l("Include hidden datasets"),"</label></div>","</div>"].join(""),{variable:"view"}),});return{MultiPanelColumns:m}});