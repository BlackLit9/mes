(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-d63307c0"],{1:function(e,t){},"129f":function(e,t){e.exports=Object.is||function(e,t){return e===t?0!==e||1/e===1/t:e!=e&&t!=t}},2:function(e,t){},"2f91f":function(e,t,n){"use strict";n.r(t);var a=function(){var e=this,t=e.$createElement,n=e._self._c||t;return n("div",{directives:[{name:"loading",rawName:"v-loading",value:e.loading,expression:"loading"}]},[n("el-form",{attrs:{inline:!0}},[n("el-form-item",{attrs:{label:"时间:"}},[n("el-date-picker",{attrs:{type:"daterange","range-separator":"至","start-placeholder":"开始日期","end-placeholder":"结束日期","value-format":"yyyy-MM-dd",clearable:!0},on:{change:e.setDataValue},model:{value:e.dataValue,callback:function(t){e.dataValue=t},expression:"dataValue"}})],1),e.isDialog?e._e():n("div",[n("el-form-item",{attrs:{label:"物料类型:"}},[n("materialTypeSelect",{on:{changeSelect:e.changeMaterialType}})],1),n("el-form-item",{attrs:{label:"物料编码:"}},[n("materialCodeSelect",{attrs:{"is-all-obj":!0,"label-name":"no"},on:{changeSelect:e.changeMaterialCode}})],1),n("el-form-item",{attrs:{label:"物料名称:"}},[n("materialCodeSelect",{attrs:{"is-all-obj":!0},on:{changeSelect:e.changeMaterialName}})],1),n("el-form-item",{attrs:{label:"库存位:"}},[n("inventoryPosition",{on:{changSelect:e.changeInventoryPosition}})],1),n("el-form-item",[1===e.currentRoute&&e.checkPermission(["outbound_history","export"])?n("el-button",{on:{click:function(t){return e.exportTable("备品备件出库履历")}}},[e._v("导出表格")]):e._e(),2===e.currentRoute&&e.checkPermission(["inbound_history","export"])?n("el-button",{on:{click:function(t){return e.exportTable("备品备件入库履历")}}},[e._v("导出表格")]):e._e(),3===e.currentRoute&&e.checkPermission(["stock_history","export"])?n("el-button",{on:{click:function(t){return e.exportTable("备品备件盘点履历")}}},[e._v("导出表格")]):e._e()],1)],1),1===e.currentRoute?n("el-form-item",{attrs:{label:"状态:"}},[n("el-select",{attrs:{placeholder:"请选择",clearable:""},on:{change:e.changeStatus},model:{value:e.search.status,callback:function(t){e.$set(e.search,"status",t)},expression:"search.status"}},e._l(e.statusList,(function(e){return n("el-option",{key:e.id,attrs:{label:e.name,value:e.id}})})),1)],1):e._e()],1),n("el-table",{attrs:{id:"out-table",data:e.tableData,border:""}},[n("el-table-column",{attrs:{type:"index",width:"50",label:"No"}}),n("el-table-column",{attrs:{prop:"fin_time",label:"时间",width:"90"}}),n("el-table-column",{attrs:{prop:"type",label:"类型",width:"80"}}),n("el-table-column",{attrs:{prop:"spare_type",label:"物料类型"}}),n("el-table-column",{attrs:{prop:"spare_no",label:"物料编码"}}),n("el-table-column",{attrs:{prop:"spare_name",label:"物料名称"}}),n("el-table-column",{attrs:{prop:"location",label:"库存位"}}),1===e.currentRoute&&e.checkPermission(["outbound_history","price"])||2===e.currentRoute&&e.checkPermission(["inbound_history","price"])?n("el-table-column",{attrs:{prop:"unit_count",label:"单价（元）"}}):e._e(),1===e.currentRoute&&e.checkPermission(["outbound_history","price"])||2===e.currentRoute&&e.checkPermission(["inbound_history","price"])?n("el-table-column",{attrs:{prop:"cost",label:"总价（元）"}}):e._e(),1===e.currentRoute?n("el-table-column",{attrs:{prop:"purpose",label:"用途","show-overflow-tooltip":""}}):e._e(),1===e.currentRoute?n("el-table-column",{attrs:{prop:"reason",label:"出库原因","show-overflow-tooltip":""}}):e._e(),3!==e.currentRoute?n("el-table-column",{attrs:{prop:"qty",label:"数量",width:"80"}}):e._e(),3!==e.currentRoute?n("el-table-column",{attrs:{prop:"dst_qty",label:"剩余数量",width:"100"}}):e._e(),3===e.currentRoute?n("el-table-column",{attrs:{prop:"src_qty",label:"变更前数量"}}):e._e(),3===e.currentRoute?n("el-table-column",{attrs:{prop:"dst_qty",label:"变更后数量"}}):e._e(),n("el-table-column",{attrs:{prop:"unit",label:"单位"}}),1===e.currentRoute?n("el-table-column",{attrs:{prop:"created_username",label:"出库员"}}):e._e(),1===e.currentRoute?n("el-table-column",{attrs:{prop:"receive_user",label:"领用人"}}):e._e(),2===e.currentRoute?n("el-table-column",{attrs:{prop:"created_username",label:"入库员"}}):e._e(),3===e.currentRoute?n("el-table-column",{attrs:{prop:"reason",label:"备注","show-overflow-tooltip":""}}):e._e(),3===e.currentRoute?n("el-table-column",{attrs:{prop:"created_username",label:"操作人"}}):e._e(),1===e.currentRoute?n("el-table-column",{attrs:{prop:"created_username",label:"状态"},scopedSlots:e._u([{key:"default",fn:function(t){var n=t.row;return[e._v(" "+e._s(1===n.status?"完成":"注销")+" ")]}}],null,!1,285612918)}):e._e(),1===e.currentRoute&&e.checkPermission(["outbound_history","cancel"])?n("el-table-column",{attrs:{label:"操作",width:"80"},scopedSlots:e._u([{key:"default",fn:function(t){return[1===t.row.status?n("el-button",{attrs:{size:"mini"},on:{click:function(n){return e.revokeFun(t.row,t.$index)}}},[e._v("撤销")]):e._e()]}}],null,!1,1314307934)}):e._e()],1),n("page",{attrs:{"old-page":!1,total:e.total,"current-page":e.search.page},on:{currentChange:e.currentChange}})],1)},r=[],o=(n("caad"),n("b0c0"),n("ac1f"),n("841c"),n("96cf"),n("1da1")),i=n("8041"),c=n("a0e0"),l=n("5c1c"),s=n("3e51"),u=n("ed08"),d=n("d585"),h={components:{page:s["a"],inventoryPosition:i["a"],materialCodeSelect:l["a"],materialTypeSelect:c["a"]},props:{isDialog:{type:Boolean,default:!1},show:{type:Boolean,default:!1},dialogObj:{type:Object,default:function(){return{}}}},data:function(){return{search:{page:1,page_size:10,type:1},dataValue:[Object(u["d"])(),Object(u["d"])()],tableData:[],total:0,loading:!1,statusList:[{id:1,name:"完成"},{id:2,name:"注销"}]}},watch:{show:function(e){if(e){if(this.isDialog){var t={spare_no:this.dialogObj.spare_no,location_no:this.dialogObj.location_no};Object.assign(this.search,t)}this.dataValue=[Object(u["d"])(),Object(u["d"])()],this.search.begin_time=Object(u["d"])(),this.search.end_time=Object(u["d"])(),this.getList()}}},created:function(){if(this.search.begin_time=Object(u["d"])(),this.search.end_time=Object(u["d"])(),["备品备件出库履历","备品备件出库管理"].includes(this.$route.meta.title)?(this.currentRoute=1,this.search.type="出库"):["备品备件入库履历","备品备件入库管理"].includes(this.$route.meta.title)?(this.currentRoute=2,this.search.type="入库"):(this.currentRoute=3,this.search.type="数量变更"),this.isDialog){var e={spare_no:this.dialogObj.spare_no,location_no:this.dialogObj.location_no};Object.assign(this.search,e)}this.getList()},methods:{checkPermission:u["a"],getList:function(){var e=this;return Object(o["a"])(regeneratorRuntime.mark((function t(){var n;return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:return t.prev=0,e.loading=!0,t.next=4,Object(d["f"])("get",null,{params:e.search});case 4:n=t.sent,e.tableData=n.results,e.total=n.count,e.loading=!1,t.next=13;break;case 10:t.prev=10,t.t0=t["catch"](0),e.loading=!1;case 13:case"end":return t.stop()}}),t,null,[[0,10]])})))()},changeMaterialType:function(e){this.search.type_name=e?e.name:null,this.search.page=1,this.getList()},changeInventoryPosition:function(e){this.search.location_no=e?e.no:null,this.search.page=1,this.getList()},setDataValue:function(e){this.search.begin_time=e?e[0]:"",this.search.end_time=e?e[1]:"",this.search.page=1,this.getList()},changeMaterialCode:function(e){this.search.spare_no=e?e.no:null,this.search.page=1,this.getList()},changeMaterialName:function(e){this.search.spare_name=e?e.name:null,this.search.page=1,this.getList()},currentChange:function(e,t){this.search.page=e,this.search.page_size=t,this.getList()},exportTable:function(e){Object(u["c"])(e)},changeStatus:function(e){this.search.page=1,this.getList()},revokeFun:function(e,t){var n=this;this.$confirm("确定撤销?","提示",{confirmButtonText:"确定",cancelButtonText:"取消",type:"warning"}).then(Object(o["a"])(regeneratorRuntime.mark((function t(){return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:return t.next=2,Object(d["d"])("patch",e.id);case 2:n.$message.success("撤销成功"),n.search.page=1,n.getList();case 5:case"end":return t.stop()}}),t)}))))}}},p=h,b=n("2877"),f=Object(b["a"])(p,a,r,!1,null,null,null);t["default"]=f.exports},3:function(e,t){},"6dfa":function(e,t,n){"use strict";n.d(t,"b",(function(){return o})),n.d(t,"c",(function(){return i})),n.d(t,"d",(function(){return c})),n.d(t,"a",(function(){return l}));var a=n("b775"),r=n("99b1");function o(e){return Object(a["a"])({url:r["a"].MaterialLocationBinding,method:"get",params:e})}function i(e){return Object(a["a"])({url:r["a"].MaterialLocationBinding,method:"post",data:e})}function c(e,t){return Object(a["a"])({url:r["a"].MaterialLocationBinding+t+"/",method:"put",data:e})}function l(e){return Object(a["a"])({url:r["a"].MaterialLocationBinding+e+"/",method:"delete"})}},"841c":function(e,t,n){"use strict";var a=n("d784"),r=n("825a"),o=n("1d80"),i=n("129f"),c=n("14c3");a("search",1,(function(e,t,n){return[function(t){var n=o(this),a=void 0==t?void 0:t[e];return void 0!==a?a.call(t,n):new RegExp(t)[e](String(n))},function(e){var a=n(t,e,this);if(a.done)return a.value;var o=r(e),l=String(this),s=o.lastIndex;i(s,0)||(o.lastIndex=0);var u=c(o,l);return i(o.lastIndex,s)||(o.lastIndex=s),null===u?-1:u.index}]}))},d585:function(e,t,n){"use strict";n.d(t,"a",(function(){return o})),n.d(t,"e",(function(){return i})),n.d(t,"g",(function(){return c})),n.d(t,"c",(function(){return l})),n.d(t,"f",(function(){return s})),n.d(t,"b",(function(){return u})),n.d(t,"i",(function(){return d})),n.d(t,"h",(function(){return h})),n.d(t,"d",(function(){return p}));var a=n("b775"),r=n("99b1");function o(e,t){var n=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},o={url:t?r["a"].LocationNameList+t+"/":r["a"].LocationNameList,method:e};return Object.assign(o,n),Object(a["a"])(o)}function i(e,t){var n=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},o={url:t?r["a"].SpareInventory+t+"/":r["a"].SpareInventory,method:e};return Object.assign(o,n),Object(a["a"])(o)}function c(e,t){var n=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},o={url:(t?r["a"].SpareInventory+t+"/":r["a"].SpareInventory)+"check_storage/",method:e};return Object.assign(o,n),Object(a["a"])(o)}function l(e,t){var n=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},o={url:(t?r["a"].SpareInventory+t+"/":r["a"].SpareInventory)+"put_storage/",method:e};return Object.assign(o,n),Object(a["a"])(o)}function s(e,t){var n=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},o={url:t?r["a"].SpareInventoryLog+t+"/":r["a"].SpareInventoryLog,method:e};return Object.assign(o,n),Object(a["a"])(o)}function u(e,t){var n=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},o={url:(t?r["a"].SpareInventory+t+"/":r["a"].SpareInventory)+"out_storage/",method:e};return Object.assign(o,n),Object(a["a"])(o)}function d(e,t){var n=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},o={url:t?r["a"].SparepartsSpareType+t+"/":r["a"].SparepartsSpareType,method:e};return Object.assign(o,n),Object(a["a"])(o)}function h(e,t){var n=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},o={url:t?r["a"].SparepartsSpare+t+"/":r["a"].SparepartsSpare,method:e};return Object.assign(o,n),Object(a["a"])(o)}function p(e,t){var n=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},o={url:(t?r["a"].SpareInventoryLog+t+"/":r["a"].SpareInventoryLog)+"revocation_log/",method:e};return Object.assign(o,n),Object(a["a"])(o)}},ed08:function(e,t,n){"use strict";n.d(t,"d",(function(){return s})),n.d(t,"b",(function(){return d})),n.d(t,"a",(function(){return h})),n.d(t,"c",(function(){return p}));n("4160"),n("caad"),n("c975"),n("45fc"),n("a9e3"),n("b64b"),n("d3b7"),n("4d63"),n("ac1f"),n("25f0"),n("2532"),n("4d90"),n("5319"),n("1276"),n("159b");var a=n("53ca"),r=n("4360"),o=n("21a6"),i=n.n(o),c=n("1146"),l=n.n(c);function s(e,t,n){var a=e?new Date(e):new Date,r={y:a.getFullYear(),m:u(a.getMonth()+1),d:u(a.getDate()),h:u(a.getHours()),i:u(a.getMinutes()),s:u(a.getSeconds()),a:u(a.getDay())};return t?r.y+"-"+r.m+"-"+r.d+" "+r.h+":"+r.i+":"+r.s:n&&"continuation"===n?r.y+r.m+r.d+r.h+r.i+r.s:r.y+"-"+r.m+"-"+r.d}function u(e){return e=Number(e),e<10?"0"+e:e}function d(e){if(!e&&"object"!==Object(a["a"])(e))throw new Error("error arguments","deepClone");var t=e.constructor===Array?[]:{};return Object.keys(e).forEach((function(n){e[n]&&"object"===Object(a["a"])(e[n])?t[n]=d(e[n]):t[n]=e[n]})),t}function h(e){if(e&&e instanceof Array&&e.length>0){var t=r["a"].getters&&r["a"].getters.permission,n=t[e[0]];if(!n||0===n.length)return;var a=n.some((function(t){return t===e[1]}));return a}return console.error("need roles! Like v-permission=\"['admin','editor']\""),!1}function p(e){var t=l.a.utils.table_to_book(document.querySelector("#out-table"),{raw:!0}),n=l.a.write(t,{bookType:"xlsx",bookSST:!0,type:"array"});try{i.a.saveAs(new Blob([n],{type:"application/octet-stream"}),e+".xlsx")}catch(a){"undefined"!==typeof console&&console.log(a,n)}return n}}}]);