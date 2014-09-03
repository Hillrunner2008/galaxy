define(["utils/utils","mvc/ui/ui-table","mvc/ui/ui-misc","mvc/ui/ui-tabs"],function(c,b,e,a){var d=Backbone.View.extend({initialize:function(g,f){this.app=g;this.inputs=f.inputs;f.cls_tr="section-row";this.table=new b.View(f);this.setElement(this.table.$el);this.render()},render:function(){this.table.delAll();for(var f in this.inputs){this._add(this.inputs[f])}},_add:function(h){var g=this;var f=jQuery.extend(true,{},h);f.id=c.uuid();this.app.input_list[f.id]=f;var i=f.type;switch(i){case"conditional":this._addConditional(f);break;case"repeat":this._addRepeat(f);break;default:this._addRow(i,f)}},_addConditional:function(f){f.label=f.test_param.label;f.value=f.test_param.value;this._addRow("conditional",f);for(var h in f.cases){var g=f.id+"-section-"+h;var j=new d(this.app,{inputs:f.cases[h].inputs,cls:"ui-table-plain"});this.table.add("");this.table.add(j.$el);this.table.append(g)}},_addRepeat:function(f){var g=this;var k=new a.View({title_new:"Add "+f.title,max:f.max,onnew:function(){var i=f.id+"-section-"+c.uuid();var m=new d(g.app,{inputs:f.inputs,cls:"ui-table-plain"});k.add({id:i,title:f.title,$el:m.$el,ondel:function(){k.del(i);k.retitle(f.title);g.app.refresh()}});k.retitle(f.title);k.show(i);g.app.refresh()}});for(var j=0;j<f.min;j++){var h=f.id+"-section-"+c.uuid();var l=new d(g.app,{inputs:f.inputs,cls:"ui-table-plain"});k.add({id:h,title:f.title,$el:l.$el})}k.retitle(f.title);this.table.add("");this.table.add(k.$el);this.table.append(f.id)},_addRow:function(h,f){var j=f.id;var g=null;switch(h){case"text":g=this._field_text(f);break;case"select":g=this._field_select(f);break;case"data":g=this._field_data(f);break;case"data_column":g=this._field_column(f);break;case"textarea":g=this._field_textarea(f);break;case"conditional":g=this._field_conditional(f);break;case"hidden":g=this._field_hidden(f);break;case"integer":g=this._field_slider(f);break;case"float":g=this._field_slider(f);break;case"boolean":g=this._field_boolean(f);break;default:g=this._field_text(f);console.debug("tools-form::_addRow() : Unmatched field type ("+h+").")}if(f.value!==undefined){g.value(f.value)}this.app.field_list[j]=g;var i=$("<div/>");i.append(g.$el);if(f.help){i.append('<div class="ui-table-form-info">'+f.help+"</div>")}this.table.add('<span class="ui-table-form-title">'+f.label+"</span>","20%");this.table.add(i);this.table.append(j)},_field_conditional:function(f){var g=this;var h=[];for(var j in f.test_param.options){var k=f.test_param.options[j];h.push({label:k[0],value:k[1]})}return new e.Select.View({id:"field-"+f.id,data:h,onchange:function(s){for(var q in f.cases){var m=f.cases[q];var p=f.id+"-section-"+q;var l=g.table.get(p);var o=false;for(var n in m.inputs){var r=m.inputs[n].type;if(r&&r!=="hidden"){o=true;break}}if(m.value==s&&o){l.fadeIn("fast")}else{l.hide()}}}})},_field_data:function(f){var g=this;var l=f.id;var k=this.app.datasets.filterType();var h=[];for(var j in k){h.push({label:k[j].get("name"),value:k[j].get("id")})}return new e.Select.View({id:"field-"+l,data:h,value:h[0].value,onchange:function(u){var s=g.app.tree.findReferences(l,"data_column");var n=g.app.datasets.filter(u);if(n&&s.length>0){console.debug("tool-form::field_data() - Selected dataset "+u+".");var w=n.get("metadata_column_types");if(!w){console.debug("tool-form::field_data() - FAILED: Could not find metadata for dataset "+u+".")}for(var p in s){var q=g.app.input_list[s[p]];var r=g.app.field_list[s[p]];if(!q||!r){console.debug("tool-form::field_data() - FAILED: Column not found.")}var o=q.numerical;var m=[];for(var v in w){var t=w[v];if(t=="int"||t=="float"||!o){m.push({label:"Column: "+(parseInt(v)+1)+" ["+w[v]+"]",value:v})}}if(r){r.update(m);if(!r.exists(r.value())){r.value(r.first())}}}}else{console.debug("tool-form::field_data() - FAILED: Could not find dataset "+u+".")}}})},_field_select:function(f){var g=[];for(var h in f.options){var j=f.options[h];g.push({label:j[0],value:j[1]})}var k=e.Select;switch(f.display){case"checkboxes":k=e.Checkbox;break;case"radio":k=e.RadioButton;break}return new k.View({id:"field-"+f.id,data:g})},_field_column:function(f){return new e.Select.View({id:"field-"+f.id})},_field_text:function(f){return new e.Input({id:"field-"+f.id})},_field_slider:function(f){return new e.Slider.View({id:"field-"+f.id,min:f.min||0,max:f.max||1000,decimal:f.type=="float"})},_field_textarea:function(f){return new e.Textarea({id:"field-"+f.id})},_field_hidden:function(f){return new e.Hidden({id:"field-"+f.id})},_field_boolean:function(f){return new e.RadioButton.View({id:"field-"+f.id,data:[{label:"Yes",value:true},{label:"No",value:false}]})}});return{View:d}});