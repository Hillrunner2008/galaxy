(function(){var b=Handlebars.template,a=Handlebars.templates=Handlebars.templates||{};a["template-user-quotaMeter-quota"]=b(function(g,m,f,l,k){this.compilerInfo=[4,">= 1.0.0"];f=this.merge(f,g.helpers);k=k||{};var i="",d,p,h="function",j=this.escapeExpression,o=this,n=f.blockHelperMissing;function e(t,s){var q="",r;q+=' title="Using ';if(r=f.nice_total_disk_usage){r=r.call(t,{hash:{},data:s})}else{r=t.nice_total_disk_usage;r=typeof r===h?r.apply(t):r}q+=j(r)+'"';return q}function c(r,q){return"Using"}i+='<div id="quota-meter" class="quota-meter progress">\n    <div id="quota-meter-bar"  class="quota-meter-bar bar" style="width: ';if(d=f.quota_percent){d=d.call(m,{hash:{},data:k})}else{d=m.quota_percent;d=typeof d===h?d.apply(m):d}i+=j(d)+'%"></div>\n    \n    <div id="quota-meter-text" class="quota-meter-text"\n        style="top: 6px"';d=f["if"].call(m,m.nice_total_disk_usage,{hash:{},inverse:o.noop,fn:o.program(1,e,k),data:k});if(d||d===0){i+=d}i+=">\n        ";p={hash:{},inverse:o.noop,fn:o.program(3,c,k),data:k};if(d=f.local){d=d.call(m,p)}else{d=m.local;d=typeof d===h?d.apply(m):d}if(!f.local){d=n.call(m,d,p)}if(d||d===0){i+=d}i+=" ";if(d=f.quota_percent){d=d.call(m,{hash:{},data:k})}else{d=m.quota_percent;d=typeof d===h?d.apply(m):d}i+=j(d)+"%\n    </div>\n</div>";return i})})();