(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-f15db2c2"],{"74d9":function(t,e,a){"use strict";a.r(e);var n=function(){var t=this,e=t.$createElement,a=t._self._c||e;return a("div",{directives:[{name:"loading",rawName:"v-loading",value:t.loading,expression:"loading"}],staticClass:"manual_entry_style"},[a("el-form",{attrs:{inline:!0}},[a("el-form-item",{attrs:{label:"工厂日期："}},[a("el-date-picker",{attrs:{type:"date",placeholder:"选择日期","value-format":"yyyy-MM-dd"},on:{change:t.pageOne},model:{value:t.search.factory_date,callback:function(e){t.$set(t.search,"factory_date",e)},expression:"search.factory_date"}})],1),a("el-form-item",{attrs:{label:"生产机台："}},[a("equip-select",{attrs:{equip_no_props:t.search.equip_no},on:{"update:equip_no_props":function(e){return t.$set(t.search,"equip_no",e)},changeSearch:t.pageOne}})],1),a("el-form-item",{attrs:{label:"班次："}},[a("class-select",{on:{classSelected:t.classSelected}})],1),a("el-form-item",{attrs:{label:"胶料："}},[a("all-product-no-select",{on:{productBatchingChanged:t.productBatchingChanged}})],1)],1),t.tableDataStyle.length>0&&t.tableDataChild.length>0?a("el-table",{staticClass:"rigthTable",attrs:{data:[{}],border:"",width:"100%"}},t._l(t.tableDataStyle,(function(e,n){return a("el-table-column",{key:n,attrs:{label:e.test_indicator,width:0===n?"300":"auto"}},[e.methods.length>0?[t._l(e.methods,(function(n,r){return a("el-radio",{key:r,attrs:{label:n,disabled:!n.allowed},on:{change:function(a){return t.changeMethods(e.test_indicator,e)}},model:{value:e.checkedC,callback:function(a){t.$set(e,"checkedC",a)},expression:"valItem.checkedC"}},[t._v(" "+t._s(n.name)+" ")])})),t._e(),a("br"),a("el-button",{staticStyle:{"margin-top":"5px"},attrs:{size:"mini"},on:{click:function(a){return t.clearRadio(e,n)}}},[t._v("清除")])]:t._e()],2)})),1):t._e(),a("el-button",{directives:[{name:"permission",rawName:"v-permission",value:["test_result","add"],expression:"['test_result','add']"}],staticStyle:{float:"right",margin:"10px 0"},attrs:{loading:t.loadingBtn},on:{click:t.submitTable}},[t._v("保 存")]),a("el-table",{ref:"table",attrs:{data:t.tableDataChild,border:""}},[a("el-table-column",{key:"5",attrs:{type:"index",width:"50",label:"No"}}),a("el-table-column",{key:"4",attrs:{label:"生产信息",align:"center"}},[a("el-table-column",{attrs:{prop:"product_no",label:"胶料编码"}}),a("el-table-column",{attrs:{prop:"lot_no",label:"收皮条码"}}),a("el-table-column",{attrs:{prop:"classes",label:"班次"}}),a("el-table-column",{attrs:{prop:"equip_no",label:"生产机台"}}),a("el-table-column",{attrs:{prop:"actual_trains",label:"车次"}})],1),a("div",{key:"1"},t._l(t.changeTable,(function(e,n){return a("div",{key:n},["{}"!==JSON.stringify(e.checkedC)?a("el-table-column",{attrs:{label:e.test_indicator,align:"center"}},[t._l(e.checkedC.data_points,(function(n,r){return a("el-table-column",{key:r,attrs:{label:n.name},scopedSlots:t._u([{key:"default",fn:function(r){return n.name?[0===t.commandList(e.test_indicator).length&&r.row._list[e.test_indicator]&&r.row._list[e.test_indicator][n.name]?a("el-input-number",{attrs:{"controls-position":"right",min:0,step:"比重"===e.test_indicator?.02:1},on:{change:function(a){return t.detectionValue(r.row,r.$index,r.row._list,e.test_indicator)}},model:{value:r.row._list[e.test_indicator][n.name].value,callback:function(a){t.$set(r.row._list[e.test_indicator][n.name],"value",a)},expression:"scope.row._list[itemTa.test_indicator][itemChild.name].value"}}):t._e(),t.commandList(e.test_indicator).length>0?a("el-dropdown",{attrs:{trigger:"click"},on:{command:function(a){return t.handleCommand(a,r.$index,r.row._list,e.test_indicator,n.name,r.row)}}},[r.row._list[e.test_indicator]&&r.row._list[e.test_indicator][n.name]?a("el-input-number",{attrs:{"controls-position":"right",min:0,step:"比重"===e.test_indicator?.02:1},on:{change:function(a){return t.detectionValue(r.row,r.$index,r.row._list,e.test_indicator)}},model:{value:r.row._list[e.test_indicator][n.name].value,callback:function(a){t.$set(r.row._list[e.test_indicator][n.name],"value",a)},expression:"scope.row._list[itemTa.test_indicator][itemChild.name].value"}}):t._e(),a("el-dropdown-menu",{attrs:{slot:"dropdown"},slot:"dropdown"},t._l(t.commandList(e.test_indicator),(function(e,n){return a("el-dropdown-item",{key:n,staticStyle:{width:"150px"},attrs:{command:e}},[t._v(t._s(e))])})),1)],1):t._e()]:void 0}}],null,!0)})})),a("el-table-column",{attrs:{label:"试验方法"},scopedSlots:t._u([{key:"default",fn:function(a){return[t._v(" "+t._s(e.checkedC.name)+" "),t._e()]}}],null,!0)})],2):t._e()],1)})),0),a("el-table-column",{key:"2",attrs:{label:"备注"},scopedSlots:t._u([{key:"default",fn:function(e){return[a("el-input",{attrs:{placeholder:"请输入内容"},model:{value:e.row.note,callback:function(a){t.$set(e.row,"note",a)},expression:"scope.row.note"}})]}}])}),a("el-table-column",{key:"3",attrs:{label:"操作"},scopedSlots:t._u([{key:"default",fn:function(e){return[a("el-button",{attrs:{size:"mini"},on:{click:function(a){return t.deleteFunction(e.$index)}}},[t._v("删除")])]}}])})],1),a("view-dialog-trial",{attrs:{show:t.dialogVisible},on:{handleClose:function(e){t.dialogVisible=!1}}})],1)},r=[],i=(a("4de4"),a("c740"),a("4160"),a("a434"),a("b0c0"),a("a9e3"),a("ac1f"),a("841c"),a("159b"),a("ade3")),l=(a("96cf"),a("1da1")),o=a("1f6c"),s=a("ed08"),c=a("4090"),u=a("cfc4"),d=a("5dce"),h=function(){var t=this,e=t.$createElement,a=t._self._c||e;return a("div",[a("el-dialog",{attrs:{title:"",visible:t.dialogVisible,width:"80%","before-close":t.handleClose},on:{"update:visible":function(e){t.dialogVisible=e}}},[a("div",{directives:[{name:"loading",rawName:"v-loading",value:t.loading,expression:"loading"}]},[a("el-form",{attrs:{inline:!0}},[a("el-form-item",{staticStyle:{"margin-right":"50px"},attrs:{label:t.showData.type_name}}),a("el-form-item",{attrs:{label:"胶料编码:"}},[t._v(" "+t._s(t.showData.material_no)+" ")]),t.testMethodSelectShow?a("el-form-item",{attrs:{label:"试验方法:"}},[a("testMethodSelect",{attrs:{"create-load":!0,"test-type-id":t.showData.test_type_id,testmodeprop:t.testMode},on:{changeSelect:t.testMethodChange}})],1):t._e()],1),a("el-table",{attrs:{data:t.tableData,border:"","span-method":t.objectSpanMethod}},[a("el-table-column",{attrs:{prop:"level",label:"等级"}}),a("el-table-column",{attrs:{prop:"result",label:"处理意见"}}),a("el-table-column",{key:0,attrs:{prop:"limits_val",label:"区分"}}),t._l(t.headTable,(function(e,n){return a("el-table-column",{key:n+1,attrs:{label:e.name},scopedSlots:t._u([{key:"default",fn:function(n){return["上限"===n.row.limits_val?a("span",[t._v(" "+t._s(n.row[e.name]?n.row[e.name].upper_limit:"")+" ")]):a("span",[t._v(" "+t._s(n.row[e.name]?n.row[e.name].lower_limit:"")+" ")])]}}],null,!0)})}))],2)],1)])],1)},f=[],b=(a("d3b7"),a("3ca3"),a("ddb0"),a("dbca")),p={components:{testMethodSelect:b["a"]},props:{show:Boolean,showData:{type:Object,default:function(){return{}}}},data:function(){return{dialogVisible:!1,testMode:"",search:this.showData,loading:!0,testMethodSelectShow:!1,tableData:[],headTable:[]}},watch:{show:function(t){this.dialogVisible=t,t&&(this.testMethodSelectShow=!0,this.search=this.showData)}},methods:{getList:function(){var t=this;return Object(l["a"])(regeneratorRuntime.mark((function e(){var a,n;return regeneratorRuntime.wrap((function(e){while(1)switch(e.prev=e.next){case 0:return e.prev=0,e.next=3,Object(o["w"])("get",null,{params:t.search});case 3:return a=e.sent,n=[],a.forEach((function(t,e){t.limits_val="上限",n.push(t);var a=Object(s["b"])(t);a.limits_val="下限",n.push(a)})),e.abrupt("return",n);case 9:e.prev=9,e.t0=e["catch"](0),t.loading=!1;case 12:case"end":return e.stop()}}),e,null,[[0,9]])})))()},getTestTypes:function(){var t=this;return Object(l["a"])(regeneratorRuntime.mark((function e(){var a;return regeneratorRuntime.wrap((function(e){while(1)switch(e.prev=e.next){case 0:return e.prev=0,e.next=3,Object(o["A"])("get",null,{params:t.search});case 3:return a=e.sent,e.abrupt("return",a);case 7:e.prev=7,e.t0=e["catch"](0),t.loading=!1;case 10:case"end":return e.stop()}}),e,null,[[0,7]])})))()},handleClose:function(t){this.$emit("handleClose",!1),this.testMethodSelectShow=!1,t()},objectSpanMethod:function(t){t.row,t.column;var e=t.rowIndex,a=t.columnIndex;if(0===a||1===a)return e%2===0?{rowspan:2,colspan:1}:{rowspan:0,colspan:0}},testMethodChange:function(t){var e=this;this.search.test_method_id=t,Promise.all([this.getList(),this.getTestTypes()]).then((function(t){e.tableData=t[0],e.headTable=t[1],e.loading=!1})).catch((function(t){e.loading=!1}))}}},m=p,_=a("2877"),g=Object(_["a"])(m,h,f,!1,null,"2678feac",null),v=g.exports,w={components:{equipSelect:c["a"],classSelect:u["a"],allProductNoSelect:d["a"],viewDialogTrial:v},data:function(){return{dialogVisible:!1,loading:!1,total:0,search:{ShiftRules:"",factory_date:Object(s["d"])(),equip_no:"",classes:"",product_no:""},tableData:[],tableDataStyle:[],tableDataChild:[],showTableDataChild:!1,changeTable:[],loadingBtn:!1,arr:[]}},mounted:function(){},methods:{getTableDataChild:function(){var t=this;return Object(l["a"])(regeneratorRuntime.mark((function e(){var a;return regeneratorRuntime.wrap((function(e){while(1)switch(e.prev=e.next){case 0:return e.prev=0,t.titleInfo(t.search.equip_no,"请输入生产机台"),t.titleInfo(t.search.classes,"请输入班次"),t.titleInfo(t.search.product_no,"请输入胶料"),t.titleInfo(t.search.factory_date,"请输入时间"),t.loading=!0,e.next=8,Object(o["F"])("get",null,{params:t.search});case 8:a=e.sent,t.getTestType(t.search.product_no),t.tableDataChild=a||[],t.tableDataChild.forEach((function(e,a){t.$set(e,"_index",a)})),t.loading=!1,e.next=18;break;case 15:e.prev=15,e.t0=e["catch"](0),t.loading=!1;case 18:case"end":return e.stop()}}),e,null,[[0,15]])})))()},titleInfo:function(t,e){if(!t&&0!==t)throw this.$message.info(e),new Error(e)},getList:function(){var t=this;return Object(l["a"])(regeneratorRuntime.mark((function e(){var a;return regeneratorRuntime.wrap((function(e){while(1)switch(e.prev=e.next){case 0:return t.clearData(),t.showTableDataChild=!1,e.prev=2,t.loading=!0,e.next=6,Object(o["E"])("get",null,{params:t.search});case 6:a=e.sent,t.tableData=a.results||[],t.total=a.count,t.loading=!1,e.next=15;break;case 12:e.prev=12,e.t0=e["catch"](2),t.loading=!1;case 15:case"end":return e.stop()}}),e,null,[[2,12]])})))()},getTestType:function(t){var e=this;return Object(l["a"])(regeneratorRuntime.mark((function a(){var n;return regeneratorRuntime.wrap((function(a){while(1)switch(a.prev=a.next){case 0:return a.prev=0,a.next=3,Object(o["x"])("get",null,{params:{material_no:t}});case 3:n=a.sent,e.tableDataStyle=n||[],e.tableDataStyle.forEach((function(t){e.$set(t,"checkedC",{})})),a.next=10;break;case 8:a.prev=8,a.t0=a["catch"](0);case 10:case"end":return a.stop()}}),a,null,[[0,8]])})))()},changeMethods:function(t,e){y(this,e)},clearRadio:function(t,e){var a=this;"{}"!==JSON.stringify(t.checkedC)&&(this.$set(this.tableDataStyle[e],"checkedC",{}),this.$nextTick((function(){y(a,t)})))},currentChange:function(t){this.search.page=t,this.getList()},pageOne:function(){this.getTableDataChild(),this.tableDataStyle.forEach((function(t){t.checkedC={}})),this.changeTable=[]},planScheduleSelected:function(t){this.search.ShiftRules=t,this.pageOne()},classSelected:function(t){this.search.classes=t,this.pageOne()},productBatchingChanged:function(t){this.search.product_no=t?t.material_no:"",this.pageOne()},rowClick:function(t){this.getTestType(t.product_no),this.clearData(),this.showTableDataChild=!0;for(var e=parseInt(Number(t.end_trains)-Number(t.begin_trains)+1),a=0;a<e;a++){var n=JSON.parse(JSON.stringify(t));this.$set(n,"input",""),this.$set(n,"actual_trains",Number(t.begin_trains)+a),this.tableDataChild.push(n)}},clearData:function(){this.changeTable=[],this.tableDataStyle=[],this.tableDataChild=[]},deleteFunction:function(t){var e=this;this.$confirm("是否删除?","提示",{confirmButtonText:"确定",cancelButtonText:"取消",type:"warning"}).then((function(){e.tableDataChild.splice(t,1)}))},viewTrial:function(){this.dialogVisible=!0},handleCommand:function(t,e,a,n,r,i){this.$set(this.tableDataChild[e]._list[n][r],"value",t),this.detectionValue(i,e,a)},commandList:function(t){var e=JSON.parse(localStorage.getItem("detectionValue"))||{};return"比重"===t?e[t]||[1.11,1.13,1.15]:"硬度"===t?e[t]||[59]:[]},detectionValue:function(t,e,a,n){var r=JSON.parse(localStorage.getItem("detectionValue"))||{},i="{}"!==JSON.stringify(r)&&r[n]?r[n]:[];for(var l in t._filledIn=!1,a)for(var o in a[l])a[l][o]&&a[l][o].value&&(t._filledIn=!0,a[n]&&a[n][o]&&a[n][o].value&&(i.unshift(a[n][o].value),i.length>3&&i.pop(),this.$set(r,n,i),localStorage.setItem("detectionValue",JSON.stringify(r))))},testMethodChange:function(t,e){if(e)for(var a in e)e[a]&&this.$set(e[a],"test_method_name",t)},submitTable:function(){var t=this;return Object(l["a"])(regeneratorRuntime.mark((function e(){var a,n,r;return regeneratorRuntime.wrap((function(e){while(1)switch(e.prev=e.next){case 0:if(a=[],e.prev=1,0!==t.tableDataChild.length){e.next=4;break}return e.abrupt("return");case 4:n=t.tableDataChild.filter((function(t){return t._filledIn})),r=Object(s["b"])(n),r.forEach((function(e,n){var r=[];if(!e.lot_no)throw t.$message.error("收皮条码不能为空！"),new Error("收皮条码不能为空！");if("{}"!==JSON.stringify(e._list))for(var i in e._list)for(var l in e._list[i])e._list[i][l]&&(e._list[i][l].value||(e._list[i][l].value=null),r.push(e._list[i][l]));a[n]={lot_no:e.lot_no,actual_trains:e.actual_trains,product_no:e.product_no,plan_classes_uid:e.plan_classes_uid,production_class:e.classes,production_equip_no:e.equip_no,production_factory_date:t.search.factory_date,note:e.note,order_results:r}})),e.next=12;break;case 9:return e.prev=9,e.t0=e["catch"](1),e.abrupt("return");case 12:return t.loadingBtn=!0,e.prev=13,e.next=16,Object(o["B"])("post",null,{data:a});case 16:t.$message.success("录入成功"),t.loadingBtn=!1,e.next=23;break;case 20:e.prev=20,e.t1=e["catch"](13),t.loadingBtn=!1;case 23:case"end":return e.stop()}}),e,null,[[1,9],[13,20]])})))()}}};function y(t,e){var a={},n={},r={};if("{}"!==JSON.stringify(e.checkedC)){var l=Object(s["b"])(e.checkedC.data_points);l.forEach((function(n){var i={};t.$set(i,"test_indicator_name",e.test_indicator),t.$set(i,"data_point_name",n.name),t.$set(i,"test_method_name",e.checkedC.name),t.$set(i,"value",void 0),r=Object(s["b"])(i),t.$set(a,n.name,r)})),Object.assign(n,Object(i["a"])({},e.test_indicator,a))}var o=t.changeTable.findIndex((function(t){return t.test_indicator===e.test_indicator}));o>-1?"{}"===JSON.stringify(e.checkedC)?(t.tableDataChild.forEach((function(t){delete t._list[e.test_indicator]})),t.changeTable.splice(o,1)):t.changeTable[o]=e:t.changeTable.push(e),t.tableDataChild.forEach((function(a){if("{}"!==JSON.stringify(e.checkedC)){var r=Object(s["b"])(n);a._list||t.$set(a,"_list",{});var i=Object.assign({},a._list,r);t.$set(a,"_list",i)}else delete a._list[e.test_indicator]}))}var k=w,O=(a("8b91"),Object(_["a"])(k,n,r,!1,null,"77bcc595",null));e["default"]=O.exports},"8b91":function(t,e,a){"use strict";var n=a("cf7a"),r=a.n(n);r.a},c740:function(t,e,a){"use strict";var n=a("23e7"),r=a("b727").findIndex,i=a("44d2"),l=a("ae40"),o="findIndex",s=!0,c=l(o);o in[]&&Array(1)[o]((function(){s=!1})),n({target:"Array",proto:!0,forced:s||!c},{findIndex:function(t){return r(this,t,arguments.length>1?arguments[1]:void 0)}}),i(o)},cf7a:function(t,e,a){},daa1:function(t,e,a){"use strict";a.d(e,"e",(function(){return i})),a.d(e,"b",(function(){return l})),a.d(e,"a",(function(){return o})),a.d(e,"f",(function(){return s})),a.d(e,"g",(function(){return c})),a.d(e,"h",(function(){return u})),a.d(e,"i",(function(){return d})),a.d(e,"c",(function(){return h})),a.d(e,"d",(function(){return f}));var n=a("b775"),r=a("99b1");function i(t){var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},a={url:r["a"].MaterialQuantityDemandedUrl,method:t};return Object.assign(a,e),Object(n["a"])(a)}function l(t){var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},a={url:r["a"].ClassArrangelUrl,method:t};return Object.assign(a,e),Object(n["a"])(a)}function o(t){var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},a={url:r["a"].BanburyPlanUrl,method:t};return Object.assign(a,e),Object(n["a"])(a)}function s(t){var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},a={url:r["a"].MaterialRepertoryUrl,method:t};return Object.assign(a,e),Object(n["a"])(a)}function c(t){var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},a={url:r["a"].MaterialTypelUrl,method:t};return Object.assign(a,e),Object(n["a"])(a)}function u(t){var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},a={url:r["a"].RubberRepertoryUrl,method:t};return Object.assign(a,e),Object(n["a"])(a)}function d(t){var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},a={url:r["a"].StageGlobalUrl,method:t};return Object.assign(a,e),Object(n["a"])(a)}function h(t){return Object(n["a"])({url:r["a"].EquipUrl,method:"get",params:t})}function f(){return Object(n["a"])({url:r["a"].GlobalCodesUrl,method:"get",params:{all:1,class_name:"工序"}})}}}]);