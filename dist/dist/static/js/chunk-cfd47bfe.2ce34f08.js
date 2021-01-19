(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-cfd47bfe"],{1:function(e,t){},2:function(e,t){},3:function(e,t){},a6a4:function(e,t,a){"use strict";a.r(t);var l=function(){var e=this,t=e.$createElement,a=e._self._c||t;return a("div",{staticStyle:{"margin-top":"25px"}},[a("el-form",{attrs:{inline:!0}},[a("el-form-item",{attrs:{label:"日期"}},[a("el-date-picker",{attrs:{type:"date","value-format":"yyyy-MM-dd",placeholder:"选择日期",format:"yyyy-MM-dd"},on:{change:e.planDateChange},model:{value:e.planDate,callback:function(t){e.planDate=t},expression:"planDate"}})],1),a("el-form-item",{attrs:{label:"原材料类别"}},[a("el-select",{attrs:{clearable:"",placeholder:"请选择"},on:{change:e.materialTypeChange,"visible-change":e.materialTypeVisibleChange},model:{value:e.materialType,callback:function(t){e.materialType=t},expression:"materialType"}},e._l(e.materialTypeOptions,(function(e){return a("el-option",{key:e.global_name,attrs:{label:e.global_name,value:e.global_name}})})),1)],1),a("el-form-item",{attrs:{label:"原材料名称"}},[a("el-input",{on:{input:e.materialNameChanged},model:{value:e.materialName,callback:function(t){e.materialName=t},expression:"materialName"}})],1)],1),a("el-table",{staticStyle:{width:"100%"},attrs:{data:e.tableData,border:""}},[a("el-table-column",{attrs:{label:"S",prop:"unit",width:"35"}}),a("el-table-column",{attrs:{type:"index",label:"No"}}),a("el-table-column",{attrs:{prop:"material_type",label:"原材料类别"}}),a("el-table-column",{attrs:{prop:"material_no",label:"原材料代码"}}),a("el-table-column",{attrs:{prop:"material_name",label:"原材料名称"}}),a("el-table-column",{attrs:{prop:"storage_weight",label:"原材料库存（Kg）",width:"140px"}}),a("el-table-column",{attrs:{align:"center",label:"原材料需要量（Kg）"}},[a("el-table-column",{attrs:{prop:"class_details.早班",label:"早班",width:"75px"}}),a("el-table-column",{attrs:{prop:"class_details.中班",label:"中班",width:"75px"}}),a("el-table-column",{attrs:{prop:"class_details.夜班",label:"夜班",width:"75px"}}),a("el-table-column",{attrs:{label:"总计",width:"80px"},scopedSlots:e._u([{key:"default",fn:function(t){return[a("span",{domProps:{textContent:e._s((t.row.class_details.早班?t.row.class_details.早班:0)+(t.row.class_details.中班?t.row.class_details.中班:0)+(t.row.class_details.夜班?t.row.class_details.夜班:0))}})]}}])})],1),a("el-table-column",{attrs:{align:"center",label:"领料计划（Kg）"}},[a("el-table-column",{attrs:{label:"早班",width:"75px"}}),a("el-table-column",{attrs:{label:"中班",width:"75px"}}),a("el-table-column",{attrs:{label:"夜班",width:"75px"}}),a("el-table-column",{attrs:{label:"总计",width:"80px"}})],1)],1),a("page",{attrs:{total:e.total,"current-page":e.getParams.page},on:{currentChange:e.currentChange}})],1)},n=[],r=a("b775"),i=a("99b1");function o(e){return Object(r["a"])({url:i["a"].MaterialDemanded,method:"get",params:e})}function s(e){return Object(r["a"])({url:i["a"].GlobalCodesUrl,method:"get",params:e})}var c=a("3e51"),u=a("ed08"),m={components:{page:c["a"]},data:function(){return{tableData:[],planDate:Object(u["d"])(),materialType:"",materialName:"",materialTypeOptions:[],getParams:{page:1},currentPage:1,total:0}},created:function(){this.getMaterialDemanded()},methods:{beforeGetData:function(){this.getParams["plan_date"]=this.planDate,this.getParams["material_type"]=this.materialType,this.getParams["material_name"]=this.materialName},planDateChange:function(){this.getParams.page=1,this.beforeGetData(),this.getMaterialDemanded()},materialTypeVisibleChange:function(e){e&&this.getMaterialType()},materialTypeChange:function(){this.getParams.page=1,this.beforeGetData(),this.getMaterialDemanded()},materialNameChanged:function(){this.getParams.page=1,this.beforeGetData(),this.getMaterialDemanded()},getMaterialDemanded:function(){var e=this;this.beforeGetData(),o(this.getParams).then((function(t){e.tableData=t.results,e.total=t.count}))},getMaterialType:function(){var e=this;s({class_name:"原材料类别"}).then((function(t){e.materialTypeOptions=t.results}))},currentChange:function(e){this.getParams.page=e,this.getMaterialDemanded()}}},p=m,d=a("2877"),b=Object(d["a"])(p,l,n,!1,null,"66b9e39e",null);t["default"]=b.exports},ed08:function(e,t,a){"use strict";a.d(t,"d",(function(){return c})),a.d(t,"b",(function(){return m})),a.d(t,"a",(function(){return p})),a.d(t,"c",(function(){return d}));a("4160"),a("caad"),a("c975"),a("45fc"),a("a9e3"),a("b64b"),a("d3b7"),a("4d63"),a("ac1f"),a("25f0"),a("2532"),a("4d90"),a("5319"),a("1276"),a("159b");var l=a("53ca"),n=a("4360"),r=a("21a6"),i=a.n(r),o=a("1146"),s=a.n(o);function c(e,t,a){var l=e?new Date(e):new Date,n={y:l.getFullYear(),m:u(l.getMonth()+1),d:u(l.getDate()),h:u(l.getHours()),i:u(l.getMinutes()),s:u(l.getSeconds()),a:u(l.getDay())};return t?n.y+"-"+n.m+"-"+n.d+" "+n.h+":"+n.i+":"+n.s:a&&"continuation"===a?n.y+n.m+n.d+n.h+n.i+n.s:n.y+"-"+n.m+"-"+n.d}function u(e){return e=Number(e),e<10?"0"+e:e}function m(e){if(!e&&"object"!==Object(l["a"])(e))throw new Error("error arguments","deepClone");var t=e.constructor===Array?[]:{};return Object.keys(e).forEach((function(a){e[a]&&"object"===Object(l["a"])(e[a])?t[a]=m(e[a]):t[a]=e[a]})),t}function p(e){if(e&&e instanceof Array&&e.length>0){var t=n["a"].getters&&n["a"].getters.permission,a=t[e[0]];if(!a||0===a.length)return;var l=a.some((function(t){return t===e[1]}));return l}return console.error("need roles! Like v-permission=\"['admin','editor']\""),!1}function d(e){var t=s.a.utils.table_to_book(document.querySelector("#out-table"),{raw:!0}),a=s.a.write(t,{bookType:"xlsx",bookSST:!0,type:"array"});try{i.a.saveAs(new Blob([a],{type:"application/octet-stream"}),e+".xlsx")}catch(l){"undefined"!==typeof console&&console.log(l,a)}return a}}}]);