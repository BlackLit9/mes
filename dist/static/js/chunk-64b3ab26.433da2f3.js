(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-64b3ab26","chunk-2d0b21c8"],{"235f":function(e,t,s){"use strict";s.r(t);var o=function(){var e=this,t=e.$createElement,s=e._self._c||t;return s("div",{staticClass:"app-container"},[s("el-row",[s("el-col",{attrs:{span:12}},[s("el-table",{staticStyle:{"margin-top":"40px"},attrs:{data:e.disposeTypeList,border:"","highlight-current-row":""},on:{"current-change":e.disposeTypeCurrentRowChange}},[s("el-table-column",{attrs:{type:"index",label:"No",align:"center"}}),s("el-table-column",{attrs:{label:"公用代码",width:"80",align:"center",prop:"global_no"}}),s("el-table-column",{attrs:{label:"处理类型",align:"center",prop:"global_name"}}),s("el-table-column",{attrs:{label:"操作",align:"center"},scopedSlots:e._u([{key:"default",fn:function(t){var o=t.row;return[s("el-button",{directives:[{name:"permission",rawName:"v-permission",value:["deal_suggestion","change"],expression:"['deal_suggestion','change']"}],attrs:{size:"mini"},on:{click:function(t){return e.handleUpdateType(o)}}},[e._v("编辑")])]}}])})],1)],1),s("el-col",{attrs:{span:12}},[s("el-button",{directives:[{name:"permission",rawName:"v-permission",value:["deal_suggestion","add"],expression:"['deal_suggestion','add']"}],staticStyle:{float:"right"},attrs:{disabled:!e.disposeTypeCurrentRow},on:{click:e.handleNewOpinion}},[e._v("新增")]),s("el-table",{attrs:{border:"",data:e.opinionsList}},[s("el-table-column",{attrs:{type:"index",label:"No",align:"center"}}),s("el-table-column",{attrs:{label:"处理意见",prop:"suggestion_desc",align:"center"}}),s("el-table-column",{attrs:{label:"操作",align:"center"},scopedSlots:e._u([{key:"default",fn:function(t){var o=t.row;return[s("el-button",{directives:[{name:"permission",rawName:"v-permission",value:["deal_suggestion","change"],expression:"['deal_suggestion','change']"}],attrs:{size:"mini"},on:{click:function(t){return e.handleUpdateOpinion(o)}}},[e._v("编辑")])]}}])})],1)],1)],1),s("el-dialog",{attrs:{title:e.textMap[e.dialogDisposeStatus]+"处理类型",visible:e.dialogDisposeTypeVisible,"append-to-body":!0},on:{"update:visible":function(t){e.dialogDisposeTypeVisible=t}}},[s("el-form",{ref:"disposeTypeForm",attrs:{model:e.disposeTypeForm,rules:e.disposeTypeRules}},[s("el-form-item",{attrs:{label:"处理类型","label-width":"110px",prop:"global_name"}},[s("el-input",{model:{value:e.disposeTypeForm.global_name,callback:function(t){e.$set(e.disposeTypeForm,"global_name",t)},expression:"disposeTypeForm.global_name"}})],1),s("el-form-item",{attrs:{label:"公用代码编号","label-width":"110px",prop:"global_no"}},[s("el-input",{attrs:{disabled:"update"===e.dialogDisposeStatus},model:{value:e.disposeTypeForm.global_no,callback:function(t){e.$set(e.disposeTypeForm,"global_no",t)},expression:"disposeTypeForm.global_no"}})],1)],1),s("div",{staticClass:"dialog-footer",attrs:{slot:"footer"},slot:"footer"},[s("el-button",{on:{click:function(t){e.dialogDisposeTypeVisible=!1}}},[e._v(" 取消 ")]),s("el-button",{attrs:{type:"primary"},on:{click:function(t){"create"===e.dialogDisposeStatus?e.createDisposeType():e.updateDisposeType()}}},[e._v(" 确定 ")])],1)],1),s("el-dialog",{attrs:{title:e.textMap[e.disposeOpinionStatus]+"处理意见",visible:e.dialogOpinionVisible,"append-to-body":!0},on:{"update:visible":function(t){e.dialogOpinionVisible=t}}},[s("el-form",{ref:"disposeOpinionForm",attrs:{model:e.disposeOpinionForm,rules:e.disposeOpinionRules}},[s("el-form-item",{attrs:{label:"处理意见","label-width":"110px",prop:"suggestion_desc"}},[s("el-input",{model:{value:e.disposeOpinionForm.suggestion_desc,callback:function(t){e.$set(e.disposeOpinionForm,"suggestion_desc",t)},expression:"disposeOpinionForm.suggestion_desc"}})],1)],1),s("div",{staticClass:"dialog-footer",attrs:{slot:"footer"},slot:"footer"},[s("el-button",{on:{click:function(t){e.dialogOpinionVisible=!1}}},[e._v(" 取消 ")]),s("el-button",{attrs:{type:"primary"},on:{click:function(t){"create"===e.disposeOpinionStatus?e.createOpinion():e.updateOpinion()}}},[e._v(" 确定 ")])],1)],1)],1)},i=[],n=s("5530"),a=(s("96cf"),s("1da1")),r=s("b775"),l=s("99b1");function u(){return Object(r["a"])({url:l["a"].GlobalTypesUrl,method:"get",params:{type_name:"处理类型"}})}function p(){return Object(r["a"])({url:l["a"].DisposeTypeUrl,method:"get",params:{all:1,type_no:14}})}function c(e,t,s){var o={url:t?l["a"].DisposeTypeUrl+t+"/":l["a"].DisposeTypeUrl,method:e,data:s};return Object(r["a"])(o)}function d(e){return Object(r["a"])({url:l["a"].DealSuggestionUrl,method:"get",params:{deal_type:e}})}function g(e,t,s){var o={url:t?l["a"].DealSuggestionUrl+t+"/":l["a"].DealSuggestionUrl,method:e,data:s};return Object(r["a"])(o)}var m={data:function(){return{globalType:null,disposeTypeList:[],dialogDisposeTypeVisible:!1,dialogOpinionVisible:!1,disposeTypeForm:{global_name:"",global_no:""},textMap:{update:"编辑",create:"创建"},dialogDisposeStatus:"",disposeTypeRules:{global_name:[{required:!0,message:"该字段不能为空",trigger:"blur"}],global_no:[{required:!0,message:"该字段不能为空",trigger:"blur"}]},disposeTypeCurrentRow:null,opinionsList:[],disposeOpinionStatus:"",disposeOpinionForm:{suggestion_desc:""},disposeOpinionRules:{suggestion_desc:[{required:!0,message:"该字段不能为空",trigger:"blur"}]}}},created:function(){this.getDisposeTypeGlobalType(),this.getDisposeTypes()},methods:{disposeTypeCurrentRowChange:function(e){var t=this;this.disposeTypeCurrentRow=e,this.opinionsList=[],e&&d(e.id).then((function(e){t.opinionsList=e.results}))},getDisposeTypeGlobalType:function(){var e=this;return Object(a["a"])(regeneratorRuntime.mark((function t(){var s;return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:return t.prev=0,t.next=3,u();case 3:s=t.sent,e.globalType=s.results[0].id,t.next=9;break;case 7:t.prev=7,t.t0=t["catch"](0);case 9:case"end":return t.stop()}}),t,null,[[0,7]])})))()},getDisposeTypes:function(){var e=this;return Object(a["a"])(regeneratorRuntime.mark((function t(){var s;return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:return t.prev=0,t.next=3,p();case 3:s=t.sent,e.disposeTypeList=s.results,t.next=9;break;case 7:t.prev=7,t.t0=t["catch"](0);case 9:case"end":return t.stop()}}),t,null,[[0,7]])})))()},handleNewType:function(){var e=this;this.disposeTypeForm={global_name:"",global_no:""},this.dialogDisposeStatus="create",this.dialogDisposeTypeVisible=!0,this.$nextTick((function(){e.$refs["disposeTypeForm"].clearValidate()}))},handleUpdateType:function(e){var t=this;this.disposeTypeForm=Object.assign({},e),this.dialogDisposeStatus="update",this.dialogDisposeTypeVisible=!0,this.$nextTick((function(){t.$refs["disposeTypeForm"].clearValidate()}))},createDisposeType:function(){var e=this;this.$refs["disposeTypeForm"].validate((function(t){t&&c("post",null,Object(n["a"])(Object(n["a"])({},e.disposeTypeForm),{},{global_type:e.globalType})).then((function(){e.dialogDisposeTypeVisible=!1,e.getDisposeTypes(),e.$notify({title:"成功",message:"".concat(e.disposeTypeForm.global_name,"创建成功"),type:"success",duration:2e3})}))}))},updateDisposeType:function(){var e=this;this.$refs["disposeTypeForm"].validate((function(t){t&&c("patch",e.disposeTypeForm.id,{global_name:e.disposeTypeForm.global_name}).then((function(){e.dialogDisposeTypeVisible=!1,e.getDisposeTypes(),e.$notify({title:"成功",message:"".concat(e.disposeTypeForm.global_name,"修改成功"),type:"success",duration:2e3})}))}))},handleNewOpinion:function(){var e=this;this.disposeOpinionForm={suggestion_desc:""},this.disposeOpinionStatus="create",this.dialogOpinionVisible=!0,this.$nextTick((function(){e.$refs["disposeOpinionForm"].clearValidate()}))},createOpinion:function(){var e=this;this.$refs["disposeOpinionForm"].validate((function(t){t&&g("post",null,Object(n["a"])({deal_type:e.disposeTypeCurrentRow.id},e.disposeOpinionForm)).then((function(){e.dialogOpinionVisible=!1,e.disposeTypeCurrentRowChange(e.disposeTypeCurrentRow),e.$notify({title:"成功",message:"".concat(e.disposeOpinionForm.suggestion_desc,"创建成功"),type:"success",duration:2e3})}))}))},handleUpdateOpinion:function(e){var t=this;this.disposeOpinionForm=Object.assign({},e),this.disposeOpinionStatus="update",this.dialogOpinionVisible=!0,this.$nextTick((function(){t.$refs["disposeOpinionForm"].clearValidate()}))},updateOpinion:function(){var e=this;this.$refs["disposeOpinionForm"].validate((function(t){t&&g("patch",e.disposeOpinionForm.id,{suggestion_desc:e.disposeOpinionForm.suggestion_desc}).then((function(){e.dialogOpinionVisible=!1,e.disposeTypeCurrentRowChange(e.disposeTypeCurrentRow),e.$notify({title:"成功",message:"".concat(e.disposeOpinionForm.suggestion_desc,"修改成功"),type:"success",duration:2e3})}))}))}}},b=m,f=s("2877"),h=Object(f["a"])(b,o,i,!1,null,null,null);t["default"]=h.exports},"3e51":function(e,t,s){"use strict";var o=function(){var e=this,t=e.$createElement,s=e._self._c||t;return s("div",[s("el-pagination",{attrs:{layout:"total,prev,pager,next",total:e.total,"page-size":e.pageSize,"current-page":e._currentPage},on:{"update:currentPage":function(t){e._currentPage=t},"update:current-page":function(t){e._currentPage=t},"current-change":e.currentChange}})],1)},i=[],n=(s("a9e3"),{props:{total:{type:Number,default:0},pageSize:{type:Number,default:10},currentPage:{type:Number,default:1}},data:function(){return{}},computed:{_currentPage:{get:function(){return this.currentPage},set:function(){return 1}}},methods:{currentChange:function(e){this.$emit("currentChange",e)}}}),a=n,r=s("2877"),l=Object(r["a"])(a,o,i,!1,null,null,null);t["a"]=l.exports},c83d:function(e,t,s){"use strict";s.d(t,"c",(function(){return n})),s.d(t,"d",(function(){return a})),s.d(t,"f",(function(){return r})),s.d(t,"a",(function(){return l})),s.d(t,"b",(function(){return u})),s.d(t,"e",(function(){return p}));var o=s("b775"),i=s("99b1");function n(e,t,s){var n={url:t?i["a"].MaterialDealResultUrl+t+"/":i["a"].MaterialDealResultUrl,method:e,data:s};return Object(o["a"])(n)}function a(e){return Object(o["a"])({url:i["a"].MaterialDealResultUrl,method:"get",params:e})}function r(){return Object(o["a"])({url:i["a"].ResultStatusUrl,method:"get"})}function l(e){return Object(o["a"])({url:i["a"].DealSuggestionUrl,method:"get",params:{type_name:e}})}function u(){return Object(o["a"])({url:i["a"].dealSuggestionView,method:"get"})}function p(e){return Object(o["a"])({url:i["a"].PrintMaterialDealResult,method:"get",params:e,responseType:"blob"})}},ea83:function(e,t,s){"use strict";s.r(t);var o=function(){var e=this,t=e.$createElement,s=e._self._c||t;return s("div",{staticClass:"app-container"},[s("el-form",{attrs:{inline:!0}},[s("el-form-item",{attrs:{label:"生产日期"}},[s("el-date-picker",{attrs:{"value-format":"yyyy-MM-dd",clearable:"",type:"date",placeholder:"选择日期"},on:{change:e.dayChanged},model:{value:e.getParams.day,callback:function(t){e.$set(e.getParams,"day",t)},expression:"getParams.day"}})],1),s("el-form-item",{attrs:{label:"状态"}},[s("el-select",{attrs:{placeholder:"请选择",clearable:""},on:{change:e.statusChanged},model:{value:e.getParams.status,callback:function(t){e.$set(e.getParams,"status",t)},expression:"getParams.status"}},e._l(e.resultStatusList,(function(e){return s("el-option",{key:e.status,attrs:{label:e.status,value:e.status}})})),1)],1),s("el-form-item",{staticStyle:{float:"right"}},[s("el-button",{on:{click:e.exportData}},[e._v("导出")])],1)],1),s("el-table",{staticStyle:{width:"100%"},attrs:{border:"",fit:"",data:e.inferiorQualityList}},[s("el-table-column",{attrs:{label:"No",type:"index",align:"center"}}),s("el-table-column",{attrs:{label:"生产日期",width:"155",prop:"production_factory_date"}}),s("el-table-column",{attrs:{label:"机台",prop:"product_info.production_equip_no"}}),s("el-table-column",{attrs:{label:"班次",prop:"product_info.production_class"}}),s("el-table-column",{attrs:{label:"胶料编码",prop:"product_info.product_no"}}),s("el-table-column",{attrs:{label:"lot追踪号",width:"90",prop:"lot_no"}}),s("el-table-column",{attrs:{label:"等级",prop:"level",width:"60"}}),s("el-table-column",{attrs:{label:"不合格原因",width:"100",prop:"reason"},scopedSlots:e._u([{key:"default",fn:function(t){var o=t.row;return[s("el-popover",{attrs:{placement:"top-start",title:"不合格原因",width:"400",trigger:"hover",content:o.reason}},[s("a",{attrs:{slot:"reference"},slot:"reference"},[e._v(" "+e._s(o.reason.slice(0,6)))])])]}}])}),s("el-table-column",{attrs:{label:"状态",prop:"status"}}),s("el-table-column",{attrs:{label:"操作",width:"160",align:"center"},scopedSlots:e._u([{key:"default",fn:function(t){var o=t.row;return["待处理"===o.status?s("el-button",{directives:[{name:"permission",rawName:"v-permission",value:["non-conformity_product","change"],expression:"['non-conformity_product','change']"}],attrs:{size:"mini"},on:{click:function(t){return e.handleDispose(o)}}},[e._v("处理")]):e._e(),"待确认"===o.status?s("el-button",{directives:[{name:"permission",rawName:"v-permission",value:["non-conformity_product","change"],expression:"['non-conformity_product','change']"}],attrs:{size:"mini"},on:{click:function(t){return e.confirm(o)}}},[e._v("确认")]):e._e(),"待确认"===o.status?s("el-button",{directives:[{name:"permission",rawName:"v-permission",value:["non-conformity_product","change"],expression:"['non-conformity_product','change']"}],attrs:{size:"mini"},on:{click:function(t){return e.reject(o)}}},[e._v("驳回")]):e._e()]}}])}),s("el-table-column",{attrs:{label:"是否出库",align:"center",prop:"be_warehouse_out",formatter:function(e){return e.be_warehouse_out?"Y":"N"}}}),s("el-table-column",{attrs:{label:"出库时间",width:"155",prop:"warehouse_out_time",align:"center"}}),s("el-table-column",{attrs:{label:"处理意见",align:"center",width:"155",prop:"deal_suggestion"}}),s("el-table-column",{attrs:{label:"检测结果",prop:"deal_result"}}),s("el-table-column",{attrs:{label:"处理人",prop:"deal_user"}}),s("el-table-column",{attrs:{label:"确认人",prop:"confirm_user"}})],1),s("page",{attrs:{total:e.total,"current-page":e.getParams.page},on:{currentChange:e.currentChange}}),s("el-dialog",{attrs:{title:"处理不合格品",visible:e.dialogDisposeVisible},on:{"update:visible":function(t){e.dialogDisposeVisible=t}}},[s("el-form",{ref:"disposeForm",attrs:{model:e.disposeForm,rules:e.rules,"label-position":"left","label-width":"110px"}},[s("el-form-item",{attrs:{label:"处理意见",prop:"deal_suggestion"}},[s("el-select",{attrs:{clearable:""},model:{value:e.disposeForm.deal_suggestion,callback:function(t){e.$set(e.disposeForm,"deal_suggestion",t)},expression:"disposeForm.deal_suggestion"}},e._l(e.suggestionOptions,(function(t){return s("el-option-group",{key:t.label,attrs:{label:t.label}},e._l(t.options,(function(e){return s("el-option",{key:e.id,attrs:{label:e.suggestion_desc,value:e.suggestion_desc}})})),1)})),1)],1),s("el-form-item",{attrs:{label:"出库"}},[s("el-checkbox",{model:{value:e.disposeForm.be_warehouse_out,callback:function(t){e.$set(e.disposeForm,"be_warehouse_out",t)},expression:"disposeForm.be_warehouse_out"}})],1),s("el-form-item",{attrs:{label:"出库时间选择",prop:"warehouse_out_time"}},[s("el-date-picker",{attrs:{clearable:"",type:"datetime",placeholder:"选择日期","value-format":"yyyy-MM-dd HH:mm:ss"},model:{value:e.disposeForm.warehouse_out_time,callback:function(t){e.$set(e.disposeForm,"warehouse_out_time",t)},expression:"disposeForm.warehouse_out_time"}})],1),s("el-form-item",[s("el-button",{directives:[{name:"permission",rawName:"v-permission",value:["deal_suggestion","add"],expression:"['deal_suggestion','add']"}],on:{click:function(t){e.dialogOpinionsVisible=!0}}},[e._v("新建处理意见")])],1)],1),s("div",{staticClass:"dialog-footer",attrs:{slot:"footer"},slot:"footer"},[s("el-button",{on:{click:function(t){e.dialogDisposeVisible=!1}}},[e._v(" 取消 ")]),s("el-button",{attrs:{type:"primary"},on:{click:function(t){return e.updateDispose()}}},[e._v(" 确定 ")])],1)],1),s("el-dialog",{attrs:{title:"不合格处理意见管理",visible:e.dialogOpinionsVisible,width:"80%","before-close":function(t){e.getDealSuggestions(),t()}},on:{"update:visible":function(t){e.dialogOpinionsVisible=t}}},[s("unqualified-treatment-opinions")],1)],1)},i=[],n=(s("4160"),s("d3b7"),s("3ca3"),s("ddb0"),s("2b3d"),s("96cf"),s("1da1")),a=s("3e51"),r=s("235f"),l=s("c83d"),u={components:{Page:a["a"],UnqualifiedTreatmentOpinions:r["default"]},data:function(){var e=this,t=function(t,s,o){e.disposeForm.be_warehouse_out&&!s?o(new Error("出库时必须选择出库时间")):o()};return{total:0,getParams:{page:1,day:null,status:null},inferiorQualityList:[],dialogDisposeVisible:!1,disposeForm:{deal_suggestion:"",be_warehouse_out:!1,warehouse_out_time:null},rules:{deal_suggestion:[{required:!0,message:"该字段不能为空",trigger:"change"}],warehouse_out_time:[{validator:t,trigger:"change"}]},resultStatusList:[{status:"待处理"},{status:"待确认"},{status:"已处理"}],dialogOpinionsVisible:!1,suggestionOptions:[]}},created:function(){this.getMaterialDealResult()},methods:{getDealSuggestions:function(){var e=this;this.suggestionOptions=[];try{["放行处理","不合格处理"].forEach(function(){var t=Object(n["a"])(regeneratorRuntime.mark((function t(s){var o;return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:return t.next=2,Object(l["a"])(s);case 2:o=t.sent,e.suggestionOptions.push({label:s,options:o.results});case 4:case"end":return t.stop()}}),t)})));return function(e){return t.apply(this,arguments)}}())}catch(t){}},getResultStatus:function(){var e=this;return Object(n["a"])(regeneratorRuntime.mark((function t(){return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:return t.prev=0,t.next=3,Object(l["f"])();case 3:e.resultStatusList=t.sent,t.next=8;break;case 6:t.prev=6,t.t0=t["catch"](0);case 8:case"end":return t.stop()}}),t,null,[[0,6]])})))()},dayChanged:function(){this.currentChange(1)},statusChanged:function(){this.currentChange(1)},currentChange:function(e){this.getParams.page=e,this.getMaterialDealResult()},getMaterialDealResult:function(){var e=this;return Object(n["a"])(regeneratorRuntime.mark((function t(){var s;return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:return t.prev=0,t.next=3,Object(l["d"])(e.getParams);case 3:s=t.sent,e.inferiorQualityList=s.results,e.total=s.count,t.next=10;break;case 8:t.prev=8,t.t0=t["catch"](0);case 10:case"end":return t.stop()}}),t,null,[[0,8]])})))()},handleDispose:function(e){var t=this;this.getDealSuggestions(),this.disposeForm=Object.assign({},e),this.dialogDisposeVisible=!0,this.$nextTick((function(){t.$refs["disposeForm"].clearValidate()}))},confirm:function(e){var t=this;Object(l["c"])("patch",e.id,{status:"已处理",material_no:e.product_info.product_no,warehouse_info:1}).then((function(){t.currentChange(t.getParams.page),t.$notify({title:"成功",message:"更新成功",type:"success",duration:2e3})}))},reject:function(e){var t=this;Object(l["c"])("patch",e.id,{status:"待处理",material_no:e.product_info.product_no,warehouse_info:1}).then((function(){t.currentChange(t.getParams.page),t.$notify({title:"成功",message:"更新成功",type:"success",duration:2e3})}))},updateDispose:function(){var e=this;console.log(this.disposeForm,"here"),this.$refs["disposeForm"].validate((function(t){if(t){var s=e.disposeForm,o=s.deal_suggestion,i=s.be_warehouse_out,n=s.warehouse_out_time;Object(l["c"])("patch",e.disposeForm.id,{deal_suggestion:o,be_warehouse_out:i,warehouse_out_time:n,status:"待确认",material_no:e.disposeForm.product_info.product_no,warehouse_info:1}).then((function(){e.dialogDisposeVisible=!1,e.currentChange(e.getParams.page),e.$notify({title:"成功",message:"更新成功",type:"success",duration:2e3})}))}}))},exportData:function(){Object(l["e"])(this.getParams).then((function(e){var t=document.createElement("a"),s=new Blob([e],{type:"application/vnd.ms-excel"});t.style.display="none",t.href=URL.createObjectURL(s),t.download="不合格品.xlsx",document.body.appendChild(t),t.click(),document.body.removeChild(t)}))}}},p=u,c=s("2877"),d=Object(c["a"])(p,o,i,!1,null,null,null);t["default"]=d.exports}}]);