(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-7443ccc2"],{2275:function(t,e,a){"use strict";a.r(e);var n=function(){var t=this,e=t.$createElement,a=t._self._c||e;return a("div",[a("el-form",{attrs:{inline:!0}},[a("el-form-item",{attrs:{label:"类型"}},[a("el-select",{attrs:{multiple:"",placeholder:"请选择"},on:{change:t.getTableData,"visible-change":t.visibleChange},model:{value:t.getParams.type_name,callback:function(e){t.$set(t.getParams,"type_name",e)},expression:"getParams.type_name"}},t._l(t.typeOptions,(function(t){return a("el-option",{key:t.global_name,attrs:{label:t.global_name,value:t.global_name}})})),1)],1),a("el-form-item",{attrs:{label:"库存位"}},[a("inventoryPosition",{on:{changSelect:t.changSelect}})],1),a("el-form-item",{staticStyle:{float:"right"}},[a("el-button",{directives:[{name:"permission",rawName:"v-permission",value:["spare_location","add"],expression:"['spare_location', 'add']"}],on:{click:t.showCreateDialog}},[t._v("新建")])],1)],1),a("el-table",{staticStyle:{width:"100%"},attrs:{data:t.tableData,border:""}},[a("el-table-column",{attrs:{align:"center",type:"index",label:"No",width:"50"}}),a("el-table-column",{attrs:{prop:"type_name",label:"类型"}}),a("el-table-column",{attrs:{prop:"name",label:"库存位"}}),a("el-table-column",{attrs:{label:"操作"},scopedSlots:t._u([{key:"default",fn:function(e){return[a("el-button-group",[a("el-button",{directives:[{name:"permission",rawName:"v-permission",value:["spare_location","change"],expression:"['spare_location', 'change']"}],attrs:{size:"mini"},on:{click:function(a){return t.showEditDialog(e.row)}}},[t._v("编辑")]),a("el-button",{directives:[{name:"permission",rawName:"v-permission",value:["spare_location","delete"],expression:"['spare_location', 'delete']"}],attrs:{size:"mini",type:"danger"},on:{click:function(a){return t.handleDelete(e.row)}}},[t._v(t._s(e.row.used_flag?"停用":"启用")+" ")])],1)]}}])})],1),a("page",{attrs:{"old-page":!1,total:t.total,"current-page":t.getParams.page},on:{currentChange:t.currentChange}}),a("el-dialog",{attrs:{title:"添加位置点",visible:t.dialogCreateVisible,"close-on-click-modal":!1},on:{"update:visible":function(e){t.dialogCreateVisible=e}}},[a("el-form",{ref:"createForm",attrs:{rules:t.rules,model:t.locationForm,"label-width":"100px"}},[a("el-form-item",{attrs:{label:"类型",prop:"type"}},[a("el-select",{attrs:{placeholder:"请选择"},model:{value:t.locationForm.type,callback:function(e){t.$set(t.locationForm,"type",e)},expression:"locationForm.type"}},t._l(t.typeOptions,(function(t){return a("el-option",{key:t.id,attrs:{label:t.global_name,value:t.id}})})),1)],1),a("el-form-item",{attrs:{label:"位置点",prop:"name"}},[a("el-input",{model:{value:t.locationForm.name,callback:function(e){t.$set(t.locationForm,"name",e)},expression:"locationForm.name"}})],1)],1),a("div",{staticClass:"dialog-footer",attrs:{slot:"footer"},slot:"footer"},[a("el-button",{on:{click:function(e){t.dialogCreateVisible=!1}}},[t._v("取 消")]),a("el-button",{attrs:{type:"primary"},on:{click:t.handleCreate}},[t._v("确 定")])],1)],1),a("el-dialog",{attrs:{title:"编辑位置点",visible:t.dialogEditVisible,"close-on-click-modal":!1},on:{"update:visible":function(e){t.dialogEditVisible=e}}},[a("el-form",{ref:"editForm",attrs:{rules:t.rules,model:t.locationForm,"label-width":"100px"}},[a("el-form-item",{attrs:{label:"类型",prop:"type"}},[a("el-select",{attrs:{placeholder:"请选择"},model:{value:t.locationForm.type,callback:function(e){t.$set(t.locationForm,"type",e)},expression:"locationForm.type"}},t._l(t.typeOptions,(function(t){return a("el-option",{key:t.id,attrs:{label:t.global_name,value:t.id}})})),1)],1),a("el-form-item",{attrs:{label:"位置点",prop:"name"}},[a("el-input",{model:{value:t.locationForm.name,callback:function(e){t.$set(t.locationForm,"name",e)},expression:"locationForm.name"}})],1)],1),a("div",{staticClass:"dialog-footer",attrs:{slot:"footer"},slot:"footer"},[a("el-button",{on:{click:function(e){t.dialogEditVisible=!1}}},[t._v("取 消")]),a("el-button",{attrs:{type:"primary"},on:{click:t.handleEdit}},[t._v("确 定")])],1)],1)],1)},o=[],r=(a("b0c0"),a("b775")),i=a("99b1");function l(t){return Object(r["a"])({url:i["a"].SpareLocation,method:"get",params:t})}function c(t){return Object(r["a"])({url:i["a"].SpareLocation,method:"post",data:t})}function u(t,e){return Object(r["a"])({url:i["a"].SpareLocation+e+"/",method:"put",data:t})}function s(t){return Object(r["a"])({url:i["a"].SpareLocation+t+"/",method:"delete"})}var d=a("8041"),m=a("3e51"),g=a("6336"),p={components:{inventoryPosition:d["a"],page:m["a"]},data:function(){return{formLabelWidth:"auto",tableData:[],typeOptions:[],types:[],dialogCreateVisible:!1,dialogEditVisible:!1,locationForm:{type:"",name:""},rules:{name:[{required:!0,message:"不能为空",trigger:"blur"}],type:[{required:!0,message:"不能为空",trigger:"change"}]},getParams:{page:1,type_name:[],name:""},currentPage:1,total:1}},created:function(){this.getTableData()},methods:{getTableData:function(){var t=this;l(this.getParams).then((function(e){t.tableData=e.results,t.total=e.count}))},changSelect:function(t){this.getParams.name=t?t.name:"",this.getParams.page=1,this.getTableData()},getTypeOptions:function(){var t=this;Object(g["c"])({all:1,class_name:"备品备件类型"}).then((function(e){t.typeOptions=e.results}))},visibleChange:function(t){t&&this.getTypeOptions()},showCreateDialog:function(){var t=this;this.getTypeOptions(),this.locationForm={type:"",name:""},this.dialogCreateVisible=!0,this.$nextTick((function(){t.$refs.createForm.clearValidate()}))},handleCreate:function(){var t=this;this.$refs.createForm.validate((function(e){e&&c(t.locationForm).then((function(e){t.dialogCreateVisible=!1,t.$message(t.locationForm.name+"创建成功"),t.getTableData()})).catch((function(t){}))}))},showEditDialog:function(t){var e=this;this.getTypeOptions(),this.locationForm=Object.assign({},t),this.dialogEditVisible=!0,this.$nextTick((function(){e.$refs.editForm.clearValidate()}))},handleEdit:function(){var t=this;this.$refs.editForm.validate((function(e){e&&u(t.locationForm,t.locationForm.id).then((function(e){t.dialogEditVisible=!1,t.$message(t.locationForm.name+"修改成功"),t.getTableData()}))}))},handleDelete:function(t){var e=this,a=t.used_flag?"停用":"启用";this.$confirm("此操作将"+a+t.name+", 是否继续?","提示",{confirmButtonText:"确定",cancelButtonText:"取消",type:"warning"}).then((function(){s(t.id).then((function(t){e.$message({type:"success",message:"操作成功!"}),e.getTableData()}))}))},currentChange:function(t,e){this.getParams.page=t,this.getParams.page_size=e,this.getTableData()}}},b=p,f=a("2877"),h=Object(f["a"])(b,n,o,!1,null,null,null);e["default"]=h.exports},6336:function(t,e,a){"use strict";a.d(e,"d",(function(){return r})),a.d(e,"f",(function(){return i})),a.d(e,"h",(function(){return l})),a.d(e,"b",(function(){return c})),a.d(e,"c",(function(){return u})),a.d(e,"e",(function(){return s})),a.d(e,"g",(function(){return d})),a.d(e,"a",(function(){return m}));var n=a("b775"),o=a("99b1");function r(t){return Object(n["a"])({url:o["a"].GlobalTypesUrl,method:"get",params:t})}function i(t){return Object(n["a"])({url:o["a"].GlobalTypesUrl,method:"post",data:t})}function l(t,e){return Object(n["a"])({url:o["a"].GlobalTypesUrl+e+"/",method:"put",data:t})}function c(t){return Object(n["a"])({url:o["a"].GlobalTypesUrl+t+"/",method:"delete"})}function u(t){return Object(n["a"])({url:o["a"].GlobalCodesUrl,method:"get",params:t})}function s(t){return Object(n["a"])({url:o["a"].GlobalCodesUrl,method:"post",data:t})}function d(t,e){return Object(n["a"])({url:o["a"].GlobalCodesUrl+e+"/",method:"put",data:t})}function m(t){return Object(n["a"])({url:o["a"].GlobalCodesUrl+t+"/",method:"delete"})}},"6dfa":function(t,e,a){"use strict";a.d(e,"b",(function(){return r})),a.d(e,"c",(function(){return i})),a.d(e,"d",(function(){return l})),a.d(e,"a",(function(){return c}));var n=a("b775"),o=a("99b1");function r(t){return Object(n["a"])({url:o["a"].MaterialLocationBinding,method:"get",params:t})}function i(t){return Object(n["a"])({url:o["a"].MaterialLocationBinding,method:"post",data:t})}function l(t,e){return Object(n["a"])({url:o["a"].MaterialLocationBinding+e+"/",method:"put",data:t})}function c(t){return Object(n["a"])({url:o["a"].MaterialLocationBinding+t+"/",method:"delete"})}},d585:function(t,e,a){"use strict";a.d(e,"e",(function(){return r})),a.d(e,"k",(function(){return i})),a.d(e,"m",(function(){return l})),a.d(e,"i",(function(){return c})),a.d(e,"l",(function(){return u})),a.d(e,"h",(function(){return s})),a.d(e,"o",(function(){return d})),a.d(e,"n",(function(){return m})),a.d(e,"j",(function(){return g})),a.d(e,"c",(function(){return p})),a.d(e,"d",(function(){return b})),a.d(e,"g",(function(){return f})),a.d(e,"q",(function(){return h})),a.d(e,"a",(function(){return v})),a.d(e,"b",(function(){return y})),a.d(e,"p",(function(){return O})),a.d(e,"f",(function(){return j}));var n=a("b775"),o=a("99b1");function r(t,e){var a=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},r={url:e?o["a"].LocationNameList+e+"/":o["a"].LocationNameList,method:t};return Object.assign(r,a),Object(n["a"])(r)}function i(t,e){var a=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},r={url:e?o["a"].SpareInventory+e+"/":o["a"].SpareInventory,method:t};return Object.assign(r,a),Object(n["a"])(r)}function l(t,e){var a=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},r={url:(e?o["a"].SpareInventory+e+"/":o["a"].SpareInventory)+"check_storage/",method:t};return Object.assign(r,a),Object(n["a"])(r)}function c(t,e){var a=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},r={url:(e?o["a"].SpareInventory+e+"/":o["a"].SpareInventory)+"put_storage/",method:t};return Object.assign(r,a),Object(n["a"])(r)}function u(t,e){var a=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},r={url:e?o["a"].SpareInventoryLog+e+"/":o["a"].SpareInventoryLog,method:t};return Object.assign(r,a),Object(n["a"])(r)}function s(t,e){var a=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},r={url:(e?o["a"].SpareInventory+e+"/":o["a"].SpareInventory)+"out_storage/",method:t};return Object.assign(r,a),Object(n["a"])(r)}function d(t,e){var a=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},r={url:e?o["a"].SparepartsSpareType+e+"/":o["a"].SparepartsSpareType,method:t};return Object.assign(r,a),Object(n["a"])(r)}function m(t,e){var a=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},r={url:e?o["a"].SparepartsSpare+e+"/":o["a"].SparepartsSpare,method:t};return Object.assign(r,a),Object(n["a"])(r)}function g(t,e){var a=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},r={url:(e?o["a"].SpareInventoryLog+e+"/":o["a"].SpareInventoryLog)+"revocation_log/",method:t};return Object.assign(r,a),Object(n["a"])(r)}function p(t,e){var a=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},r={url:e?o["a"].InventoryNow+e+"/":o["a"].InventoryNow,method:t};return Object.assign(r,a),Object(n["a"])(r)}function b(t,e){var a=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},r={url:e?o["a"].InventoryToday+e+"/":o["a"].InventoryToday,method:t};return Object.assign(r,a),Object(n["a"])(r)}function f(t,e){var a=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},r={url:e?o["a"].MixGumOutInventoryLog+e+"/":o["a"].MixGumOutInventoryLog,method:t};return Object.assign(r,a),Object(n["a"])(r)}function h(t,e){var a=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},r={url:e?o["a"].WeightingTackStatus+e+"/":o["a"].WeightingTackStatus,method:t};return Object.assign(r,a),Object(n["a"])(r)}function v(t,e){var a=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},r={url:e?o["a"].BatchChargeLogList+e+"/":o["a"].BatchChargeLogList,method:t};return Object.assign(r,a),Object(n["a"])(r)}function y(t,e){var a=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},r={url:e?o["a"].EquipTank+e+"/":o["a"].EquipTank,method:t};return Object.assign(r,a),Object(n["a"])(r)}function O(t,e){var a=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},r={url:e?o["a"].WeightBatchingLogList+e+"/":o["a"].WeightBatchingLogList,method:t};return Object.assign(r,a),Object(n["a"])(r)}function j(t,e){var a=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},r={url:e?o["a"].MaterialInventoryList+e+"/":o["a"].MaterialInventoryList,method:t};return Object.assign(r,a),Object(n["a"])(r)}}}]);