(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-7f8dbbcf"],{1:function(e,t){},2:function(e,t){},3:function(e,t){},4722:function(e,t,r){"use strict";r.r(t);var o=function(){var e=this,t=e.$createElement,r=e._self._c||t;return r("div",{directives:[{name:"loading",rawName:"v-loading",value:e.loading,expression:"loading"}],staticClass:"roles-manage"},[r("el-form",{attrs:{inline:!0}},[r("el-form-item",{attrs:{label:"角色"}},[r("el-input",{on:{input:e.groupCodeChanged},model:{value:e.getParams.group_code,callback:function(t){e.$set(e.getParams,"group_code",t)},expression:"getParams.group_code"}})],1),r("el-form-item",{attrs:{label:"角色名"}},[r("el-input",{on:{input:e.nameChanged},model:{value:e.getParams.name,callback:function(t){e.$set(e.getParams,"name",t)},expression:"getParams.name"}})],1),r("el-form-item",{attrs:{label:"是否使用"}},[r("el-select",{attrs:{clearable:"",placeholder:"请选择"},on:{change:e.nameChanged},model:{value:e.getParams.use_flag,callback:function(t){e.$set(e.getParams,"use_flag",t)},expression:"getParams.use_flag"}},e._l(e.optionsUser,(function(e){return r("el-option",{key:e.value,attrs:{label:e.label,value:e.value}})})),1)],1),r("el-form-item",{staticStyle:{float:"right"}},[e.checkPermission(["groupextension","add"])?r("el-button",{on:{click:e.showCreateGroupDialog}},[e._v("新建")]):e._e()],1)],1),r("el-table",{directives:[{name:"loading",rawName:"v-loading",value:e.loadingTable,expression:"loadingTable"}],staticStyle:{width:"100%"},attrs:{data:e.tableData,border:""}},[r("el-table-column",{attrs:{updated:"",upstream:"",align:"center",width:"50",type:"index",label:"No"}}),r("el-table-column",{attrs:{prop:"group_code",label:"角色代码"}}),r("el-table-column",{attrs:{prop:"name",label:"角色名称"}}),r("el-table-column",{attrs:{prop:"use_flag",label:"使用",width:"80",formatter:e.formatter}}),r("el-table-column",{attrs:{label:"创建人"},scopedSlots:e._u([{key:"default",fn:function(t){return[e._v(" "+e._s(t.row.created_username?t.row.created_username:"--")+" ")]}}])}),r("el-table-column",{attrs:{prop:"created_date",label:"创建日期"}}),r("el-table-column",{attrs:{label:"操作",width:"150"},scopedSlots:e._u([{key:"default",fn:function(t){return[r("el-button-group",[r("el-button",{directives:[{name:"permission",rawName:"v-permission",value:["groupextension","change"],expression:"['groupextension','change']"}],attrs:{size:"mini"},on:{click:function(r){return e.showEditGroupDialog(t.row)}}},[e._v("编辑 ")]),r("el-button",{directives:[{name:"permission",rawName:"v-permission",value:["groupextension","delete"],expression:"['groupextension','delete']"}],attrs:{size:"mini",type:"danger"},on:{click:function(r){return e.handleGroupDelete(t.row)}}},[e._v(e._s(t.row.use_flag?"停用":"启用")+" ")])],1)]}}])})],1),r("page",{attrs:{total:e.count,"current-page":e.getParams.page},on:{currentChange:e.changePage}}),r("el-dialog",{attrs:{title:e.dialogTitle,visible:e.dialogEditGroupVisible,"close-on-click-modal":!1,width:"800px","before-close":e.handleClose},on:{"update:visible":function(t){e.dialogEditGroupVisible=t}}},[r("el-form",{ref:"groupForm",attrs:{model:e.groupForm}},[r("el-form-item",{attrs:{error:e.groupFormError.group_code,label:"角色代码"}},[r("el-input",{model:{value:e.groupForm.group_code,callback:function(t){e.$set(e.groupForm,"group_code",t)},expression:"groupForm.group_code"}})],1),r("el-form-item",{attrs:{error:e.groupFormError.name,label:"角色名称"}},[r("el-input",{model:{value:e.groupForm.name,callback:function(t){e.$set(e.groupForm,"name",t)},expression:"groupForm.name"}})],1),r("el-form-item",{attrs:{label:"权限设置",size:"medium"}},[r("transferLimit",{attrs:{"group-id":e.groupForm.id},on:{changeTransferPermissions:e.changeTransferPermissions}})],1)],1),r("div",{staticClass:"dialog-footer",attrs:{slot:"footer"},slot:"footer"},[r("el-button",{on:{click:function(t){e.dialogEditGroupVisible=!1}}},[e._v("取 消")]),r("el-button",{attrs:{type:"primary"},on:{click:function(t){return e.handleEditGroup("groupForm")}}},[e._v("确 定")])],1)],1)],1)},n=[],a=(r("053b"),r("e793")),i=r("5630"),s=r("3e51"),l=function(){var e=this,t=e.$createElement,r=e._self._c||t;return r("div",{directives:[{name:"loading",rawName:"v-loading",value:e.loading,expression:"loading"}],staticClass:"transferLimit"},[e.permissionsData.length>0?r("el-table",{staticStyle:{width:"100%"},attrs:{data:e.permissionsData,border:""}},[r("el-table-column",{attrs:{prop:"name",label:"菜单",width:"180"}}),r("el-table-column",{attrs:{label:"权限"},scopedSlots:e._u([{key:"default",fn:function(t){return[r("el-checkbox",{on:{change:function(r){return e.handleCheckAllChange(r,t.row,t.row.permissions)}},model:{value:t.row.checkAll,callback:function(r){e.$set(t.row,"checkAll",r)},expression:"scope.row.checkAll"}},[e._v("全选")]),r("div",{staticStyle:{margin:"15px 0"}}),r("el-checkbox-group",{on:{change:function(r){return e.handleCheckedCitiesChange(r,t.row)}},model:{value:t.row.checkedCities,callback:function(r){e.$set(t.row,"checkedCities",r)},expression:"scope.row.checkedCities"}},e._l(t.row.permissions,(function(t){return r("el-checkbox",{key:t.id,attrs:{label:t.id}},[e._v(e._s(t.name))])})),1)]}}],null,!1,860461732)})],1):e._e()],1)},u=[],c=(r("fe59"),r("513c"),r("08ba"),r("5748")),d=r("b775"),g=r("99b1");function m(e,t){var r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},o={url:t?g["a"].PermissionUrl+t+"/":g["a"].PermissionUrl,method:e};return Object.assign(o,r),Object(d["a"])(o)}var p={props:{defaultPermissions:{type:Array,default:function(){return[]}},groupId:{type:Number,default:0}},data:function(){return{permissionsData:[],loading:!0}},computed:{},watch:{groupId:function(){this.permissionsData.forEach((function(e){e.permissions.forEach((function(e){e.checkedCities=[]})),e.checkAll=!1})),this.getPermissions()}},mounted:function(){this.getPermissions()},methods:{getPermissions:function(){var e=this;this.loading=!0;var t={};this.groupId&&(t={params:{group_id:this.groupId}}),m("get",null,t).then((function(t){var r=t.result||[];e.permissionsData=r,e.permissionsData.forEach((function(t){var r=[];t.permissions.forEach((function(e){e.has_permission&&r.push(e.id)})),t.permissions.length===r.length?e.$set(t,"checkAll",!0):e.$set(t,"checkAll",!1),e.$set(t,"checkedCities",r)})),e.loading=!1})).catch((function(){e.loading=!1}))},handleCheckAllChange:function(e,t,r){var o=[];r.forEach((function(e){o.push(e.id)})),t.checkedCities=e?o:[],this.setPermissionsData()},handleCheckedCitiesChange:function(e,t){var r=e.length;t.checkAll=r===t.permissions.length,this.setPermissionsData()},setPermissionsData:function(e){var t=[];this.permissionsData.forEach((function(e){t.push.apply(t,Object(c["a"])(e.checkedCities))})),this.$emit("changeTransferPermissions",t)}}},f=p,h=(r("5e20a"),r("9ca4")),b=Object(h["a"])(f,l,u,!1,null,"15df56b4",null),v=b.exports,_=r("ed08"),k={components:{page:s["a"],transferLimit:v},data:function(){return{getParams:{page:1,use_flag:null},tableData:[],count:0,group_code:"",name:"",groupForm:{name:"",group_code:"",use_flag:!0},groupFormError:{name:"",group_code:"",use_flag:""},permissions:[],dialogEditGroupVisible:!1,dialogTitle:"新增角色",loading:!0,loadingTable:!1,optionsUser:[{value:1,label:"Y"},{value:0,label:"N"}]}},computed:{},created:function(){this.currentChange()},methods:{checkPermission:_["a"],currentChange:function(){var e=this;this.loadingTable=!0,Object(i["a"])("get",null,{params:this.getParams}).then((function(t){e.loading=!1,e.loadingTable=!1,e.count=t.count||0,e.tableData=t.results||[]})).catch((function(t){e.loading=!1,e.loadingTable=!1}))},formatter:function(e,t){return e.use_flag?"Y":"N"},changePage:function(e){this.getParams["page"]=e,this.currentChange()},groupCodeChanged:function(){this.getParams["page"]=1,this.currentChange()},nameChanged:function(){this.getParams["page"]=1,this.currentChange()},clearGroupForm:function(){this.groupForm={name:"",group_code:"",use_flag:!0}},clearGroupFormError:function(){this.groupFormError={name:"",group_code:"",use_flag:""}},showCreateGroupDialog:function(){this.clearGroupForm(),this.clearGroupFormError(),this.dialogTitle="新增角色",this.dialogEditGroupVisible=!0},handleEditGroup:function(){var e=this;this.clearGroupFormError();var t=this.groupForm.id?"put":"post",r=this.groupForm.id?this.groupForm.id:"";Object(i["a"])(t,r,{data:Object(a["a"])({},this.groupForm)}).then((function(t){e.dialogEditGroupVisible=!1,e.$message.success(e.groupForm.name+e.groupForm.id?"编辑成功":"创建成功"),e.groupForm.id=null,e.currentChange()})).catch((function(e){}))},showEditGroupDialog:function(e){this.groupForm=JSON.parse(JSON.stringify(e)),this.clearGroupFormError(),this.dialogTitle="编辑角色",this.dialogEditGroupVisible=!0},handleGroupDelete:function(e){var t=this,r=e.use_flag?"停用":"启用",o="确定"+r+e.name+(e.use_flag?"，且解除该角色下所有用户":"")+", 是否继续?";this.$confirm(o,"提示",{confirmButtonText:"确定",cancelButtonText:"取消",type:"warning"}).then((function(){Object(i["a"])("delete",e.id).then((function(e){t.$message({type:"success",message:"操作成功!"}),t.currentChange()}))}))},changeTransferPermissions:function(e){this.$set(this.groupForm,"permissions",e)},handleClose:function(e){this.groupForm.id=null,e()}}},w=k,C=(r("a194"),Object(h["a"])(w,o,n,!1,null,null,null));t["default"]=C.exports},"4f5b":function(e,t,r){},5630:function(e,t,r){"use strict";r.d(t,"a",(function(){return a}));var o=r("b775"),n=r("99b1");function a(e,t){var r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},a={url:t?n["a"].GroupUrl+t+"/":n["a"].GroupUrl,method:e};return Object.assign(a,r),Object(o["a"])(a)}},"5e20a":function(e,t,r){"use strict";var o=r("4f5b"),n=r.n(o);n.a},a194:function(e,t,r){"use strict";var o=r("fbde"),n=r.n(o);n.a},ed08:function(e,t,r){"use strict";r.d(t,"d",(function(){return u})),r.d(t,"b",(function(){return d})),r.d(t,"a",(function(){return g})),r.d(t,"c",(function(){return m}));r("fe59"),r("b130"),r("ecb4"),r("d497"),r("513c"),r("fe8a"),r("e18c"),r("84c2"),r("e35a"),r("1c2e"),r("90aa"),r("898e"),r("5e9f"),r("0d7a"),r("08ba");var o=r("f7f9"),n=r("4360"),a=r("ecc0"),i=r.n(a),s=r("d85b"),l=r.n(s);function u(e,t,r){var o=e?new Date(e):new Date,n={y:o.getFullYear(),m:c(o.getMonth()+1),d:c(o.getDate()),h:c(o.getHours()),i:c(o.getMinutes()),s:c(o.getSeconds()),a:c(o.getDay())};return t?n.y+"-"+n.m+"-"+n.d+" "+n.h+":"+n.i+":"+n.s:r&&"continuation"===r?n.y+n.m+n.d+n.h+n.i+n.s:n.y+"-"+n.m+"-"+n.d}function c(e){return e=Number(e),e<10?"0"+e:e}function d(e){if(!e&&"object"!==Object(o["a"])(e))throw new Error("error arguments","deepClone");var t=e.constructor===Array?[]:{};return Object.keys(e).forEach((function(r){e[r]&&"object"===Object(o["a"])(e[r])?t[r]=d(e[r]):t[r]=e[r]})),t}function g(e){if(e&&e instanceof Array&&e.length>0){var t=n["a"].getters&&n["a"].getters.permission,r=t[e[0]];if(!r||0===r.length)return;var o=r.some((function(t){return t===e[1]}));return o}return console.error("need roles! Like v-permission=\"['admin','editor']\""),!1}function m(e){var t=l.a.utils.table_to_book(document.querySelector("#out-table"),{raw:!0}),r=l.a.write(t,{bookType:"xlsx",bookSST:!0,type:"array"});try{i.a.saveAs(new Blob([r],{type:"application/octet-stream"}),e+".xlsx")}catch(o){"undefined"!==typeof console&&console.log(o,r)}return r}},fbde:function(e,t,r){}}]);