var hidden_width=7;var border_tweak=9;var jq=jQuery;function ensure_dd_helper(){if(jq("#DD-helper").length==0){$("<div id='DD-helper'/>").css({background:"white",opacity:0,zIndex:9000,position:"absolute",top:0,left:0,width:"100%",height:"100%"}).appendTo("body").hide()}}function make_left_panel(f,b,c){var e=false;var d=null;resize=function(g){var h=g;if(g<0){g=0}jq(f).css("width",g);jq(c).css("left",h);jq(b).css("left",g+7);if(document.recalc){document.recalc()}};toggle=function(){if(e){jq(c).removeClass("hover");jq(c).animate({left:d},"fast");jq(f).css("left",-d).show().animate({left:0},"fast",function(){resize(d);jq(c).removeClass("hidden")});e=false}else{d=jq(c).position().left;jq(b).css("left",hidden_width);if(document.recalc){document.recalc()}jq(c).removeClass("hover");jq(f).animate({left:-d},"fast");jq(c).animate({left:-1},"fast",function(){jq(this).addClass("hidden")});e=true}};jq(c).hover(function(){jq(this).addClass("hover")},function(){jq(this).removeClass("hover")}).draggable({start:function(g,h){jq("#DD-helper").show()},stop:function(g,h){jq("#DD-helper").hide();return false},drag:function(g,h){x=h.position.left;x=Math.min(400,Math.max(100,x));if(e){jq(f).css("left",0);jq(c).removeClass("hidden");e=false}resize(x);h.position.left=x;h.position.top=$(this).data("draggable").originalPosition.top},click:function(){toggle()}}).find("div").show();var a=function(g){if((e&&g=="show")||(!e&&g=="hide")){toggle()}};return{force_panel:a}}function make_right_panel(a,e,h){var j=false;var g=false;var c=null;var d=function(k){jq(a).css("width",k);jq(e).css("right",k+9);jq(h).css("right",k).css("left","");if(document.recalc){document.recalc()}};var i=function(){if(j){jq(h).removeClass("hover");jq(h).animate({right:c},"fast");jq(a).css("right",-c).show().animate({right:0},"fast",function(){d(c);jq(h).removeClass("hidden")});j=false}else{c=jq(document).width()-jq(h).position().left-border_tweak;jq(e).css("right",hidden_width+1);if(document.recalc){document.recalc()}jq(h).removeClass("hover");jq(a).animate({right:-c},"fast");jq(h).animate({right:-1},"fast",function(){jq(this).addClass("hidden")});j=true}g=false};var b=function(k){var l=jq(e).width()-(j?c:0);if(l<k){if(!j){i();g=true}}else{if(g){i();g=false}}};jq(h).hover(function(){jq(this).addClass("hover")},function(){jq(this).removeClass("hover")}).draggable({start:function(k,l){jq("#DD-helper").show()},stop:function(k,l){x=l.position.left;w=jq(window).width();x=Math.min(w-100,x);x=Math.max(w-400,x);d(w-x-border_tweak);jq("#DD-helper").hide();return false},click:function(){i()},drag:function(k,l){x=l.position.left;w=jq(window).width();x=Math.min(w-100,x);x=Math.max(w-400,x);if(j){jq(a).css("right",0);jq(h).removeClass("hidden");j=false}d(w-x-border_tweak);l.position.left=x;l.position.top=$(this).data("draggable").originalPosition.top}}).find("div").show();var f=function(k){if((j&&k=="show")||(!j&&k=="hide")){i()}};return{handle_minwidth_hint:b,force_panel:f}}function hide_modal(){$(".dialog-box-container").fadeOut(function(){$("#overlay").hide()})}function show_modal(f,c,e,d){$(".dialog-box").find(".title").html(f);var a=$(".dialog-box").find(".buttons").html("");if(e){$.each(e,function(b,g){a.append($("<button/>").text(b).click(g));a.append(" ")});a.show()}else{a.hide()}var a=$(".dialog-box").find(".extra_buttons").html("");if(d){$.each(d,function(b,g){a.append($("<button/>").text(b).click(g));a.append(" ")});a.show()}else{a.hide()}if(c=="progress"){c=$("<img src='../images/yui/rel_interstitial_loading.gif')' />")}$(".dialog-box").find(".body").html(c);if(!$(".dialog-box-container").is(":visible")){$("#overlay").show();$(".dialog-box-container").fadeIn()}}function make_popupmenu(d,b){var a=$("<div class='popupmenu'><div class='popupmenu-top'><div class='popupmenu-top-inner'/></div></div>").appendTo("body");$.each(b,function(g,f){$("<div class='popupmenu-item' />").html(g).click(f).appendTo(a)});var c=function(){$(a).unbind().hide();$("#popup-helper").unbind().hide()};var e=function(){var f=$(d).offset();$("#popup-helper").mousedown(c).show();$(a).click(c).css({top:-1000}).show().css({top:f.top+$(d).height()+9,left:f.left+$(d).width()-$(a).width()})};$(d).click(e)}$(function(){$("span.tab").each(function(){var a=$(this).children("div.submenu");if(a.length>0){if($.browser.msie){a.prepend("<iframe style=\"position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; filter:Alpha(Opacity='0');\"></iframe>")}$(this).hoverIntent(function(){a.show()},function(){a.hide()});a.click(function(){a.hide()})}})});function user_changed(a,b){if(a){$(".loggedin-only").show();$(".loggedout-only").hide();$("#user-email").text(a);if(b){$(".admin-only").show()}}else{$(".loggedin-only").hide();$(".loggedout-only").show();$(".admin-only").hide()}};