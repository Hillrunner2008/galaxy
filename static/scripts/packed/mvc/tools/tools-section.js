define(["utils/utils","mvc/ui/ui-table","mvc/ui/ui-misc","mvc/tools/tools-repeat","mvc/tools/tools-select-content","mvc/tools/tools-input"],function(d,b,g,c,a,e){var f=Backbone.View.extend({initialize:function(i,h){this.app=i;this.inputs=h.inputs;h.cls_tr="section-row";this.table=new b.View(h);this.setElement(this.table.$el);this.render()},render:function(){this.table.delAll();for(var h in this.inputs){this._add(this.inputs[h])}},_add:function(j){var i=this;var h=jQuery.extend(true,{},j);h.id=j.id=d.uuid();this.app.input_list[h.id]=h;var k=h.type;switch(k){case"conditional":this._addConditional(h);break;case"repeat":this._addRepeat(h);break;default:this._addRow(h)}},_addConditional:function(h){var j=this;h.test_param.id=h.id;var m=this._addRow(h.test_param);m.options.onchange=function(t){var p=j.app.tree.matchCase(h,t);for(var r in h.cases){var w=h.cases[r];var u=h.id+"-section-"+r;var o=j.table.get(u);var v=false;for(var q in w.inputs){var s=w.inputs[q].type;if(s&&s!=="hidden"){v=true;break}}if(r==p&&v){o.fadeIn("fast")}else{o.hide()}}j.app.refresh()};for(var l in h.cases){var k=h.id+"-section-"+l;var n=new f(this.app,{inputs:h.cases[l].inputs,cls:"ui-table-plain"});n.$el.addClass("ui-table-form-section");this.table.add(n.$el);this.table.append(k)}m.trigger("change")},_addRepeat:function(o){var r=this;var p=0;function m(i,t){var s=o.id+"-section-"+(p++);var u=null;if(t){u=function(){k.del(s);k.retitle(o.title);r.app.rebuild();r.app.refresh()}}var v=new f(r.app,{inputs:i,cls:"ui-table-plain"});k.add({id:s,title:o.title,$el:v.$el,ondel:u});k.retitle(o.title)}var k=new c.View({title_new:o.title,max:o.max,onnew:function(){m(o.inputs,true);r.app.rebuild();r.app.refresh()}});var h=o.min;var q=_.size(o.cache);for(var l=0;l<Math.max(q,h);l++){var n=null;if(l<q){n=o.cache[l]}else{n=o.inputs}m(n,l>=h)}var j=new e(this.app,{label:o.title,help:o.help,field:k});j.$el.addClass("ui-table-form-section");this.table.add(j.$el);this.table.append(o.id)},_addRow:function(h){var k=h.id;var i=this._createField(h);if(h.is_dynamic){this.app.is_dynamic=true}this.app.field_list[k]=i;var j=new e(this.app,{label:h.label,optional:h.optional,help:h.help,field:i});this.app.element_list[k]=j;this.table.add(j.$el);this.table.append(k);return i},_createField:function(h){var i=null;switch(h.type){case"text":i=this._fieldText(h);break;case"select":i=this._fieldSelect(h);break;case"data":i=this._fieldData(h);break;case"data_column":i=this._fieldSelect(h);break;case"hidden":i=this._fieldHidden(h);break;case"integer":i=this._fieldSlider(h);break;case"float":i=this._fieldSlider(h);break;case"boolean":i=this._fieldBoolean(h);break;case"genomebuild":h.searchable=true;i=this._fieldSelect(h);break;case"drill_down":i=this._fieldDrilldown(h);break;case"baseurl":i=this._fieldHidden(h);break;default:this.app.incompatible=true;if(h.options){i=this._fieldSelect(h)}else{i=this._fieldText(h)}console.debug("tools-form::_addRow() : Auto matched field type ("+h.type+").")}if(h.value!==undefined){i.value(h.value)}return i},_fieldData:function(h){var i=this;return new a.View(this.app,{id:"field-"+h.id,extensions:h.extensions,multiple:h.multiple,type:h.type,data:h.options,onchange:function(){i.app.refresh()}})},_fieldSelect:function(h){var k=[];for(var l in h.options){var m=h.options[l];k.push({label:m[0],value:m[1]})}var n=g.Select;switch(h.display){case"checkboxes":n=g.Checkbox;break;case"radio":n=g.Radio;break}var j=this;return new n.View({id:"field-"+h.id,data:k,multiple:h.multiple,searchable:h.searchable,onchange:function(){j.app.refresh()}})},_fieldDrilldown:function(h){var i=this;return new g.Drilldown.View({id:"field-"+h.id,data:h.options,display:h.display,onchange:function(){i.app.refresh()}})},_fieldText:function(h){var i=this;return new g.Input({id:"field-"+h.id,area:h.area,onchange:function(){i.app.refresh()}})},_fieldSlider:function(h){return new g.Slider.View({id:"field-"+h.id,precise:h.type=="float",min:h.min,max:h.max})},_fieldHidden:function(h){return new g.Hidden({id:"field-"+h.id})},_fieldBoolean:function(h){return new g.RadioButton.View({id:"field-"+h.id,data:[{label:"Yes",value:"true"},{label:"No",value:"false"}]})}});return{View:f}});