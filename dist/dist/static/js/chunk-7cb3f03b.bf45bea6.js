(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-7cb3f03b"],{8168:function(e,t,a){"use strict";a.r(t);var r=function(){var e=this,t=e.$createElement,a=e._self._c||t;return a("div",[a("el-form",{attrs:{inline:!0}},[a("el-form-item",{attrs:{label:"原材料类别"}},[a("el-select",{attrs:{clearable:"",placeholder:"请选择"},on:{"visible-change":e.materialTypeChange,change:e.changeSearch},model:{value:e.materialType,callback:function(t){e.materialType=t},expression:"materialType"}},e._l(e.materialTypeOptions,(function(e){return a("el-option",{key:e.global_name,attrs:{label:e.global_name,value:e.global_name}})})),1)],1)],1),a("el-table",{staticStyle:{width:"100%"},attrs:{"highlight-current-row":"",data:e.tableData,border:""}},[a("el-table-column",{attrs:{prop:"sn",label:"No",align:"center",width:"40px"}}),a("el-table-column",{attrs:{prop:"material_type",label:"原材料类型",align:"center"}}),a("el-table-column",{attrs:{prop:"material_no",label:"原材料编码",align:"center"}}),a("el-table-column",{attrs:{prop:"material_name",label:"原材料名称",align:"center"}}),a("el-table-column",{attrs:{prop:"site",label:"产地",align:"center"}}),a("el-table-column",{attrs:{prop:"qty",label:"库存数",align:"center"}}),a("el-table-column",{attrs:{prop:"unit",label:"单位",align:"center"}}),a("el-table-column",{attrs:{prop:"unit_weight",label:"单位重量",align:"center"}}),a("el-table-column",{attrs:{prop:"total_weight",label:"总重量",align:"center"}}),a("el-table-column",{attrs:{prop:"standard_flag",label:"品质状态",align:"center",formatter:e.StandardFlagFormatter}})],1),a("page",{attrs:{total:e.total,"current-page":e.getParams.page},on:{currentChange:e.currentChange}})],1)},n=[],l=(a("96cf"),a("1da1")),i=a("3e51"),c=a("daa1"),o={components:{page:i["a"]},data:function(){return{tableData:[],total:0,getParams:{page:1},materialType:null,materialTypeOptions:[]}},created:function(){this.material_repertory_list()},methods:{material_repertory_list:function(){var e=this;return Object(l["a"])(regeneratorRuntime.mark((function t(){var a;return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:return t.prev=0,t.next=3,Object(c["f"])("get",{params:e.getParams});case 3:a=t.sent,e.tableData=a.results,e.total=a.count,t.next=11;break;case 8:throw t.prev=8,t.t0=t["catch"](0),new Error(t.t0);case 11:case"end":return t.stop()}}),t,null,[[0,8]])})))()},materials_type_list:function(){var e=this;return Object(l["a"])(regeneratorRuntime.mark((function t(){var a;return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:return t.prev=0,t.next=3,Object(c["g"])("get",{params:{}});case 3:a=t.sent,0!==a.results.length&&(e.materialTypeOptions=a.results),t.next=10;break;case 7:throw t.prev=7,t.t0=t["catch"](0),new Error(t.t0);case 10:case"end":return t.stop()}}),t,null,[[0,7]])})))()},materialTypeChange:function(e){e&&this.materials_type_list()},StandardFlagFormatter:function(e,t){return this.StandardFlagChoice(e.standard_flag)},StandardFlagChoice:function(e){switch(e){case!0:return"合格";case!1:return"不合格"}},changeSearch:function(){this.getParams["material_type"]=this.materialType,this.getParams.page=1,this.material_repertory_list()},currentChange:function(e){this.getParams.page=e,this.material_repertory_list()}}},u=o,s=a("2877"),p=Object(s["a"])(u,r,n,!1,null,"c2ce55ac",null);t["default"]=p.exports},daa1:function(e,t,a){"use strict";a.d(t,"e",(function(){return l})),a.d(t,"b",(function(){return i})),a.d(t,"a",(function(){return c})),a.d(t,"f",(function(){return o})),a.d(t,"g",(function(){return u})),a.d(t,"h",(function(){return s})),a.d(t,"i",(function(){return p})),a.d(t,"c",(function(){return g})),a.d(t,"d",(function(){return m}));var r=a("b775"),n=a("99b1");function l(e){var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},a={url:n["a"].MaterialQuantityDemandedUrl,method:e};return Object.assign(a,t),Object(r["a"])(a)}function i(e){var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},a={url:n["a"].ClassArrangelUrl,method:e};return Object.assign(a,t),Object(r["a"])(a)}function c(e){var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},a={url:n["a"].BanburyPlanUrl,method:e};return Object.assign(a,t),Object(r["a"])(a)}function o(e){var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},a={url:n["a"].MaterialRepertoryUrl,method:e};return Object.assign(a,t),Object(r["a"])(a)}function u(e){var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},a={url:n["a"].MaterialTypelUrl,method:e};return Object.assign(a,t),Object(r["a"])(a)}function s(e){var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},a={url:n["a"].RubberRepertoryUrl,method:e};return Object.assign(a,t),Object(r["a"])(a)}function p(e){var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},a={url:n["a"].StageGlobalUrl,method:e};return Object.assign(a,t),Object(r["a"])(a)}function g(e){return Object(r["a"])({url:n["a"].EquipUrl,method:"get",params:e})}function m(){return Object(r["a"])({url:n["a"].GlobalCodesUrl,method:"get",params:{all:1,class_name:"工序"}})}}}]);