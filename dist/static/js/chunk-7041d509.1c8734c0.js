(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-7041d509"],{"3e51":function(e,t,a){"use strict";var n=function(){var e=this,t=e.$createElement,a=e._self._c||t;return a("div",[a("el-pagination",{attrs:{layout:"total,prev,pager,next",total:e.total,"page-size":e.pageSize,"current-page":e._currentPage},on:{"update:currentPage":function(t){e._currentPage=t},"update:current-page":function(t){e._currentPage=t},"current-change":e.currentChange}})],1)},r=[],l=(a("a9e3"),{props:{total:{type:Number,default:0},pageSize:{type:Number,default:10},currentPage:{type:Number,default:1}},data:function(){return{}},computed:{_currentPage:{get:function(){return this.currentPage},set:function(){return 1}}},methods:{currentChange:function(e){this.$emit("currentChange",e)}}}),o=l,s=a("2877"),i=Object(s["a"])(o,n,r,!1,null,null,null);t["a"]=i.exports},bc9f:function(e,t,a){"use strict";a.r(t);var n=function(){var e=this,t=e.$createElement,a=e._self._c||t;return a("div",[a("el-form",{attrs:{inline:!0}},[a("el-form-item",{attrs:{label:"时间"}},[a("el-date-picker",{attrs:{type:"daterange","range-separator":"至","start-placeholder":"开始日期","end-placeholder":"结束日期","value-format":"yyyy-MM-dd"},on:{change:e.searchDate},model:{value:e.dateValue,callback:function(t){e.dateValue=t},expression:"dateValue"}})],1),a("el-form-item",{attrs:{label:"原因编辑"}},[a("el-select",{attrs:{clearable:"",placeholder:"请选择"},on:{change:e.reasonChange},model:{value:e.search.reason,callback:function(t){e.$set(e.search,"reason",t)},expression:"search.reason"}},e._l(e.options,(function(e){return a("el-option",{key:e.name,attrs:{label:e.name,value:e.bool}})})),1)],1),a("el-form-item",{attrs:{label:"技术处理"}},[a("el-select",{attrs:{clearable:"",placeholder:"请选择"},on:{change:e.reasonChange},model:{value:e.search.t_deal_suggestion,callback:function(t){e.$set(e.search,"t_deal_suggestion",t)},expression:"search.t_deal_suggestion"}},e._l(e.options,(function(e){return a("el-option",{key:e.name,attrs:{label:e.name,value:e.bool}})})),1)],1),a("el-form-item",{attrs:{label:"检查处理"}},[a("el-select",{attrs:{clearable:"",placeholder:"请选择"},on:{change:e.reasonChange},model:{value:e.search.c_deal_suggestion,callback:function(t){e.$set(e.search,"c_deal_suggestion",t)},expression:"search.c_deal_suggestion"}},e._l(e.options,(function(e){return a("el-option",{key:e.name,attrs:{label:e.name,value:e.bool}})})),1)],1)],1),a("el-table",{staticStyle:{width:"100%"},attrs:{data:e.tableData,border:"","tooltip-effect":"dark"}},[a("el-table-column",{attrs:{type:"index",width:"50",label:"No"}}),a("el-table-column",{attrs:{label:"处置单号","show-overflow-tooltip":""},scopedSlots:e._u([{key:"default",fn:function(t){return[a("el-link",{attrs:{type:"primary"},on:{click:function(a){return e.clickOrderNum(t.$index,t.row)}}},[e._v(e._s(t.row.unqualified_deal_order_uid))])]}}])}),a("el-table-column",{attrs:{prop:"created_date",label:"创建时间"},scopedSlots:e._u([{key:"default",fn:function(t){var a=t.row;return[e._v(" "+e._s(a.created_date.split(" ")[0])+" ")]}}])}),a("el-table-column",{attrs:{prop:"department",label:"发生部门"}}),a("el-table-column",{attrs:{prop:"reason",label:"不合格原因","show-overflow-tooltip":""},scopedSlots:e._u([{key:"default",fn:function(t){var a=t.row;return[e._v(" "+e._s(e.changeInputBack(a.reason))+" ")]}}])}),a("el-table-column",{attrs:{prop:"t_deal_suggestion",label:"技术不合格原因","show-overflow-tooltip":""},scopedSlots:e._u([{key:"default",fn:function(t){var a=t.row;return[e._v(" "+e._s(e.changeInputBack(a.t_deal_suggestion))+" ")]}}])}),a("el-table-column",{attrs:{prop:"c_deal_suggestion",label:"检查不合格原因","show-overflow-tooltip":""},scopedSlots:e._u([{key:"default",fn:function(t){var a=t.row;return[e._v(" "+e._s(e.changeInputBack(a.c_deal_suggestion))+" ")]}}])}),a("el-table-column",{attrs:{label:"原因编辑"},scopedSlots:e._u([{key:"default",fn:function(t){return[a("el-button",{directives:[{name:"permission",rawName:"v-permission",value:["unqualified_order","reason"],expression:"['unqualified_order','reason']"}],attrs:{size:"small"},on:{click:function(a){return e.editReason(t.$index,t.row,1)}}},[e._v("编辑")])]}}])}),a("el-table-column",{attrs:{label:"技术处理"},scopedSlots:e._u([{key:"default",fn:function(t){return[a("el-button",{directives:[{name:"permission",rawName:"v-permission",value:["unqualified_order","tech"],expression:"['unqualified_order','tech']"}],attrs:{size:"small"},on:{click:function(a){return e.editReason(t.$index,t.row,2)}}},[e._v("编辑")])]}}])}),a("el-table-column",{attrs:{label:"检查处理"},scopedSlots:e._u([{key:"default",fn:function(t){return[a("el-button",{directives:[{name:"permission",rawName:"v-permission",value:["unqualified_order","check"],expression:"['unqualified_order','check']"}],attrs:{size:"small"},on:{click:function(a){return e.editReason(t.$index,t.row,3)}}},[e._v("编辑")])]}}])}),a("el-table-column",{attrs:{prop:"deal_user",label:"原因编辑人"}}),a("el-table-column",{attrs:{prop:"t_deal_user",label:"技术处理人"}}),a("el-table-column",{attrs:{prop:"c_deal_user",label:"检查处理人"}}),a("el-table-column",{attrs:{prop:"deal_date",label:"原因编辑时间"}}),a("el-table-column",{attrs:{prop:"t_deal_date",label:"技术处理时间"}}),a("el-table-column",{attrs:{prop:"c_deal_date",label:"检查处理时间"}})],1),a("page",{attrs:{total:e.total,"current-page":e.search.page},on:{currentChange:e.currentChange}}),a("el-dialog",{attrs:{fullscreen:!0,visible:e.handleCardDialogVisible},on:{"update:visible":function(t){e.handleCardDialogVisible=t}}},[a("excel",{ref:"handleCard",attrs:{"order-row":e.currentRow,"edit-type":e.editType,show:e.handleCardDialogVisible},on:{submitFun:e.submitFun}})],1)],1)},r=[],l=(a("ac1f"),a("5319"),a("841c"),a("96cf"),a("1da1")),o=a("3e51"),s=a("f5b4"),i=a("1f6c"),c=a("ed08"),u={components:{excel:s["a"],page:o["a"]},data:function(){return{tableData:[],search:{value:[],page:1},total:0,options:[{name:"已处理",bool:!1},{name:"未处理",bool:!0}],handleCardDialogVisible:!1,currentRow:{},editType:null,dateValue:[Object(c["b"])(),Object(c["b"])()]}},created:function(){this.search.st=Object(c["b"])(),this.search.et=Object(c["b"])(),this.getList()},methods:{getList:function(){var e=this;return Object(l["a"])(regeneratorRuntime.mark((function t(){var a;return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:return t.prev=0,t.next=3,Object(i["O"])("get",null,{params:e.search});case 3:a=t.sent,e.tableData=a.results,e.total=a.count,t.next=10;break;case 8:t.prev=8,t.t0=t["catch"](0);case 10:case"end":return t.stop()}}),t,null,[[0,8]])})))()},changeInputBack:function(e){return e?e.replace(/<br>/g,"\r\n").replace(/<br>/g,"\n").replace(/&nbsp;/g,"s"):""},editReason:function(e,t,a){this.handleCardDialogVisible=!0,this.currentRow=t,this.editType=a},clickOrderNum:function(e,t){this.handleCardDialogVisible=!0,this.currentRow=t,this.editType=null},currentChange:function(e){this.search.page=e,this.getList()},searchDate:function(e){this.search.st=e?e[0]:"",this.search.et=e?e[1]:"",this.search.page=1,this.getList()},submitFun:function(){this.handleCardDialogVisible=!1,this.getList()},reasonChange:function(){this.search.page=1,this.getList()}}},d=u,p=a("2877"),h=Object(p["a"])(d,n,r,!1,null,null,null);t["default"]=h.exports}}]);