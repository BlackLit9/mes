(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-6de6cfec"],{"129f":function(e,t){e.exports=Object.is||function(e,t){return e===t?0!==e||1/e===1/t:e!=e&&t!=t}},"25f6":function(e,t,a){"use strict";a.d(t,"a",(function(){return i}));var n=a("b775"),r=a("99b1");function i(e){return Object(n["a"])({url:r["a"].MaterialInventoryManage,method:"get",params:e})}},"27c9":function(e,t,a){"use strict";var n=a("3f66"),r=a.n(n);r.a},"3f66":function(e,t,a){},"53c1":function(e,t,a){"use strict";var n=a("b633"),r=a.n(n);r.a},"5cfb":function(e,t,a){"use strict";var n=function(){var e=this,t=e.$createElement,a=e._self._c||t;return a("div",{staticClass:"generate_normal_outbound"},[a("el-form",{ref:"ruleForm",attrs:{model:e.ruleForm,rules:e.rules,"label-width":"140px"}},[a("el-form-item",{attrs:{label:"仓库名称"}},[e._v(" "+e._s(e.warehouseName)+" ")]),a("el-form-item",{attrs:{label:"仓库位置",prop:"station"}},[a("stationInfoWarehouse",{ref:"stationInfoWarehouseRef",attrs:{"warehouse-name":e.warehouseName,"start-using":!0},on:{changSelect:e.changSelectStation}})],1),a("el-form-item",{attrs:{label:"品质状态",prop:"quality_status"}},[a("el-select",{attrs:{placeholder:"请选择"},model:{value:e.ruleForm.quality_status,callback:function(t){e.$set(e.ruleForm,"quality_status",t)},expression:"ruleForm.quality_status"}},e._l(e.options,(function(e){return a("el-option",{key:e,attrs:{label:e,value:e}})})),1)],1),a("el-form-item",{attrs:{label:"物料编码",prop:"material_no"}},[a("materialCodeSelect",{attrs:{"store-name":e.warehouseName,"default-val":e.ruleForm.material_no},on:{changSelect:e.materialCodeFun}})],1),a("el-form-item",{attrs:{label:"可用库存数",prop:"c"}},[a("el-input",{attrs:{disabled:""},model:{value:e.ruleForm.c,callback:function(t){e.$set(e.ruleForm,"c",t)},expression:"ruleForm.c"}})],1),a("el-form-item",{attrs:{label:"需求数量("+("帘布库"===e.warehouseName?"托":"车")+")",prop:"need_qty"}},[a("el-input-number",{attrs:{"controls-position":"right",max:e.ruleForm.c},model:{value:e.ruleForm.need_qty,callback:function(t){e.$set(e.ruleForm,"need_qty",t)},expression:"ruleForm.need_qty"}})],1),a("el-form-item",{attrs:{label:"需求重量"}},[a("el-input-number",{attrs:{"controls-position":"right",precision:3},model:{value:e.ruleForm.need_weight,callback:function(t){e.$set(e.ruleForm,"need_weight",t)},expression:"ruleForm.need_weight"}})],1),"终炼胶出库计划"===e.$route.meta.title?a("el-form-item",{attrs:{label:"关联发货计划"}},[e._v(" "+e._s(e.ruleForm.deliveryPlan)+" "),a("el-button",{attrs:{type:"primary"},on:{click:e.deliverClick}},[e._v("请添加")])],1):e._e(),"混炼胶出库计划"===e.$route.meta.title?a("el-form-item",{attrs:{label:"机台号"}},[a("EquipSelect",{ref:"EquipSelect",attrs:{"is-multiple":!0},on:{equipSelected:e.equipSelected}})],1):e._e()],1),a("div",{staticClass:"dialog-footer",attrs:{slot:"footer"},slot:"footer"},[a("el-button",{on:{click:function(t){return e.visibleMethod(!0)}}},[e._v("取 消")]),a("el-button",{attrs:{type:"primary",loading:e.loadingBtn},on:{click:function(t){return e.visibleMethod(!1)}}},[e._v("确 定")])],1),a("el-dialog",{attrs:{title:"发货计划管理",visible:e.dialogVisible,width:"90%","append-to-body":""},on:{"update:visible":function(t){e.dialogVisible=t}}},[a("receiveList",{ref:"receiveList",attrs:{show:e.dialogVisible,"defalut-val":e.handleSelection,"is-dialog":!0,"material-no":e.ruleForm.material_no}}),a("span",{staticClass:"dialog-footer",attrs:{slot:"footer"},slot:"footer"},[a("el-button",{on:{click:function(t){e.dialogVisible=!1}}},[e._v("取 消")]),a("el-button",{attrs:{type:"primary"},on:{click:e.sureDeliveryPlan}},[e._v("确 定")])],1)],1)],1)},r=[],i=(a("4160"),a("caad"),a("b0c0"),a("a9e3"),a("159b"),a("621a")),l=a("a5db"),o=a("1c7e2"),s=a("8448"),u={components:{EquipSelect:s["a"],materialCodeSelect:i["a"],stationInfoWarehouse:l["a"],receiveList:o["default"]},props:{warehouseName:{type:String,default:function(){return""}},warehouseInfo:{type:Number,default:function(){return null}}},data:function(){var e=this,t=function(e,t,a,n,r){n?a():a(new Error(r))};return{ruleForm:{warehouse_name:this.warehouseName,warehouse_info:this.warehouseInfo,material_no:"",inventory_type:"正常出库",order_no:"order_no",status:4,need_weight:void 0},rules:{material_no:[{required:!0,message:"请输入物料编码",trigger:"blur"}],quality_status:[{required:!0,message:"请选择品质状态",trigger:"change"}],c:[{required:!0,trigger:"blur",validator:function(a,n,r){t(a,n,r,e.ruleForm.c,"无库存数")}}],station:[{required:!0,trigger:"blur",validator:function(a,n,r){t(a,n,r,e.ruleForm.station,"仓库位置")}}],need_qty:[{required:!0,message:"请输入需求数量",trigger:"blur"}]},visible:!1,loadingBtn:null,dialogVisible:!1,handleSelection:[],options:["终炼胶库","混炼胶库"].includes(this.warehouseName)?["一等品","三等品"]:["合格品","不合格品"]}},watch:{},created:function(){},methods:{creadVal:function(){this.$refs.ruleForm.resetFields(),this.$refs.receiveList&&this.$refs.receiveList.clearReceiveSelect(),this.$refs.EquipSelect&&(this.$refs.EquipSelect.equipId=null),this.ruleForm.dispatch=[],this.ruleForm.equip=[],this.handleSelection=[],this.ruleForm.deliveryPlan="",this.loadingBtn=!1,this.$refs.stationInfoWarehouseRef&&(this.$refs.stationInfoWarehouseRef.value=null)},materialCodeFun:function(e){this.ruleForm.material_no=e.material_no||null,this.ruleForm.c=e.all_qty||null,this.$refs.receiveList&&this.$refs.receiveList.clearReceiveSelect(),this.ruleForm.deliveryPlan="",this.handleSelection=[]},visibleMethod:function(e){var t=this;if(e)this.creadVal(),this.$emit("visibleMethod");else{var a=[];this.handleSelection&&this.handleSelection.length>0?(this.handleSelection.forEach((function(e){a.push(e.id)})),this.$set(this.ruleForm,"dispatch",a)):this.$set(this.ruleForm,"dispatch",[]),this.$refs.ruleForm.validate((function(e){if(!e)return!1;t.loadingBtn=!0,t.$emit("visibleMethodSubmit",t.ruleForm)}))}},changSelectStation:function(e){this.ruleForm.station=e?e.name:""},deliverClick:function(){this.ruleForm.material_no?this.dialogVisible=!0:this.$message.info("请选择物料编码")},sureDeliveryPlan:function(){var e=this,t=0;this.handleSelection=this.$refs.receiveList.handleSelection,this.ruleForm.deliveryPlan="",this.handleSelection.forEach((function(a){e.ruleForm.deliveryPlan+=a.order_no+";",t+=a.need_qty})),t>this.ruleForm.c?this.$message.info("物料可用库存数不足"):t<this.ruleForm.c&&this.$message.info("物料可用库存数有余"),this.dialogVisible=!1},equipSelected:function(e){e&&e.length>0?this.$set(this.ruleForm,"equip",e):Object.prototype.hasOwnProperty.call(this.ruleForm,"equip")&&delete this.ruleForm.equip}}},c=u,d=(a("8e49"),a("2877")),h=Object(d["a"])(c,n,r,!1,null,null,null);t["a"]=h.exports},"64dc":function(e,t,a){"use strict";a.d(t,"l",(function(){return i})),a.d(t,"j",(function(){return l})),a.d(t,"b",(function(){return o})),a.d(t,"h",(function(){return s})),a.d(t,"e",(function(){return u})),a.d(t,"a",(function(){return c})),a.d(t,"i",(function(){return d})),a.d(t,"f",(function(){return h})),a.d(t,"k",(function(){return m})),a.d(t,"c",(function(){return b})),a.d(t,"g",(function(){return f})),a.d(t,"d",(function(){return p}));var n=a("b775"),r=a("99b1");function i(){return Object(n["a"])({url:r["a"].WarehouseNamesUrl,method:"get"})}function l(e){return Object(n["a"])({url:r["a"].WarehouseInfoUrl,method:"get",params:e})}function o(e,t,a){return Object(n["a"])({url:t?r["a"].WarehouseInfoUrl+t+"/":r["a"].WarehouseInfoUrl,method:e,data:a})}function s(e){return Object(n["a"])({url:r["a"].WarehouseInfoUrl+e+"/reversal_use_flag/",method:"put"})}function u(e){return Object(n["a"])({url:r["a"].StationInfoUrl,method:"get",params:e})}function c(e,t,a){return Object(n["a"])({url:t?r["a"].StationInfoUrl+t+"/":r["a"].StationInfoUrl,method:e,data:a})}function d(e){return Object(n["a"])({url:r["a"].StationInfoUrl+e+"/reversal_use_flag/",method:"put"})}function h(){return Object(n["a"])({url:r["a"].StationTypesUrl,methods:"get"})}function m(e){return Object(n["a"])({url:r["a"].WarehouseMaterialTypeUrl,method:"get",params:e})}function b(e,t,a){return Object(n["a"])({url:t?r["a"].WarehouseMaterialTypeUrl+t+"/":r["a"].WarehouseMaterialTypeUrl,method:e,data:a})}function f(e){return Object(n["a"])({url:r["a"].WarehouseMaterialTypeUrl+e+"/reversal_use_flag/",method:"put"})}function p(){return Object(n["a"])({url:r["a"].MaterialTypesUrl,methods:"get"})}},"66ad":function(e,t,a){"use strict";a.d(t,"b",(function(){return i})),a.d(t,"c",(function(){return l})),a.d(t,"f",(function(){return o})),a.d(t,"a",(function(){return s})),a.d(t,"e",(function(){return u})),a.d(t,"d",(function(){return c})),a.d(t,"g",(function(){return d}));var n=a("b775"),r=a("99b1");function i(e){return Object(n["a"])({url:r["a"].EquipUrl,method:"get",params:e})}function l(e){return Object(n["a"])({url:r["a"].PalletFeedBacksUrl,method:"get",params:e})}function o(e){return Object(n["a"])({url:r["a"].TrainsFeedbacksUrl,method:"get",params:e})}function s(e){return Object(n["a"])({url:r["a"].EchartsListUrl,method:"get",params:e})}function u(e){return Object(n["a"])({url:r["a"].ProductActualUrl,method:"get",params:e})}function c(e){return Object(n["a"])({url:r["a"].PalletFeedbacksUrl,method:"get",params:e})}function d(e){return Object(n["a"])({url:r["a"].ProductDayPlanNoticeUrl,method:"post",id:e})}},"82f97":function(e,t,a){"use strict";a.r(t);var n=function(){var e=this,t=e.$createElement,a=e._self._c||t;return a("div",{directives:[{name:"loading",rawName:"v-loading",value:e.loading,expression:"loading"}],staticClass:"app-container outbound_manage"},[a("el-form",{attrs:{inline:!0,"label-width":"80px"}},[a("el-form-item",{attrs:{label:"开始日期"}},[a("el-date-picker",{attrs:{type:"daterange","range-separator":"至","start-placeholder":"开始日期","end-placeholder":"结束日期","value-format":"yyyy-MM-dd"},on:{change:e.changeDate},model:{value:e.dateSearch,callback:function(t){e.dateSearch=t},expression:"dateSearch"}})],1),a("el-form-item",{attrs:{label:"订单状态"}},[a("el-select",{attrs:{clearable:"",placeholder:"请选择"},on:{change:e.changeList},model:{value:e.search.status,callback:function(t){e.$set(e.search,"status",t)},expression:"search.status"}},e._l(e.options1,(function(e){return a("el-option",{key:e.id,attrs:{label:e.name,value:e.id}})})),1)],1),a("el-form-item",{attrs:{label:"物料编码"}},[a("el-input",{on:{input:e.changeList},model:{value:e.search.material_no,callback:function(t){e.$set(e.search,"material_no",t)},expression:"search.material_no"}})],1),a("el-form-item",{attrs:{label:"仓库名称"}},[e._v(" "+e._s(e.warehouseName)+" ")]),a("el-form-item",{directives:[{name:"permission",rawName:"v-permission",value:["compoundRubber_plan","norman"],expression:"['compoundRubber_plan','norman']"}],staticStyle:{float:"right"}},[a("el-button",{on:{click:e.normalOutbound}},[e._v("正常出库")])],1),a("el-form-item",{staticStyle:{float:"right"}},[a("el-button",{directives:[{name:"permission",rawName:"v-permission",value:["compoundRubber_plan","assign"],expression:"['compoundRubber_plan','assign']"}],on:{click:e.assignOutbound}},[e._v("指定出库")])],1)],1),a("el-table",{attrs:{border:"",data:e.tableData,size:"mini"}},[a("el-table-column",{attrs:{label:"No",type:"index",align:"center",width:"30"}}),a("el-table-column",{attrs:{label:"仓库名称",align:"center",prop:"name"}}),a("el-table-column",{attrs:{label:"出库类型",align:"center",prop:"inventory_type",width:"65"}}),a("el-table-column",{attrs:{label:"出库单号",align:"center",prop:"order_no"}}),a("el-table-column",{attrs:{label:"托盘号",align:"center",prop:"pallet_no"}}),a("el-table-column",{attrs:{label:"物料编码",align:"center",prop:"material_no"}}),a("el-table-column",{attrs:{label:"出库原因",align:"center",prop:"inventory_reason",width:"50"}}),a("el-table-column",{attrs:{label:"需求数量",align:"center",prop:"need_qty",width:"50"}}),a("el-table-column",{attrs:{label:"出库数量",align:"center",prop:"actual.actual_qty",width:"50"}}),a("el-table-column",{attrs:{label:"实际出库重量",align:"center",prop:"actual.actual_wegit"}}),a("el-table-column",{attrs:{label:"单位",align:"center",prop:"unit",width:"40"}}),a("el-table-column",{attrs:{label:"需求重量",align:"center",prop:"need_weight"}}),a("el-table-column",{attrs:{label:"出库位置",align:"center",prop:"location",width:"40"}}),a("el-table-column",{attrs:{label:"目的地",align:"center",prop:"destination"}}),a("el-table-column",{attrs:{label:"操作",align:"center",width:"220"},scopedSlots:e._u([{key:"default",fn:function(t){return 4===t.row.status?[a("el-button-group",[a("el-button",{directives:[{name:"permission",rawName:"v-permission",value:["compoundRubber_plan","manual"],expression:"['compoundRubber_plan','manual']"}],attrs:{size:"mini",type:"primary"},on:{click:function(a){return e.manualDelivery(t.row)}}},[e._v("人工出库")]),a("el-button",{directives:[{name:"permission",rawName:"v-permission",value:["compoundRubber_plan","change"],expression:"['compoundRubber_plan','change']"}],attrs:{size:"mini",type:"warning"},on:{click:function(a){return e.demandQuantity(t.$index,t.row)}}},[e._v("编辑")]),a("el-button",{directives:[{name:"permission",rawName:"v-permission",value:["compoundRubber_plan","close"],expression:"['compoundRubber_plan','close']"}],attrs:{size:"mini",type:"info"},on:{click:function(a){return e.closePlan(t.$index,t.row)}}},[e._v("关闭")])],1)]:void 0}}],null,!0)}),a("el-table-column",{attrs:{label:"订单状态",align:"center",prop:"",width:"60"},scopedSlots:e._u([{key:"default",fn:function(t){var a=t.row;return[e._v(" "+e._s(e.setOperation(a.status))+" ")]}}])}),a("el-table-column",{attrs:{label:"发起人",align:"center",prop:"created_user"}}),a("el-table-column",{attrs:{label:"发起时间",align:"center",prop:"created_date"}}),a("el-table-column",{attrs:{label:"完成时间",align:"center",prop:"finish_time"}})],1),a("page",{attrs:{total:e.total,"current-page":e.search.page},on:{currentChange:e.currentChange}}),a("el-dialog",{attrs:{title:"编辑",visible:e.dialogVisible,width:"50%","before-close":e.handleClose},on:{"update:visible":function(t){e.dialogVisible=t}}},[a("el-form",{attrs:{inline:!0}},[a("el-form-item",{attrs:{label:"需求数量"}},[a("el-input",{attrs:{placeholder:"需求数量"},model:{value:e.demandQuantityVal,callback:function(t){e.demandQuantityVal=t},expression:"demandQuantityVal"}})],1)],1),a("span",{staticClass:"dialog-footer",attrs:{slot:"footer"},slot:"footer"},[a("el-button",{on:{click:function(t){e.dialogVisible=!1}}},[e._v("取 消")]),a("el-button",{attrs:{type:"primary",loading:e.loadingBtn},on:{click:e.submitDemandQuantity}},[e._v("确 定")])],1)],1),a("el-dialog",{attrs:{title:"指定出库",visible:e.assignOutboundDialogVisible,"before-close":e.handleCloseNormal,width:"80%"},on:{"update:visible":function(t){e.assignOutboundDialogVisible=t}}},[a("generate-assign-outbound",{ref:"assignOutbound",attrs:{"warehouse-name":e.warehouseName,"warehouse-info":e.warehouseInfo},on:{visibleMethod:e.visibleMethodNormal,visibleMethodSubmit:e.visibleMethodAssignSubmit}})],1),a("el-dialog",{attrs:{title:"正常出库",visible:e.normalOutboundDialogVisible,"before-close":e.handleCloseNormal},on:{"update:visible":function(t){e.normalOutboundDialogVisible=t}}},[a("generate-normal-outbound",{ref:"normalOutbound",attrs:{"warehouse-name":e.warehouseName,"warehouse-info":e.warehouseInfo},on:{visibleMethod:e.visibleMethodNormal,visibleMethodSubmit:e.visibleMethodSubmit}})],1)],1)},r=[],i=(a("ac1f"),a("841c"),a("96cf"),a("1da1")),l=a("b4ac"),o=a("5cfb"),s=a("1f6c"),u=a("64dc"),c=a("3e51"),d=a("cf45"),h=a("ed08"),m={components:{page:c["a"],GenerateAssignOutbound:l["a"],GenerateNormalOutbound:o["a"]},data:function(){return{loading:!1,search:{page:1},dateSearch:[],dialogVisible:!1,total:0,options1:d["a"].statusList,tableData:[],assignOutboundDialogVisible:!1,normalOutboundDialogVisible:!1,currentIndex:null,demandQuantityVal:"",loadingBtn:!1,rowVal:{},warehouseName:"混炼胶库",warehouseInfo:null}},created:function(){var e=new Date,t=e.getTime()+864e5;this.search.st=Object(h["d"])(),this.search.et=Object(h["d"])(t),this.dateSearch=[this.search.st,this.search.et],this.getListWrehouseInfo(),this.getList()},methods:{getList:function(){var e=this;return Object(i["a"])(regeneratorRuntime.mark((function t(){var a;return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:return t.prev=0,e.loading=!0,e.tableData=[],t.next=5,Object(s["M"])("get",null,{params:e.search});case 5:a=t.sent,e.total=a.count,e.tableData=a.results,e.loading=!1,t.next=14;break;case 11:t.prev=11,t.t0=t["catch"](0),e.loading=!1;case 14:case"end":return t.stop()}}),t,null,[[0,11]])})))()},getListWrehouseInfo:function(){var e=this;return Object(i["a"])(regeneratorRuntime.mark((function t(){var a;return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:return t.prev=0,t.next=3,Object(u["j"])({all:1,name:e.warehouseName});case 3:a=t.sent,e.warehouseInfo=a[0].id,t.next=9;break;case 7:t.prev=7,t.t0=t["catch"](0);case 9:case"end":return t.stop()}}),t,null,[[0,7]])})))()},currentChange:function(e){this.search.page=e,this.getList()},warehouseSelect:function(e){},handleCloseNormal:function(e){this.$refs.normalOutbound&&this.$refs.normalOutbound.creadVal(),this.$refs.assignOutbound&&this.$refs.assignOutbound.creadVal(),e()},changeList:function(){this.search.page=1,this.getList()},changeDate:function(e){this.search.st=e?e[0]:"",this.search.et=e?e[1]:"",this.getList(),this.search.page=1},visibleMethodNormal:function(){this.normalOutboundDialogVisible=!1,this.assignOutboundDialogVisible=!1},visibleMethodSubmit:function(e){var t=this;return Object(i["a"])(regeneratorRuntime.mark((function a(){return regeneratorRuntime.wrap((function(a){while(1)switch(a.prev=a.next){case 0:return a.prev=0,a.next=3,Object(s["M"])("post",null,{data:[e]});case 3:t.$message.success("操作成功"),t.normalOutboundDialogVisible=!1,t.getList(),t.$refs.normalOutbound.loadingBtn=!1,t.$refs.normalOutbound.creadVal(),a.next=13;break;case 10:a.prev=10,a.t0=a["catch"](0),t.$refs.normalOutbound.loadingBtn=!1;case 13:case"end":return a.stop()}}),a,null,[[0,10]])})))()},visibleMethodAssignSubmit:function(e){var t=this;return Object(i["a"])(regeneratorRuntime.mark((function a(){return regeneratorRuntime.wrap((function(a){while(1)switch(a.prev=a.next){case 0:return a.prev=0,a.next=3,Object(s["M"])("post",null,{data:e});case 3:t.$message.success("操作成功"),t.assignOutboundDialogVisible=!1,t.$refs.assignOutbound.creadVal(),t.getList(),a.next=12;break;case 9:a.prev=9,a.t0=a["catch"](0),t.$refs.assignOutbound.loadingBtn=!1;case 12:case"end":return a.stop()}}),a,null,[[0,9]])})))()},handleClose:function(e){e()},normalOutbound:function(){d["a"].normalOutboundSwitch?this.normalOutboundDialogVisible=!0:this.$message.info("该功能wms暂时无法使用")},assignOutbound:function(){this.assignOutboundDialogVisible=!0},submitDemandQuantity:function(){var e=this;return Object(i["a"])(regeneratorRuntime.mark((function t(){var a,n;return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:if(t.prev=0,a=e.tableData[e.currentIndex],e.demandQuantityVal||0===e.demandQuantityVal){t.next=5;break}return e.$message.info("需求数量不可为空"),t.abrupt("return");case 5:return n={inventory_type:3333,need_qty:e.demandQuantityVal,order_no:"order_no",warehouse_info:a.warehouse_info},e.loadingBtn=!0,t.next=9,Object(s["M"])("put",a.id,{data:n});case 9:e.dialogVisible=!1,e.loadingBtn=!1,e.getList(),t.next=17;break;case 14:t.prev=14,t.t0=t["catch"](0),e.loadingBtn=!1;case 17:case"end":return t.stop()}}),t,null,[[0,14]])})))()},manualDelivery:function(e){var t=this;this.$confirm("确定出库?","提示",{confirmButtonText:"确定",cancelButtonText:"取消",type:"warning"}).then(Object(i["a"])(regeneratorRuntime.mark((function a(){var n;return regeneratorRuntime.wrap((function(a){while(1)switch(a.prev=a.next){case 0:return n={warehouse_info:e.warehouse_info,inventory_type:e.inventory_type,order_no:e.order_no,material_no:e.material_no,wegit:e.need_weight||"",created_date:e.created_date,pallet_no:e.pallet_no||"",inventory_reason:e.inventory_reason||""},t.loading=!0,a.next=4,Object(s["M"])("put",e.id,{data:n});case 4:t.$message.success("操作成功"),t.getList();case 6:case"end":return a.stop()}}),a)})))).catch((function(){t.loading=!1}))},demandQuantity:function(e,t){this.currentIndex=e,this.dialogVisible=!0,this.demandQuantityVal=t.need_qty||""},closePlan:function(e,t){var a=this;this.$confirm("确定关闭?","提示",{confirmButtonText:"确定",cancelButtonText:"取消",type:"warning"}).then(Object(i["a"])(regeneratorRuntime.mark((function e(){var n;return regeneratorRuntime.wrap((function(e){while(1)switch(e.prev=e.next){case 0:return n={status:5,order_no:"order_no",warehouse_info:a.warehouseInfo},a.loading=!0,e.next=4,Object(s["M"])("put",t.id,{data:n});case 4:a.$message.success("操作成功"),a.getList();case 6:case"end":return e.stop()}}),e)})))).catch((function(){a.loading=!1}))},setOperation:function(e){switch(e){case 1:return"完成";case 2:return"执行中";case 3:return"失败";case 4:return"新建";case 5:return"关闭"}}}},b=m,f=(a("53c1"),a("2877")),p=Object(f["a"])(b,n,r,!1,null,null,null);t["default"]=p.exports},"841c":function(e,t,a){"use strict";var n=a("d784"),r=a("825a"),i=a("1d80"),l=a("129f"),o=a("14c3");n("search",1,(function(e,t,a){return[function(t){var a=i(this),n=void 0==t?void 0:t[e];return void 0!==n?n.call(t,a):new RegExp(t)[e](String(a))},function(e){var n=a(t,e,this);if(n.done)return n.value;var i=r(e),s=String(this),u=i.lastIndex;l(u,0)||(i.lastIndex=0);var c=o(i,s);return l(i.lastIndex,u)||(i.lastIndex=u),null===c?-1:c.index}]}))},"87a12":function(e,t,a){},"8e49":function(e,t,a){"use strict";var n=a("87a12"),r=a.n(n);r.a},b4ac:function(e,t,a){"use strict";var n=function(){var e=this,t=e.$createElement,a=e._self._c||t;return a("div",{directives:[{name:"loading",rawName:"v-loading",value:e.loading,expression:"loading"}],staticClass:"app-container"},[a("el-form",{attrs:{inline:!0}},[a("el-form-item",{attrs:{label:"仓库名称"}},[e._v(" "+e._s(e.warehouseName)+" ")]),a("el-form-item",{attrs:{label:"仓库位置"}},[a("stationInfoWarehouse",{attrs:{"warehouse-name":e.warehouseName,"start-using":!0},on:{changSelect:e.changSelectStation}})],1),a("el-form-item",{attrs:{label:"物料编码"}},[a("el-input",{on:{input:e.changeSearch},model:{value:e.getParams.material_no,callback:function(t){e.$set(e.getParams,"material_no",t)},expression:"getParams.material_no"}})],1),a("el-form-item",{attrs:{label:"品质状态"}},[a("el-select",{attrs:{placeholder:"请选择",clearable:""},on:{change:e.changeSearch},model:{value:e.getParams.quality_status,callback:function(t){e.$set(e.getParams,"quality_status",t)},expression:"getParams.quality_status"}},e._l(e.options,(function(e){return a("el-option",{key:e,attrs:{label:e,value:e}})})),1)],1)],1),a("el-table",{ref:"multipleTable",staticStyle:{width:"100%"},attrs:{border:"",data:e.tableData,"row-key":e.getRowKeys},on:{"selection-change":e.handleSelectionChange}},[a("el-table-column",{attrs:{type:"selection",width:"40","reserve-selection":!0}}),a("el-table-column",{attrs:{label:"物料类型",align:"center",prop:"material_type"}}),a("el-table-column",{attrs:{label:"物料编码",align:"center",prop:"material_no"}}),a("el-table-column",{attrs:{label:"lot",align:"center",prop:"lot_no"}}),a("el-table-column",{attrs:{label:"托盘号",align:"center",prop:"container_no"}}),a("el-table-column",{attrs:{label:"库存位",align:"center",prop:"location"}}),"终炼胶库"===e.warehouseName?a("el-table-column",{attrs:{label:"车次",align:"center",prop:""},scopedSlots:e._u([{key:"default",fn:function(t){var a=t.row;return[e._v(" "+e._s(a.qty)+" ")]}}],null,!1,1845176995)}):e._e(),a("el-table-column",{attrs:{label:"总重量",align:"center",prop:"total_weight"}}),a("el-table-column",{attrs:{label:"品质状态",align:"center"},scopedSlots:e._u([{key:"default",fn:function(t){var n=t.row;return["帘布库出库计划"===e.$route.meta.title?a("span",[e._v(e._s(n.quality_status))]):a("span",[e._v(e._s(n.quality_level))])]}}])}),a("el-table-column",{attrs:{label:"入库时间",align:"center",prop:"in_storage_time"}}),a("el-table-column",{attrs:{label:"机台号",align:"center",prop:"equip_no"}}),a("el-table-column",{attrs:{label:"车号",align:"center",prop:"memo"}}),"终炼胶出库计划"===e.$route.meta.title?a("el-table-column",{attrs:{label:"关联发货计划",align:"center",width:"120"},scopedSlots:e._u([{key:"default",fn:function(t){return[e._v(" "+e._s(t.row.deliveryPlan)+" "),a("el-button",{attrs:{size:"mini",type:"primary"},on:{click:function(a){return e.deliverClick(t.row,t.$index)}}},[e._v("添加发货计划")])]}}],null,!1,2461161841)}):e._e(),"混炼胶出库计划"===e.$route.meta.title?a("el-table-column",{attrs:{label:"机台号",align:"center","min-width":"100"},scopedSlots:e._u([{key:"default",fn:function(t){return[a("EquipSelect",{attrs:{"is-multiple":!0},on:{equipSelected:function(a){return e.equipSelected(a,t.$index)}}})]}}],null,!1,3155262495)}):e._e()],1),a("page",{attrs:{total:e.total,"current-page":e.getParams.page},on:{currentChange:e.currentChange}}),a("div",{staticClass:"dialog-footer",attrs:{slot:"footer"},slot:"footer"},[a("el-button",{on:{click:function(t){return e.visibleMethod(!0)}}},[e._v("取 消")]),a("el-button",{attrs:{type:"primary",loading:e.loadingBtn},on:{click:function(t){return e.visibleMethod(!1)}}},[e._v("确 定")])],1),a("el-dialog",{attrs:{title:"发货计划管理",visible:e.dialogVisible,width:"90%","append-to-body":""},on:{"update:visible":function(t){e.dialogVisible=t}}},[a("receiveList",{ref:"receiveList",attrs:{show:e.dialogVisible,"is-dialog":!0,"defalut-val":e.handleSelection,"material-no":e.material_no_current}}),a("span",{staticClass:"dialog-footer",attrs:{slot:"footer"},slot:"footer"},[a("el-button",{on:{click:function(t){e.dialogVisible=!1}}},[e._v("取 消")]),a("el-button",{attrs:{type:"primary"},on:{click:e.sureDeliveryPlan}},[e._v("确 定")])],1)],1)],1)},r=[],i=(a("4160"),a("caad"),a("b0c0"),a("a9e3"),a("159b"),a("25f6")),l=a("3e51"),o=a("a5db"),s=a("1c7e2"),u=a("8448"),c={components:{EquipSelect:u["a"],page:l["a"],stationInfoWarehouse:o["a"],receiveList:s["default"]},props:{warehouseName:{type:String,default:""},warehouseInfo:{type:Number,default:null}},data:function(){return{tableData:[],getParams:{page:1,location_status:"有货货位",material_type:"",material_no:"",container_no:"",warehouse_name:this.warehouseName},currentPage:1,total:0,options:["终炼胶库","混炼胶库"].includes(this.warehouseName)?["一等品","三等品"]:["合格品","不合格品"],loading:!1,multipleSelection:[],loadingBtn:!1,dialogVisible:!1,material_no_current:"",currentIndex:null,handleSelection:[]}},computed:{},created:function(){this.getTableData()},methods:{getTableData:function(){var e=this;this.loading=!0,Object(i["a"])(this.getParams).then((function(t){e.tableData=t.results,e.total=t.count,e.tableData.forEach((function(t){e.$set(t,"_DeliveryPlan",[])})),e.loading=!1})).catch((function(){e.loading=!1}))},currentChange:function(e){this.currentPage=e,this.getParams.page=e,this.getTableData()},changeSearch:function(){this.getParams.page=1,this.getTableData()},changeMaterialType:function(e){this.getParams.material_type=e,this.getParams.page=1,this.getTableData()},warehouseSelect:function(e){this.getParams.page=1,this.getParams.warehouse_name=e,this.getTableData()},creadVal:function(){this.$refs.multipleTable.clearSelection(),this.loadingBtn=!1,this.multipleSelection=[],this.tableData.forEach((function(e){e.equipNoArr=null,e._DeliveryPlan=null,e.deliveryPlan=null}))},visibleMethod:function(e){var t=this;if(e)this.creadVal(),this.$emit("visibleMethod");else{if(!this.getParams.station)return void this.$message.info("请选择仓库位置！");if(0===this.multipleSelection.length)return;var a=[];this.multipleSelection.forEach((function(e){a.push({station:t.getParams.station,order_no:"order_no",pallet_no:e.container_no,need_qty:e.qty,need_weight:e.total_weight,material_no:e.material_no,inventory_type:"指定出库",inventory_reason:e.inventory_reason,unit:e.unit,status:4,warehouse_info:t.warehouseInfo,quality_status:e.quality_status,dispatch:e.dispatch||[],equip:e.equip||[],location:e.location})})),this.loadingBtn=!0,this.$emit("visibleMethodSubmit",a)}},changSelectStation:function(e){this.getParams.station=e?e.name:""},handleSelectionChange:function(e){e.length>0&&(this.multipleSelection=e)},getRowKeys:function(e){return e.id},sureDeliveryPlan:function(){var e=this;this.dialogVisible=!1,this.tableData[this.currentIndex]._DeliveryPlan=this.$refs.receiveList.handleSelection,this.handleSelection=this.tableData[this.currentIndex]._DeliveryPlan;var t="",a=[];this.$refs.receiveList.handleSelection.forEach((function(n){t+=n.order_no+";",e.$set(e.tableData[e.currentIndex],"deliveryPlan",t),a.push(n.id)})),this.tableData[this.currentIndex].dispatch=a||[],this.handleSelection&&0!==this.handleSelection.length||this.$set(this.tableData[this.currentIndex],"deliveryPlan","")},deliverClick:function(e,t){this.material_no_current=e.material_no,this.currentIndex=t,this.handleSelection=this.tableData[this.currentIndex]._DeliveryPlan,this.dialogVisible=!0},equipSelected:function(e,t){this.$set(this.tableData[t],"equip",e)}}},d=c,h=(a("27c9"),a("2877")),m=Object(h["a"])(d,n,r,!1,null,"9d40fe64",null);t["a"]=m.exports},b633:function(e,t,a){}}]);