(function(){var b=Handlebars.template,a=Handlebars.templates=Handlebars.templates||{};a["template-hda-annotationArea"]=b(function(g,m,f,l,k){this.compilerInfo=[2,">= 1.0.0-rc.3"];f=f||g.helpers;k=k||{};var i="",d,p,h="function",j=this.escapeExpression,o=this,n=f.blockHelperMissing;function e(r,q){return"Annotation"}function c(r,q){return"Edit dataset annotation"}i+='\n<div id="';if(d=f.id){d=d.call(m,{hash:{},data:k})}else{d=m.id;d=typeof d===h?d.apply(m):d}i+=j(d)+'-annotation-area" class="annotation-area" style="display: none;">\n    <strong>';p={hash:{},inverse:o.noop,fn:o.program(1,e,k),data:k};if(d=f.local){d=d.call(m,p)}else{d=m.local;d=typeof d===h?d.apply(m):d}if(!f.local){d=n.call(m,d,p)}if(d||d===0){i+=d}i+=':</strong>\n    <div id="';if(d=f.id){d=d.call(m,{hash:{},data:k})}else{d=m.id;d=typeof d===h?d.apply(m):d}i+=j(d)+'-anotation-elt" class="annotation-elt tooltip editable-text"\n         style="margin: 1px 0px 1px 0px" title="';p={hash:{},inverse:o.noop,fn:o.program(3,c,k),data:k};if(d=f.local){d=d.call(m,p)}else{d=m.local;d=typeof d===h?d.apply(m):d}if(!f.local){d=n.call(m,d,p)}if(d||d===0){i+=d}i+='">\n    </div>\n</div>';return i})})();