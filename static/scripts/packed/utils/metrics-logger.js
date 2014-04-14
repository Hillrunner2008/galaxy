define([],function(){function h(z){z=z||{};var y=this;y.consoleLogger=z.consoleLogger||null;y._init(z);return y}h.ALL=0;h.DEBUG=10;h.INFO=20;h.WARN=30;h.ERROR=40;h.METRIC=50;h.NONE=100;h.defaultOptions={logLevel:h.NONE,consoleLevel:h.NONE,defaultNamespace:"Galaxy",clientPrefix:"client.",maxCacheSize:3000,postSize:1000,addTime:true,postUrl:"/api/metrics",getPingData:undefined,onServerResponse:undefined};h.prototype._init=function i(A){var z=this;z.options={};for(var y in h.defaultOptions){if(h.defaultOptions.hasOwnProperty(y)){z.options[y]=(A.hasOwnProperty(y))?(A[y]):(h.defaultOptions[y])}}z.options.logLevel=z._parseLevel(z.options.logLevel);z.options.consoleLevel=z._parseLevel(z.options.consoleLevel);z._sending=false;z._postSize=z.options.postSize;z._initCache();return z};h.prototype._initCache=function a(){this.cache=new w({maxSize:this.options.maxCacheSize})};h.prototype._parseLevel=function j(A){var z=typeof A;if(z==="number"){return A}if(z==="string"){var y=A.toUpperCase();if(h.hasOwnProperty(y)){return h[y]}}throw new Error("Unknown log level: "+A)};h.prototype.emit=function m(B,A,z){var y=this;A=A||y.options.defaultNamespace;if(!B||!z){return y}B=y._parseLevel(B);if(B>=y.options.logLevel){y._addToCache(B,A,z)}if(y.consoleLogger&&B>=y.options.consoleLevel){y._emitToConsole(B,A,z)}return y};h.prototype._addToCache=function b(D,A,z){this._emitToConsole("debug","MetricsLogger",["_addToCache:",arguments,this.options.addTime,this.cache.length()]);var y=this;try{var C=y.cache.add(y._buildEntry(D,A,z));if(C>=y._postSize){y._postCache()}}catch(B){if(y.options.consoleLevel<=h.WARN){console.warn("Metrics logger could not stringify logArguments:",A,z);console.error(B)}}return y};h.prototype._buildEntry=function r(B,z,y){this._emitToConsole("debug","MetricsLogger",["_buildEntry:",arguments]);var A={level:B,namespace:this.options.clientPrefix+z,args:y};if(this.options.addTime){A.time=new Date().toISOString()}return A};h.prototype._postCache=function s(B){B=B||{};this._emitToConsole("info","MetricsLogger",["_postCache",B,this._postSize]);if(!this.options.postUrl||this._sending){return jQuery.when({})}var A=this,D=B.count||A._postSize,y=A.cache.get(D),C=y.length,z=(typeof A.options.getPingData==="function")?(A.options.getPingData()):({});z.metrics=A._preprocessCache(y);A._sending=true;return jQuery.post(A.options.postUrl,z).always(function(){A._sending=false}).fail(function(){A._postSize=A.options.maxCacheSize}).done(function(E){if(typeof A.options.onServerResponse==="function"){A.options.onServerResponse(E)}A.cache.remove(C);console.debug("removed entries:",C,"size now:",A.cache.length());A._postSize=A.options.postSize})};h.prototype._preprocessCache=function f(y){return["[",(y.join(",\n")),"]"].join("\n")};h.prototype._emitToConsole=function c(C,B,A){var y=this;if(!y.consoleLogger){return y}var z=Array.prototype.slice.call(A,0);z.unshift(B);if(C>=h.METRIC&&typeof(y.consoleLogger.info)==="function"){return y.consoleLogger.info.apply(y.consoleLogger,z)}else{if(C>=h.ERROR&&typeof(y.consoleLogger.error)==="function"){return y.consoleLogger.error.apply(y.consoleLogger,z)}else{if(C>=h.WARN&&typeof(y.consoleLogger.warn)==="function"){y.consoleLogger.warn.apply(y.consoleLogger,z)}else{if(C>=h.INFO&&typeof(y.consoleLogger.info)==="function"){y.consoleLogger.info.apply(y.consoleLogger,z)}else{if(C>=h.DEBUG&&typeof(y.consoleLogger.debug)==="function"){y.consoleLogger.debug.apply(y.consoleLogger,z)}else{if(typeof(y.consoleLogger.log)==="function"){y.consoleLogger.log.apply(y.consoleLogger,z)}}}}}}return y};h.prototype.debug=function l(){this.emit(h.DEBUG,this.options.defaultNamespace,arguments)};h.prototype.log=function g(){this.emit(1,this.options.defaultNamespace,arguments)};h.prototype.info=function u(){this.emit(h.INFO,this.options.defaultNamespace,arguments)};h.prototype.warn=function t(){this.emit(h.WARN,this.options.defaultNamespace,arguments)};h.prototype.error=function p(){this.emit(h.ERROR,this.options.defaultNamespace,arguments)};h.prototype.metric=function n(){this.emit(h.METRIC,this.options.defaultNamespace,arguments)};function w(z){var y=this;y._cache=[];return y._init(z||{})}w.defaultOptions={maxSize:5000};w.prototype._init=function i(y){this.maxSize=y.maxSize||w.defaultOptions.maxSize;return this};w.prototype.add=function k(A){var z=this,y=(z.length()+1)-z.maxSize;if(y>0){z.remove(y)}z._cache.push(z._preprocessEntry(A));return z.length()};w.prototype._preprocessEntry=function q(y){return JSON.stringify(y)};w.prototype.length=function e(){return this._cache.length};w.prototype.get=function v(y){return this._cache.slice(0,y)};w.prototype.remove=function x(y){return this._cache.splice(0,y)};w.prototype.stringify=function o(y){return["[",(this.get(y).join(",\n")),"]"].join("\n")};w.prototype.print=function d(){this._cache.forEach(function(y){console.log(y)})};return{MetricsLogger:h,LoggingCache:w}});