(function(){var b=Handlebars.template,a=Handlebars.templates=Handlebars.templates||{};a["template-hda-body"]=b(function(g,r,p,k,z){this.compilerInfo=[4,">= 1.0.0"];p=this.merge(p,g.helpers);z=z||{};var q="",h,e="function",d=this.escapeExpression,o=this,c=p.blockHelperMissing;function n(D,C){var A="",B;A+='\n    <div class="dataset-summary">\n        ';if(B=p.body){B=B.call(D,{hash:{},data:C})}else{B=D.body;B=typeof B===e?B.apply(D):B}if(B||B===0){A+=B}A+='\n    </div>\n    <div class="dataset-actions clear">\n        <div class="left"></div>\n        <div class="right"></div>\n    </div>\n\n    ';return A}function m(D,C){var A="",B;A+='\n    <div class="dataset-summary">\n        ';B=p["if"].call(D,D.misc_blurb,{hash:{},inverse:o.noop,fn:o.program(4,l,C),data:C});if(B||B===0){A+=B}A+="\n\n        ";B=p["if"].call(D,D.data_type,{hash:{},inverse:o.noop,fn:o.program(6,j,C),data:C});if(B||B===0){A+=B}A+="\n\n        ";B=p["if"].call(D,D.metadata_dbkey,{hash:{},inverse:o.noop,fn:o.program(9,f,C),data:C});if(B||B===0){A+=B}A+="\n\n        ";B=p["if"].call(D,D.misc_info,{hash:{},inverse:o.noop,fn:o.program(12,x,C),data:C});if(B||B===0){A+=B}A+='\n    </div>\n\n    <div class="dataset-actions clear">\n        <div class="left"></div>\n        <div class="right"></div>\n    </div>\n\n    ';B=p.unless.call(D,D.deleted,{hash:{},inverse:o.noop,fn:o.program(14,w,C),data:C});if(B||B===0){A+=B}A+="\n\n    ";return A}function l(D,C){var A="",B;A+='\n        <div class="dataset-blurb">\n            <span class="value">';if(B=p.misc_blurb){B=B.call(D,{hash:{},data:C})}else{B=D.misc_blurb;B=typeof B===e?B.apply(D):B}A+=d(B)+"</span>\n        </div>\n        ";return A}function j(E,D){var A="",C,B;A+='\n        <div class="dataset-datatype">\n            <label class="prompt">';B={hash:{},inverse:o.noop,fn:o.program(7,i,D),data:D};if(C=p.local){C=C.call(E,B)}else{C=E.local;C=typeof C===e?C.apply(E):C}if(!p.local){C=c.call(E,C,B)}if(C||C===0){A+=C}A+='</label>\n            <span class="value">';if(C=p.data_type){C=C.call(E,{hash:{},data:D})}else{C=E.data_type;C=typeof C===e?C.apply(E):C}A+=d(C)+"</span>\n        </div>\n        ";return A}function i(B,A){return"format"}function f(E,D){var A="",C,B;A+='\n        <div class="dataset-dbkey">\n            <label class="prompt">';B={hash:{},inverse:o.noop,fn:o.program(10,y,D),data:D};if(C=p.local){C=C.call(E,B)}else{C=E.local;C=typeof C===e?C.apply(E):C}if(!p.local){C=c.call(E,C,B)}if(C||C===0){A+=C}A+='</label>\n            <span class="value">\n                ';if(C=p.metadata_dbkey){C=C.call(E,{hash:{},data:D})}else{C=E.metadata_dbkey;C=typeof C===e?C.apply(E):C}A+=d(C)+"\n            </span>\n        </div>\n        ";return A}function y(B,A){return"database"}function x(D,C){var A="",B;A+='\n        <div class="dataset-info">\n            <span class="value">';if(B=p.misc_info){B=B.call(D,{hash:{},data:C})}else{B=D.misc_info;B=typeof B===e?B.apply(D):B}A+=d(B)+"</span>\n        </div>\n        ";return A}function w(D,C){var A="",B;A+='\n    <div class="tags-display"></div>\n    <div class="annotation-display"></div>\n\n    <div class="dataset-display-applications">\n        ';B=p.each.call(D,D.display_apps,{hash:{},inverse:o.noop,fn:o.program(15,v,C),data:C});if(B||B===0){A+=B}A+="\n\n        ";B=p.each.call(D,D.display_types,{hash:{},inverse:o.noop,fn:o.program(15,v,C),data:C});if(B||B===0){A+=B}A+='\n    </div>\n\n    <div class="dataset-peek">\n    ';B=p["if"].call(D,D.peek,{hash:{},inverse:o.noop,fn:o.program(19,s,C),data:C});if(B||B===0){A+=B}A+="\n    </div>\n\n    ";return A}function v(D,C){var A="",B;A+='\n        <div class="display-application">\n            <span class="display-application-location">';if(B=p.label){B=B.call(D,{hash:{},data:C})}else{B=D.label;B=typeof B===e?B.apply(D):B}A+=d(B)+'</span>\n            <span class="display-application-links">\n                ';B=p.each.call(D,D.links,{hash:{},inverse:o.noop,fn:o.program(16,u,C),data:C});if(B||B===0){A+=B}A+="\n            </span>\n        </div>\n        ";return A}function u(E,D){var A="",C,B;A+='\n                <a target="';if(C=p.target){C=C.call(E,{hash:{},data:D})}else{C=E.target;C=typeof C===e?C.apply(E):C}A+=d(C)+'" href="';if(C=p.href){C=C.call(E,{hash:{},data:D})}else{C=E.href;C=typeof C===e?C.apply(E):C}A+=d(C)+'">';B={hash:{},inverse:o.noop,fn:o.program(17,t,D),data:D};if(C=p.local){C=C.call(E,B)}else{C=E.local;C=typeof C===e?C.apply(E):C}if(!p.local){C=c.call(E,C,B)}if(C||C===0){A+=C}A+="</a>\n                ";return A}function t(C,B){var A;if(A=p.text){A=A.call(C,{hash:{},data:B})}else{A=C.text;A=typeof A===e?A.apply(C):A}return d(A)}function s(D,C){var A="",B;A+='\n        <pre class="peek">';if(B=p.peek){B=B.call(D,{hash:{},data:C})}else{B=D.peek;B=typeof B===e?B.apply(D):B}if(B||B===0){A+=B}A+="</pre>\n    ";return A}q+='<div class="dataset-body">\n    ';h=p["if"].call(r,r.body,{hash:{},inverse:o.program(3,m,z),fn:o.program(1,n,z),data:z});if(h||h===0){q+=h}q+="\n</div>";return q})})();(function(){var b=Handlebars.template,a=Handlebars.templates=Handlebars.templates||{};a["template-hda-skeleton"]=b(function(f,r,p,k,w){this.compilerInfo=[4,">= 1.0.0"];p=this.merge(p,f.helpers);w=w||{};var q="",h,e="function",d=this.escapeExpression,o=this,c=p.blockHelperMissing;function n(B,A){var x="",z,y;x+='\n        <div class="errormessagesmall">\n            ';y={hash:{},inverse:o.noop,fn:o.program(2,m,A),data:A};if(z=p.local){z=z.call(B,y)}else{z=B.local;z=typeof z===e?z.apply(B):z}if(!p.local){z=c.call(B,z,y)}if(z||z===0){x+=z}x+=":\n            ";y={hash:{},inverse:o.noop,fn:o.program(4,l,A),data:A};if(z=p.local){z=z.call(B,y)}else{z=B.local;z=typeof z===e?z.apply(B):z}if(!p.local){z=c.call(B,z,y)}if(z||z===0){x+=z}x+="\n        </div>\n        ";return x}function m(y,x){return"There was an error getting the data for this dataset"}function l(z,y){var x;if(x=p.error){x=x.call(z,{hash:{},data:y})}else{x=z.error;x=typeof x===e?x.apply(z):x}return d(x)}function j(A,z){var x="",y;x+="\n            ";y=p["if"].call(A,A.purged,{hash:{},inverse:o.program(10,v,z),fn:o.program(7,i,z),data:z});if(y||y===0){x+=y}x+="\n        ";return x}function i(B,A){var x="",z,y;x+='\n            <div class="warningmessagesmall"><strong>\n                ';y={hash:{},inverse:o.noop,fn:o.program(8,g,A),data:A};if(z=p.local){z=z.call(B,y)}else{z=B.local;z=typeof z===e?z.apply(B):z}if(!p.local){z=c.call(B,z,y)}if(z||z===0){x+=z}x+="\n            </strong></div>\n\n            ";return x}function g(y,x){return"This dataset has been deleted and removed from disk."}function v(B,A){var x="",z,y;x+='\n            <div class="warningmessagesmall"><strong>\n                ';y={hash:{},inverse:o.noop,fn:o.program(11,u,A),data:A};if(z=p.local){z=z.call(B,y)}else{z=B.local;z=typeof z===e?z.apply(B):z}if(!p.local){z=c.call(B,z,y)}if(z||z===0){x+=z}x+='\n                \n                \n                Click <a href="javascript:void(0);" class="dataset-undelete">here</a> to undelete it\n                or <a href="javascript:void(0);" class="dataset-purge">here</a> to immediately remove it from disk\n            </strong></div>\n            ';return x}function u(y,x){return"This dataset has been deleted."}function t(B,A){var x="",z,y;x+='\n        <div class="warningmessagesmall"><strong>\n            ';y={hash:{},inverse:o.noop,fn:o.program(14,s,A),data:A};if(z=p.local){z=z.call(B,y)}else{z=B.local;z=typeof z===e?z.apply(B):z}if(!p.local){z=c.call(B,z,y)}if(z||z===0){x+=z}x+='\n            \n            Click <a href="javascript:void(0);" class="dataset-unhide">here</a> to unhide it\n        </strong></div>\n        ';return x}function s(y,x){return"This dataset has been hidden."}q+='<div class="dataset hda">\n    <div class="dataset-warnings">\n        ';h=p["if"].call(r,r.error,{hash:{},inverse:o.noop,fn:o.program(1,n,w),data:w});if(h||h===0){q+=h}q+="\n\n        ";h=p["if"].call(r,r.deleted,{hash:{},inverse:o.noop,fn:o.program(6,j,w),data:w});if(h||h===0){q+=h}q+="\n\n        ";h=p.unless.call(r,r.visible,{hash:{},inverse:o.noop,fn:o.program(13,t,w),data:w});if(h||h===0){q+=h}q+='\n    </div>\n\n    <div class="dataset-primary-actions"></div>\n    <div class="dataset-title-bar clear">\n        <span class="dataset-state-icon state-icon"></span>\n        <div class="dataset-title">\n            <span class="hda-hid">';if(h=p.hid){h=h.call(r,{hash:{},data:w})}else{h=r.hid;h=typeof h===e?h.apply(r):h}q+=d(h)+'</span>\n            <span class="dataset-name">';if(h=p.name){h=h.call(r,{hash:{},data:w})}else{h=r.name;h=typeof h===e?h.apply(r):h}q+=d(h)+'</span>\n        </div>\n    </div>\n\n    <div class="dataset-body"></div>\n</div>';return q})})();(function(){var b=Handlebars.template,a=Handlebars.templates=Handlebars.templates||{};a["template-history-historyPanel-anon"]=b(function(g,r,p,k,u){this.compilerInfo=[4,">= 1.0.0"];p=this.merge(p,g.helpers);u=u||{};var q="",i,f,o=this,e="function",c=p.blockHelperMissing,d=this.escapeExpression;function n(z,y){var v="",x,w;v+='\n                <div class="history-name" title="';w={hash:{},inverse:o.noop,fn:o.program(2,m,y),data:y};if(x=p.local){x=x.call(z,w)}else{x=z.local;x=typeof x===e?x.apply(z):x}if(!p.local){x=c.call(z,x,w)}if(x||x===0){v+=x}v+='">\n                    ';if(x=p.name){x=x.call(z,{hash:{},data:y})}else{x=z.name;x=typeof x===e?x.apply(z):x}v+=d(x)+"\n                </div>\n            ";return v}function m(w,v){return"You must be logged in to edit your history name"}function l(y,x){var v="",w;v+='\n            <div class="history-size">';if(w=p.nice_size){w=w.call(y,{hash:{},data:x})}else{w=y.nice_size;w=typeof w===e?w.apply(y):w}v+=d(w)+"</div>\n            ";return v}function j(y,x){var v="",w;v+='\n            \n            <div class="';if(w=p.status){w=w.call(y,{hash:{},data:x})}else{w=y.status;w=typeof w===e?w.apply(y):w}v+=d(w)+'message">';if(w=p.message){w=w.call(y,{hash:{},data:x})}else{w=y.message;w=typeof w===e?w.apply(y):w}v+=d(w)+"</div>\n            ";return v}function h(w,v){return"You are over your disk quota"}function t(w,v){return"Tool execution is on hold until your disk usage drops below your allocated quota"}function s(w,v){return"Your history is empty. Click 'Get Data' on the left pane to start"}q+='<div class="history-controls">\n\n        <div class="history-title">\n            \n            ';i=p["if"].call(r,r.name,{hash:{},inverse:o.noop,fn:o.program(1,n,u),data:u});if(i||i===0){q+=i}q+='\n        </div>\n\n        <div class="history-subtitle clear">\n            ';i=p["if"].call(r,r.nice_size,{hash:{},inverse:o.noop,fn:o.program(4,l,u),data:u});if(i||i===0){q+=i}q+='\n        </div>\n\n        <div class="message-container">\n            ';i=p["if"].call(r,r.message,{hash:{},inverse:o.noop,fn:o.program(6,j,u),data:u});if(i||i===0){q+=i}q+='\n        </div>\n\n        <div class="quota-message errormessage">\n            ';f={hash:{},inverse:o.noop,fn:o.program(8,h,u),data:u};if(i=p.local){i=i.call(r,f)}else{i=r.local;i=typeof i===e?i.apply(r):i}if(!p.local){i=c.call(r,i,f)}if(i||i===0){q+=i}q+=".\n            ";f={hash:{},inverse:o.noop,fn:o.program(10,t,u),data:u};if(i=p.local){i=i.call(r,f)}else{i=r.local;i=typeof i===e?i.apply(r):i}if(!p.local){i=c.call(r,i,f)}if(i||i===0){q+=i}q+='.\n        </div>\n\n    </div>\n\n    \n    <div class="datasets-list"></div>\n\n    <div class="empty-history-message infomessagesmall">\n        ';f={hash:{},inverse:o.noop,fn:o.program(12,s,u),data:u};if(i=p.local){i=i.call(r,f)}else{i=r.local;i=typeof i===e?i.apply(r):i}if(!p.local){i=c.call(r,i,f)}if(i||i===0){q+=i}q+="\n    </div>";return q})})();(function(){var b=Handlebars.template,a=Handlebars.templates=Handlebars.templates||{};a["template-history-historyPanel"]=b(function(h,s,q,l,w){this.compilerInfo=[4,">= 1.0.0"];q=this.merge(q,h.helpers);w=w||{};var r="",i,f,p=this,e="function",c=q.blockHelperMissing,d=this.escapeExpression;function o(B,A){var x="",z,y;x+='\n            <div class="history-name" title="';y={hash:{},inverse:p.noop,fn:p.program(2,n,A),data:A};if(z=q.local){z=z.call(B,y)}else{z=B.local;z=typeof z===e?z.apply(B):z}if(!q.local){z=c.call(B,z,y)}if(z||z===0){x+=z}x+='">\n                ';if(z=q.name){z=z.call(B,{hash:{},data:A})}else{z=B.name;z=typeof z===e?z.apply(B):z}x+=d(z)+"\n            </div>\n            ";return x}function n(y,x){return"Click to rename history"}function m(A,z){var x="",y;x+='\n            <div class="history-size">';if(y=q.nice_size){y=y.call(A,{hash:{},data:z})}else{y=A.nice_size;y=typeof y===e?y.apply(A):y}x+=d(y)+"</div>\n            ";return x}function k(B,A){var x="",z,y;x+='\n        <div class="warningmessagesmall"><strong>\n            ';y={hash:{},inverse:p.noop,fn:p.program(7,j,A),data:A};if(z=q.local){z=z.call(B,y)}else{z=B.local;z=typeof z===e?z.apply(B):z}if(!q.local){z=c.call(B,z,y)}if(z||z===0){x+=z}x+="\n        </strong></div>\n        ";return x}function j(y,x){return"You are currently viewing a deleted history!"}function g(A,z){var x="",y;x+='\n            \n            <div class="';if(y=q.status){y=y.call(A,{hash:{},data:z})}else{y=A.status;y=typeof y===e?y.apply(A):y}x+=d(y)+'message">';if(y=q.message){y=y.call(A,{hash:{},data:z})}else{y=A.message;y=typeof y===e?y.apply(A):y}x+=d(y)+"</div>\n            ";return x}function v(y,x){return"You are over your disk quota"}function u(y,x){return"Tool execution is on hold until your disk usage drops below your allocated quota"}function t(y,x){return"Your history is empty. Click 'Get Data' on the left pane to start"}r+='<div class="history-controls">\n\n        <div class="history-title">\n            ';i=q["if"].call(s,s.name,{hash:{},inverse:p.noop,fn:p.program(1,o,w),data:w});if(i||i===0){r+=i}r+='\n        </div>\n\n        <div class="history-subtitle clear">\n            ';i=q["if"].call(s,s.nice_size,{hash:{},inverse:p.noop,fn:p.program(4,m,w),data:w});if(i||i===0){r+=i}r+='\n\n            <div class="history-secondary-actions">\n            </div>\n        </div>\n\n        ';i=q["if"].call(s,s.deleted,{hash:{},inverse:p.noop,fn:p.program(6,k,w),data:w});if(i||i===0){r+=i}r+='\n\n        <div class="message-container">\n            ';i=q["if"].call(s,s.message,{hash:{},inverse:p.noop,fn:p.program(9,g,w),data:w});if(i||i===0){r+=i}r+='\n        </div>\n\n        <div class="quota-message errormessage">\n            ';f={hash:{},inverse:p.noop,fn:p.program(11,v,w),data:w};if(i=q.local){i=i.call(s,f)}else{i=s.local;i=typeof i===e?i.apply(s):i}if(!q.local){i=c.call(s,i,f)}if(i||i===0){r+=i}r+=".\n            ";f={hash:{},inverse:p.noop,fn:p.program(13,u,w),data:w};if(i=q.local){i=i.call(s,f)}else{i=s.local;i=typeof i===e?i.apply(s):i}if(!q.local){i=c.call(s,i,f)}if(i||i===0){r+=i}r+='.\n        </div>\n        \n        <div class="tags-display"></div>\n        <div class="annotation-display"></div>\n\n    </div>\n\n    \n    <div class="datasets-list"></div>\n\n    <div class="empty-history-message infomessagesmall">\n        ';f={hash:{},inverse:p.noop,fn:p.program(15,t,w),data:w};if(i=q.local){i=i.call(s,f)}else{i=s.local;i=typeof i===e?i.apply(s):i}if(!q.local){i=c.call(s,i,f)}if(i||i===0){r+=i}r+="\n    </div>";return r})})();