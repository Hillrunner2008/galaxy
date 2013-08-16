define(["libs/underscore","viz/trackster/util","mvc/data","libs/backbone/backbone-relational"],function(t,a,u){var e={hidden:false,show:function(){this.set("hidden",false)},hide:function(){this.set("hidden",true)},is_visible:function(){return !this.attributes.hidden}};var d=Backbone.RelationalModel.extend({defaults:{name:null,label:null,type:null,value:null,html:null,num_samples:5},initialize:function(){this.attributes.html=unescape(this.attributes.html)},copy:function(){return new d(this.toJSON())},get_samples:function(){var w=this.get("type"),v=null;if(w==="number"){v=d3.scale.linear().domain([this.get("min"),this.get("max")]).ticks(this.get("num_samples"))}else{if(w==="select"){v=t.map(this.get("options"),function(x){return x[0]})}}return v},set_value:function(v){this.set("value",v||"")}},{TYPE_DICT:{number:c},create:function(v){var w=d.TYPE_DICT[v.type]||d;return new w(v)}});var c=d.extend({defaults:t.extend({},d.prototype.defaults,{min:null,max:null}),initialize:function(){d.prototype.initialize.call(this);if(this.attributes.min){this.attributes.min=parseInt(this.attributes.min,10)}if(this.attributes.max){this.attributes.max=parseInt(this.attributes.max,10)}},set_value:function(v){this.set("value",parseInt(v,10))}});var h=Backbone.RelationalModel.extend({defaults:{id:null,name:null,description:null,target:null,inputs:[]},initialize:function(v){this.attributes.inputs=new Backbone.Collection(t.map(v.inputs,function(w){return d.create(w)}))},urlRoot:galaxy_paths.get("tool_url"),copy:function(w){var x=new h(this.toJSON());if(w){var v=new Backbone.Collection();x.get("inputs").each(function(y){if(y.get_samples()){v.push(y)}});x.set("inputs",v)}return x},apply_search_results:function(v){(t.indexOf(v,this.attributes.id)!==-1?this.show():this.hide());return this.is_visible()},set_input_value:function(v,w){this.get("inputs").find(function(x){return x.get("name")===v}).set("value",w)},set_input_values:function(w){var v=this;t.each(t.keys(w),function(x){v.set_input_value(x,w[x])})},run:function(){return this._run()},rerun:function(w,v){return this._run({action:"rerun",target_dataset_id:w.id,regions:v})},get_inputs_dict:function(){var v={};this.get("inputs").each(function(w){v[w.get("name")]=w.get("value")});return v},_run:function(x){var y=t.extend({tool_id:this.id,inputs:this.get_inputs_dict()},x);var w=$.Deferred(),v=new a.ServerStateDeferred({ajax_settings:{url:this.urlRoot,data:JSON.stringify(y),dataType:"json",contentType:"application/json",type:"POST"},interval:2000,success_fn:function(z){return z!=="pending"}});$.when(v.go()).then(function(z){w.resolve(new u.DatasetCollection().reset(z))});return w}});t.extend(h.prototype,e);var n=Backbone.View.extend({});var k=Backbone.Collection.extend({model:h});var o=Backbone.Model.extend(e);var r=Backbone.Model.extend({defaults:{elems:[],open:false},clear_search_results:function(){t.each(this.attributes.elems,function(v){v.show()});this.show();this.set("open",false)},apply_search_results:function(w){var x=true,v;t.each(this.attributes.elems,function(y){if(y instanceof o){v=y;v.hide()}else{if(y instanceof h){if(y.apply_search_results(w)){x=false;if(v){v.show()}}}}});if(x){this.hide()}else{this.show();this.set("open",true)}}});t.extend(r.prototype,e);var b=Backbone.Model.extend({defaults:{search_hint_string:"search tools",min_chars_for_search:3,spinner_url:"",clear_btn_url:"",search_url:"",visible:true,query:"",results:null,clear_key:27},initialize:function(){this.on("change:query",this.do_search)},do_search:function(){var x=this.attributes.query;if(x.length<this.attributes.min_chars_for_search){this.set("results",null);return}var w=x+"*";if(this.timer){clearTimeout(this.timer)}$("#search-clear-btn").hide();$("#search-spinner").show();var v=this;this.timer=setTimeout(function(){$.get(v.attributes.search_url,{query:w},function(y){v.set("results",y);$("#search-spinner").hide();$("#search-clear-btn").show()},"json")},200)},clear_search:function(){this.set("query","");this.set("results",null)}});t.extend(b.prototype,e);var l=Backbone.Model.extend({initialize:function(v){this.attributes.tool_search=v.tool_search;this.attributes.tool_search.on("change:results",this.apply_search_results,this);this.attributes.tools=v.tools;this.attributes.layout=new Backbone.Collection(this.parse(v.layout))},parse:function(w){var v=this,x=function(A){var z=A.type;if(z==="tool"){return v.attributes.tools.get(A.id)}else{if(z==="section"){var y=t.map(A.elems,x);A.elems=y;return new r(A)}else{if(z==="label"){return new o(A)}}}};return t.map(w,x)},clear_search_results:function(){this.get("layout").each(function(v){if(v instanceof r){v.clear_search_results()}else{v.show()}})},apply_search_results:function(){var w=this.get("tool_search").get("results");if(w===null){this.clear_search_results();return}var v=null;this.get("layout").each(function(x){if(x instanceof o){v=x;v.hide()}else{if(x instanceof h){if(x.apply_search_results(w)){if(v){v.show()}}}else{v=null;x.apply_search_results(w)}}})}});var p=Backbone.View.extend({initialize:function(){this.model.on("change:hidden",this.update_visible,this);this.update_visible()},update_visible:function(){(this.model.attributes.hidden?this.$el.hide():this.$el.show())}});var j=p.extend({tagName:"div",template:Handlebars.templates.tool_link,render:function(){this.$el.append(this.template(this.model.toJSON()));return this}});var f=p.extend({tagName:"div",className:"toolPanelLabel",render:function(){this.$el.append($("<span/>").text(this.model.attributes.name));return this}});var i=p.extend({tagName:"div",className:"toolSectionWrapper",template:Handlebars.templates.panel_section,initialize:function(){p.prototype.initialize.call(this);this.model.on("change:open",this.update_open,this)},render:function(){this.$el.append(this.template(this.model.toJSON()));var v=this.$el.find(".toolSectionBody");t.each(this.model.attributes.elems,function(w){if(w instanceof h){var x=new j({model:w,className:"toolTitle"});x.render();v.append(x.$el)}else{if(w instanceof o){var y=new f({model:w});y.render();v.append(y.$el)}else{}}});return this},events:{"click .toolSectionTitle > a":"toggle"},toggle:function(){this.model.set("open",!this.model.attributes.open)},update_open:function(){(this.model.attributes.open?this.$el.children(".toolSectionBody").slideDown("fast"):this.$el.children(".toolSectionBody").slideUp("fast"))}});var m=Backbone.View.extend({tagName:"div",id:"tool-search",className:"bar",template:Handlebars.templates.tool_search,events:{click:"focus_and_select","keyup :input":"query_changed","click #search-clear-btn":"clear"},render:function(){this.$el.append(this.template(this.model.toJSON()));if(!this.model.is_visible()){this.$el.hide()}this.$el.find(".tooltip").tooltip();return this},focus_and_select:function(){this.$el.find(":input").focus().select()},clear:function(){this.model.clear_search();this.$el.find(":input").val(this.model.attributes.search_hint_string);this.focus_and_select();return false},query_changed:function(v){if((this.model.attributes.clear_key)&&(this.model.attributes.clear_key===v.which)){this.clear();return false}this.model.set("query",this.$el.find(":input").val())}});var s=Backbone.View.extend({tagName:"div",className:"toolMenu",initialize:function(){this.model.get("tool_search").on("change:results",this.handle_search_results,this)},render:function(){var v=this;var w=new m({model:this.model.get("tool_search")});w.render();v.$el.append(w.$el);this.model.get("layout").each(function(y){if(y instanceof r){var x=new i({model:y});x.render();v.$el.append(x.$el)}else{if(y instanceof h){var z=new j({model:y,className:"toolTitleNoSection"});z.render();v.$el.append(z.$el)}else{if(y instanceof o){var A=new f({model:y});A.render();v.$el.append(A.$el)}}}});v.$el.find("a.tool-link").click(function(z){var y=$(this).attr("class").split(/\s+/)[0],x=v.model.get("tools").get(y);v.trigger("tool_link_click",z,x)});return this},handle_search_results:function(){var v=this.model.get("tool_search").get("results");if(v&&v.length===0){$("#search-no-results").show()}else{$("#search-no-results").hide()}}});var q=Backbone.View.extend({className:"toolForm",template:Handlebars.templates.tool_form,render:function(){this.$el.children().remove();this.$el.append(this.template(this.model.toJSON()))}});var g=Backbone.View.extend({className:"toolMenuAndView",initialize:function(){this.tool_panel_view=new s({collection:this.collection});this.tool_form_view=new q()},render:function(){this.tool_panel_view.render();this.tool_panel_view.$el.css("float","left");this.$el.append(this.tool_panel_view.$el);this.tool_form_view.$el.hide();this.$el.append(this.tool_form_view.$el);var v=this;this.tool_panel_view.on("tool_link_click",function(x,w){x.preventDefault();v.show_tool(w)})},show_tool:function(w){var v=this;w.fetch().done(function(){v.tool_form_view.model=w;v.tool_form_view.render();v.tool_form_view.$el.show();$("#left").width("650px")})}});return{ToolParameter:d,IntegerToolParameter:c,Tool:h,ToolCollection:k,ToolSearch:b,ToolPanel:l,ToolPanelView:s,ToolFormView:q}});