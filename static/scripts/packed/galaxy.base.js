$.fn.makeAbsolute=function(a){return this.each(function(){var b=$(this);var c=b.position();b.css({position:"absolute",marginLeft:0,marginTop:0,top:c.top,left:c.left,right:$(window).width()-(c.left+b.width())});if(a){b.remove().appendTo("body")}})};function ensure_popup_helper(){if($("#popup-helper").length===0){$("<div id='popup-helper'/>").css({background:"white",opacity:0,zIndex:15000,position:"absolute",top:0,left:0,width:"100%",height:"100%"}).appendTo("body").hide()}}function attach_popupmenu(b,d){var a=function(){d.unbind().hide();$("#popup-helper").unbind("click.popupmenu").hide()};var c=function(g){$("#popup-helper").bind("click.popupmenu",a).show();d.click(a).css({left:0,top:-1000}).show();var f=g.pageX-d.width()/2;f=Math.min(f,$(document).scrollLeft()+$(window).width()-$(d).width()-20);f=Math.max(f,$(document).scrollLeft()+20);d.css({top:g.pageY-5,left:f});return false};$(b).click(c)}function make_popupmenu(c,b){ensure_popup_helper();var a=$("<ul id='"+c.attr("id")+"-menu'></ul>");$.each(b,function(f,e){if(e){$("<li/>").html(f).click(e).appendTo(a)}else{$("<li class='head'/>").html(f).appendTo(a)}});var d=$("<div class='popmenu-wrapper'>");d.append(a).append("<div class='overlay-border'>").css("position","absolute").appendTo("body").hide();attach_popupmenu(c,d)}function make_popup_menus(){jQuery("div[popupmenu]").each(function(){var c={};$(this).find("a").each(function(){var b=$(this).attr("confirm"),d=$(this).attr("href"),e=$(this).attr("target");c[$(this).text()]=function(){if(!b||confirm(b)){var g=window;if(e=="_parent"){g=window.parent}else{if(e=="_top"){g=window.top}}g.location=d}}});var a=$("#"+$(this).attr("popupmenu"));make_popupmenu(a,c);$(this).remove();a.addClass("popup").show()})}function array_length(b){if(b.length){return b.length}var c=0;for(var a in b){c++}return c}function replace_dbkey_select(){var c=$("select[name=dbkey]");var d=c.attr("value");if(c.length!==0){var e=$("<input id='dbkey-input' type='text'></input>");e.attr("size",40);e.attr("name",c.attr("name"));e.click(function(){var g=$(this).attr("value");$(this).attr("value","Loading...");$(this).showAllInCache();$(this).attr("value",g);$(this).select()});var b=[];var a={};c.children("option").each(function(){var h=$(this).text();var g=$(this).attr("value");if(g=="?"){return}b.push(h);a[h]=g;a[g]=g;if(g==d){e.attr("value",h)}});if(e.attr("value")==""){e.attr("value","Click to Search or Select Build")}var f={selectFirst:false,autoFill:false,mustMatch:false,matchContains:true,max:1000,minChars:0,hideForLessThanMinChars:false};e.autocomplete(b,f);c.replaceWith(e);$("form").submit(function(){var i=$("#dbkey-input");if(i.length!==0){var h=i.attr("value");var g=a[h];if(g!==null&&g!==undefined){i.attr("value",g)}else{if(d!=""){i.attr("value",d)}else{i.attr("value","?")}}}})}}function async_save_text(d,f,e,a,c,h,i,g,b){if(c===undefined){c=30}if(i===undefined){i=4}$("#"+d).live("click",function(){if($("#renaming-active").length>0){return}var l=$("#"+f),k=l.text(),j;if(h){j=$("<textarea></textarea>").attr({rows:i,cols:c}).text(k)}else{j=$("<input type='text'></input>").attr({value:k,size:c})}j.attr("id","renaming-active");j.blur(function(){$(this).remove();l.show();if(b){b(j)}});j.keyup(function(n){if(n.keyCode===27){$(this).trigger("blur")}else{if(n.keyCode===13){var m={};m[a]=$(this).val();$(this).trigger("blur");$.ajax({url:e,data:m,error:function(){alert("Text editing for elt "+f+" failed")},success:function(o){l.text(o);if(b){b(j)}}})}}});if(g){g(j)}l.hide();j.insertAfter(l);j.focus();j.select();return})}$(document).ready(function(){$("a[confirm]").click(function(){return confirm($(this).attr("confirm"))});if($.fn.tipsy){$(".tooltip").tipsy({gravity:"s"})}make_popup_menus()});