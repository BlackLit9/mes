(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-f8de62ce"],{"13d5":function(t,e,a){"use strict";var r=a("23e7"),n=a("d58f").left,s=a("a640"),i=a("ae40"),l=s("reduce"),o=i("reduce",{1:0});r({target:"Array",proto:!0,forced:!l||!o},{reduce:function(t){return n(this,t,arguments.length,arguments.length>1?arguments[1]:void 0)}})},5588:function(t,e,a){},c87b:function(t,e,a){"use strict";a.r(e);var r=function(){var t=this,e=t.$createElement,a=t._self._c||e;return a("div",{directives:[{name:"loading",rawName:"v-loading",value:t.loading,expression:"loading"}]},[a("el-form",{attrs:{inline:!0}},[a("el-form-item",{attrs:{label:"时间"}},[a("el-date-picker",{attrs:{type:"daterange","range-separator":"至","start-placeholder":"开始日期","end-placeholder":"结束日期","value-format":"yyyy-MM-dd"},on:{change:t.searchDate},model:{value:t.dateValue,callback:function(e){t.dateValue=e},expression:"dateValue"}})],1),a("el-form-item",{attrs:{label:"班次"}},[a("classSelect",{on:{classSelected:t.classSelectedFun}})],1),a("el-form-item",{attrs:{label:"胶料编码"}},[a("all-product-no-select",{on:{productBatchingChanged:t.productBatchingChanged}})],1)],1),a("el-button",{directives:[{name:"permission",rawName:"v-permission",value:["unqualified_trains","add"],expression:"['unqualified_trains','add']"}],staticStyle:{float:"right","margin-bottom":"20px"},on:{click:t.generateFun}},[t._v("生成不合格处理单")]),a("el-table",{ref:"multipleTable",staticStyle:{width:"100%"},attrs:{data:t.tableData,border:"","tooltip-effect":"dark"},on:{"selection-change":t.handleSelectionChange}},[a("el-table-column",{attrs:{type:"selection",width:"55"}}),a("el-table-column",{attrs:{type:"index",width:"50",label:"No"}}),a("el-table-column",{attrs:{label:"生产日期/班次","show-overflow-tooltip":""},scopedSlots:t._u([{key:"default",fn:function(e){return[t._v(" "+t._s(e.row.date)+"/"+t._s(e.row.classes)+" ")]}}])}),a("el-table-column",{attrs:{prop:"equip_no",label:"生产机台"}}),a("el-table-column",{attrs:{prop:"product_no",label:"胶料编码"}}),a("el-table-column",{attrs:{label:"车次"},scopedSlots:t._u([{key:"default",fn:function(e){return[t._v(" "+t._s(t.setTrains(e.row.actual_trains))+" ")]}}])}),a("el-table-column",{attrs:{label:"不合格项"}},t._l(t.form_head_data,(function(e,r){return a("el-table-column",{key:r,attrs:{label:e},scopedSlots:t._u([{key:"default",fn:function(r){return[r.row.indicator_data[e]?a("div",[t.getArrMin(r.row.indicator_data[e])===t.getArrMax(r.row.indicator_data[e])?a("span",[t._v(" "+t._s(t.getArrMin(r.row.indicator_data[e]))+" ")]):a("span",[t._v(" "+t._s(t.getArrMin(r.row.indicator_data[e]))+"- "+t._s(t.getArrMax(r.row.indicator_data[e]))+" ")])]):t._e()]}}],null,!0)})})),1)],1),a("el-dialog",{attrs:{fullscreen:!0,visible:t.handleCardDialogVisible},on:{"update:visible":function(e){t.handleCardDialogVisible=e}}},[a("excel",{ref:"handleCard",attrs:{"list-data-props":t.listData,"form-head-data":t.form_head_data,show:t.handleCardDialogVisible},on:{submitFun:t.submitFun}})],1)],1)},n=[],s=(a("ac1f"),a("841c"),a("96cf"),a("1da1")),i=a("cfc4"),l=a("5dce"),o=a("f5b4"),d=a("ed08"),c=a("1f6c"),u=a("e935"),f={components:{classSelect:i["a"],allProductNoSelect:l["a"],excel:o["a"]},mixins:[u["a"]],data:function(){return{total:0,search:{},options:["已处理","未处理"],tableData:[],handleCardDialogVisible:!1,dateValue:[Object(d["d"])(),Object(d["d"])()],form_head_data:[],loading:!1,listData:[]}},created:function(){this.search.st=Object(d["d"])(),this.search.et=Object(d["d"])(),this.getList()},methods:{getList:function(){var t=this;return Object(s["a"])(regeneratorRuntime.mark((function e(){var a;return regeneratorRuntime.wrap((function(e){while(1)switch(e.prev=e.next){case 0:return e.prev=0,t.loading=!0,e.next=4,Object(c["V"])("get",null,{params:t.search});case 4:a=e.sent,t.form_head_data=a.form_head_data,t.tableData=a.ret,t.loading=!1,e.next=13;break;case 10:e.prev=10,e.t0=e["catch"](0),t.loading=!1;case 13:case"end":return e.stop()}}),e,null,[[0,10]])})))()},searchDate:function(t){this.search.st=t?t[0]:"",this.search.et=t?t[1]:"",this.getList()},classSelectedFun:function(t){this.search.classes=t,this.getList()},productBatchingChanged:function(t){this.search.product_no=t?t.material_no:"",this.getList()},handleSelectionChange:function(t){this.listData=t},currentChange:function(){},generateFun:function(){this.listData&&0!==this.listData.length&&(this.handleCardDialogVisible=!0)},submitFun:function(){this.handleCardDialogVisible=!1,this.getList()}}},p=f,_=a("2877"),m=Object(_["a"])(p,r,n,!1,null,null,null);e["default"]=m.exports},cf05:function(t,e,a){t.exports=a.p+"static/img/logo.9485082b.png"},d58f:function(t,e,a){var r=a("1c0b"),n=a("7b0b"),s=a("44ad"),i=a("50c4"),l=function(t){return function(e,a,l,o){r(a);var d=n(e),c=s(d),u=i(d.length),f=t?u-1:0,p=t?-1:1;if(l<2)while(1){if(f in c){o=c[f],f+=p;break}if(f+=p,t?f<0:u<=f)throw TypeError("Reduce of empty array with no initial value")}for(;t?f>=0:u>f;f+=p)f in c&&(o=a(o,c[f],f,d));return o}};t.exports={left:l(!1),right:l(!0)}},daa1:function(t,e,a){"use strict";a.d(e,"e",(function(){return s})),a.d(e,"b",(function(){return i})),a.d(e,"a",(function(){return l})),a.d(e,"f",(function(){return o})),a.d(e,"g",(function(){return d})),a.d(e,"h",(function(){return c})),a.d(e,"i",(function(){return u})),a.d(e,"c",(function(){return f})),a.d(e,"d",(function(){return p}));var r=a("b775"),n=a("99b1");function s(t){var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},a={url:n["a"].MaterialQuantityDemandedUrl,method:t};return Object.assign(a,e),Object(r["a"])(a)}function i(t){var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},a={url:n["a"].ClassArrangelUrl,method:t};return Object.assign(a,e),Object(r["a"])(a)}function l(t){var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},a={url:n["a"].BanburyPlanUrl,method:t};return Object.assign(a,e),Object(r["a"])(a)}function o(t){var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},a={url:n["a"].MaterialRepertoryUrl,method:t};return Object.assign(a,e),Object(r["a"])(a)}function d(t){var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},a={url:n["a"].MaterialTypelUrl,method:t};return Object.assign(a,e),Object(r["a"])(a)}function c(t){var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},a={url:n["a"].RubberRepertoryUrl,method:t};return Object.assign(a,e),Object(r["a"])(a)}function u(t){var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},a={url:n["a"].StageGlobalUrl,method:t};return Object.assign(a,e),Object(r["a"])(a)}function f(t){return Object(r["a"])({url:n["a"].EquipUrl,method:"get",params:t})}function p(){return Object(r["a"])({url:n["a"].GlobalCodesUrl,method:"get",params:{all:1,class_name:"工序"}})}},e6be:function(t,e,a){"use strict";var r=a("5588"),n=a.n(r);n.a},e935:function(t,e,a){"use strict";a("4160"),a("d3b7"),a("6062"),a("3ca3"),a("ddb0");var r=a("2909");e["a"]={methods:{setTrains:function(t){var e=this;if(t&&0!==t.length){var a=Object(r["a"])(new Set(JSON.parse(JSON.stringify(t))));a.sort((function(t,e){return t-e}));for(var n=[],s=[],i=0;i<a.length;i++)if(a[i+1]&&a[i]+1===a[i+1])s.push(a[i]),s.push(a[i+1]);else{if(s.push(a[i]),!s||0===s.length)return;n.push(s),s=[]}var l="",o=0;return n.forEach((function(t,a){if(e.getArrMin(t)===e.getArrMax(t))return o++,void(l+=(o>1?",":"")+e.getArrMin(t));o++,l+=(o>1?",":"")+e.getArrMin(t)+"-"+e.getArrMax(t)})),l}},getArrMax:function(t){return Math.max.apply(null,t)},getArrMin:function(t){return Math.min.apply(null,t)}}}},f5b4:function(t,e,a){"use strict";var r=function(){var t=this,e=t.$createElement,a=t._self._c||e;return a("div",{staticClass:"card-container"},[a("div",{ref:"PDFBtn",staticStyle:{"text-align":"right","margin-bottom":"10px"}},[t.orderNum&&!t.editType?a("el-button",{directives:[{name:"permission",rawName:"v-permission",value:["unqualified_order","export"],expression:"['unqualified_order','export']"}],on:{click:t.exportExcel}},[t._v("另存为PDF")]):a("el-button",{attrs:{loading:t.loadingBtn},on:{click:t.submitFun}},[t._v("保存")])],1),a("div",{attrs:{id:"out-table"}},[a("table",{staticClass:"info-table",attrs:{border:"1",bordercolor:"black"}},[a("thead",[a("tr",[a("th",{attrs:{colspan:4}},[t._m(0)])]),t.orderNum?a("tr",[a("td",{staticStyle:{"text-align":"right","padding-right":"15px"},attrs:{colspan:4}},[a("div",[t._v("质检编码："+t._s(t.formObj.unqualified_deal_order_uid))])])]):t._e()]),a("tbody",[a("tr",[a("td",{staticStyle:{"text-align":"left","padding-left":"25px",width:"108px"}},[t._v("发生部门： ")]),a("td",[t.orderNum?a("span",[t._v(t._s(t.formObj.deal_department))]):a("div",{staticClass:"deal_department"},[a("el-radio",{attrs:{label:"分厂"},model:{value:t.formObj.deal_department,callback:function(e){t.$set(t.formObj,"deal_department",e)},expression:"formObj.deal_department"}},[t._v("分厂")]),a("el-radio",{attrs:{label:"车间"},model:{value:t.formObj.deal_department,callback:function(e){t.$set(t.formObj,"deal_department",e)},expression:"formObj.deal_department"}},[t._v("车间")])],1)]),a("td",{staticStyle:{width:"300px"}},[t._v("胶料筹备组 炼胶")]),a("td",{staticStyle:{width:"125px"}},[t._v("日期："+t._s(t.orderNum&&t.formObj.created_date?t.formObj.created_date.split(" ")[0]:t.formObj.currentDate))])]),a("tr",{staticStyle:{"text-align":"left"}},[a("td",{staticStyle:{"padding-left":"25px"},attrs:{colspan:"4"}},[t._v("不合格品状态： "),t.orderNum?a("span",t._l(t.stateList,(function(e,r){return a("span",{key:r},[e===t.formObj.status?a("span",[t._v("☑")]):a("span",[t._v("☐")]),t._v(" "+t._s(e)+" ")])})),0):a("span",t._l(t.stateList,(function(e,r){return a("el-radio",{key:r,attrs:{label:e},model:{value:t.formObj.status,callback:function(e){t.$set(t.formObj,"status",e)},expression:"formObj.status"}},[t._v(" "+t._s(e)+" ")])})),1)])]),a("tr",{staticStyle:{"text-align":"left"}},[a("td",{staticStyle:{"padding-left":"25px"},attrs:{colspan:"4"}},[a("span",[t._v("不合格品信息(发生部门)：")]),t.orderNum?a("span",{domProps:{innerHTML:t._s(t.formObj.department)}}):a("el-input",{staticStyle:{width:"70%"},attrs:{placeholder:"请输入内容"},model:{value:t.formObj.department,callback:function(e){t.$set(t.formObj,"department",e)},expression:"formObj.department"}})],1)])])]),a("table",{staticClass:"info-table",staticStyle:{"border-top-color":"#fff"},attrs:{border:"1",bordercolor:"black"}},[a("tr",[a("th",{attrs:{rowspan:"2"}},[t._v("序号")]),a("th",{attrs:{rowspan:"2"}},[t._v("生产日期/班次")]),a("th",{attrs:{rowspan:"2"}},[t._v("生产机台")]),a("th",{attrs:{rowspan:"2"}},[t._v("胶料编码")]),a("th",{attrs:{rowspan:"2"}},[t._v("车次")]),a("th",{attrs:{colspan:t.headData.length}},[t._v("不合格项")])]),a("tr",t._l(t.headData,(function(e,r){return a("th",{key:r},[t._v(t._s(e))])})),0),t._l(t.listData,(function(e,r){return a("tr",{key:r},[a("td",[t._v(t._s(Number(r)+1))]),a("td",[t._v(t._s(e.date)+"/"+t._s(e.classes))]),a("td",[t._v(t._s(e.equip_no))]),a("td",[t._v(t._s(e.product_no))]),a("td",[t._v(t._s(t.setTrains(e.actual_trains)))]),t._l(t.headData,(function(r,n){return a("td",{key:n},[e.indicator_data[r]?a("div",[t.getArrMin(e.indicator_data[r])===t.getArrMax(e.indicator_data[r])?a("span",[t._v(" "+t._s(t.getArrMin(e.indicator_data[r]))+" ")]):a("span",[t._v(" "+t._s(t.getArrMin(e.indicator_data[r]))+"- "+t._s(t.getArrMax(e.indicator_data[r]))+" ")])]):t._e()])}))],2)})),a("tr",{staticStyle:{"text-align":"right"}},[a("td",{attrs:{colspan:5+(t.headData.length||1)}},[t._v(" 经办人： "+t._s(t.orderNum?t.formObj.created_username:t.name)+" "),a("span",{staticStyle:{margin:"0 100px"}},[t._v("日期："+t._s(t.orderNum&&t.formObj.created_date?t.formObj.created_date.split(" ")[0]:t.formObj.currentDate))])])]),a("tr",{staticStyle:{"text-align":"left"}},[a("td",{staticStyle:{"padding-left":"25px"},attrs:{colspan:5+(t.headData.length||1)}},[a("div",[t._v("不合格品情况(包括产品生产过程、原因及程度)：")]),t.orderNum&&1!==t.editType?a("div",{staticClass:"deal_suggestion",domProps:{innerHTML:t._s(t.formObj.reason)}}):a("el-input",{staticStyle:{"margin-top":"10px",width:"97%"},attrs:{type:"textarea",rows:5,resize:"none",placeholder:"请输入内容"},on:{change:function(e){return t.editOne(e,"deal_user","deal_date")}},model:{value:t.formObj.reason,callback:function(e){t.$set(t.formObj,"reason",e)},expression:"formObj.reason"}})],1)]),a("tr",{staticStyle:{"text-align":"right"}},[a("td",{attrs:{colspan:5+(t.headData.length||1)}},[t._v(" 经办人："+t._s(t.formObj.deal_user)+" "),a("span",{staticStyle:{margin:"0 100px"}},[t._v("日期："+t._s(t.formObj.deal_date))])])]),a("tr",{staticStyle:{"text-align":"left"}},[a("td",{staticStyle:{"padding-left":"25px"},attrs:{colspan:5+(t.headData.length||1)}},[a("div",[t._v("处理意见(品质技术部工艺技术科)：")]),t.orderNum&&2!==t.editType?a("div",{staticClass:"deal_suggestion",domProps:{innerHTML:t._s(t.formObj.t_deal_suggestion)}}):a("el-input",{staticStyle:{"margin-top":"10px",width:"97%"},attrs:{type:"textarea",rows:5,resize:"none",placeholder:"请输入内容"},on:{change:function(e){return t.editOne(e,"t_deal_user","t_deal_date")}},model:{value:t.formObj.t_deal_suggestion,callback:function(e){t.$set(t.formObj,"t_deal_suggestion",e)},expression:"formObj.t_deal_suggestion"}})],1)]),a("tr",{staticStyle:{"text-align":"right"}},[a("td",{attrs:{colspan:5+(t.headData.length||1)}},[t._v(" 经办人："+t._s(t.formObj.t_deal_user)+" "),a("span",{staticStyle:{margin:"0 100px"}},[t._v("日期："+t._s(t.formObj.t_deal_date))])])]),a("tr",{staticStyle:{"text-align":"left"}},[a("td",{staticStyle:{"padding-left":"25px"},attrs:{colspan:5+(t.headData.length||1)}},[a("div",[t._v("处理意见(品质技术部工艺检查科)：")]),t.orderNum&&3!==t.editType?a("div",{staticClass:"deal_suggestion",domProps:{innerHTML:t._s(t.formObj.c_deal_suggestion)}}):a("el-input",{staticStyle:{"margin-top":"10px",width:"97%"},attrs:{type:"textarea",rows:5,resize:"none",placeholder:"请输入内容"},on:{change:function(e){return t.editOne(e,"c_deal_user","c_deal_date")}},model:{value:t.formObj.c_deal_suggestion,callback:function(e){t.$set(t.formObj,"c_deal_suggestion",e)},expression:"formObj.c_deal_suggestion"}})],1)]),a("tr",{staticStyle:{"text-align":"right"}},[a("td",{attrs:{colspan:5+(t.headData.length||1)}},[t._v(" 经办人："+t._s(t.formObj.c_deal_user)+" "),a("span",{staticStyle:{margin:"0 100px"}},[t._v("日期："+t._s(t.formObj.c_deal_date))])])]),a("tr",{staticStyle:{"text-align":"left"}},[a("td",{staticStyle:{"padding-left":"25px"},attrs:{colspan:5+(t.headData.length||1)}},[a("div",[t._v("备注：")]),t.orderNum?a("div",{staticClass:"deal_suggestion",domProps:{innerHTML:t._s(t.formObj.desc)}}):a("el-input",{staticStyle:{"margin-top":"10px",width:"97%"},attrs:{type:"textarea",rows:5,resize:"none",placeholder:"请输入内容"},model:{value:t.formObj.desc,callback:function(e){t.$set(t.formObj,"desc",e)},expression:"formObj.desc"}}),a("div",{staticStyle:{"margin-top":"10px"}})],1)])],2)])])},n=[function(){var t=this,e=t.$createElement,r=t._self._c||e;return r("div",{staticStyle:{position:"relative"}},[r("div",{staticClass:"logo-style"},[r("img",{staticStyle:{width:"100%",height:"100%"},attrs:{src:a("cf05"),alt:""}})]),r("div",{staticStyle:{flex:"1","text-align":"center","font-size":"1.5em","line-height":"45px"}},[t._v("中策(安吉)不合格品处置单")])])}],s=(a("99af"),a("4160"),a("b0c0"),a("a9e3"),a("ac1f"),a("5319"),a("159b"),a("96cf"),a("1da1")),i=a("5530"),l=a("1f6c"),o=a("ed08"),d=a("2f62"),c=a("e935"),u={mixins:[c["a"]],props:{orderRow:{type:Object,default:function(){return{}}},listDataProps:{type:Array,default:function(){return[]}},formHeadData:{type:Array,default:function(){return[]}},show:{type:Boolean,default:function(){return!1}},editType:{type:Number,default:function(){return null}}},data:function(){return{formObj:{status:"来料",currentDate:Object(o["d"])()},stateList:["来料","半成品","成品","库存"],headData:this.formHeadData,orderNum:null,loadingBtn:!1,listData:this.listDataProps,aaa:""}},computed:Object(i["a"])({},Object(d["b"])(["name"])),watch:{show:function(t){t&&(this.orderNum=this.orderRow.id||null,this.listData=this.listDataProps||[],this.orderNum&&this.getInfo())}},created:function(){this.orderNum=this.orderRow.id||null,this.orderNum&&this.getInfo()},methods:{getInfo:function(){var t=this;return Object(s["a"])(regeneratorRuntime.mark((function e(){var a;return regeneratorRuntime.wrap((function(e){while(1)switch(e.prev=e.next){case 0:return e.prev=0,e.next=3,Object(l["U"])("get",t.orderNum);case 3:a=e.sent,t.formObj=a,t.formObj.reason=1===t.editType?t.changeInputBack(t.formObj.reason):t.formObj.reason,t.formObj.t_deal_suggestion=2===t.editType?t.changeInputBack(t.formObj.t_deal_suggestion):t.formObj.t_deal_suggestion,t.formObj.c_deal_suggestion=3===t.editType?t.changeInputBack(t.formObj.c_deal_suggestion):t.formObj.c_deal_suggestion,t.headData=a.form_head_data,t.listData=a.deal_details,e.next=14;break;case 12:e.prev=12,e.t0=e["catch"](0);case 14:case"end":return e.stop()}}),e,null,[[0,12]])})))()},submitFun:function(){var t=this;return Object(s["a"])(regeneratorRuntime.mark((function e(){var a,r,n,s;return regeneratorRuntime.wrap((function(e){while(1)switch(e.prev=e.next){case 0:return e.prev=0,a={},r="",n=null,t.orderNum?(n=t.formObj.id,a={t_deal_suggestion:t.formObj.t_deal_suggestion,c_deal_suggestion:t.formObj.c_deal_suggestion,reason:t.formObj.reason,deal_user:t.formObj.deal_user,deal_date:t.formObj.deal_date,t_deal_user:t.formObj.t_deal_user,t_deal_date:t.formObj.t_deal_date,c_deal_user:t.formObj.c_deal_user,c_deal_date:t.formObj.c_deal_date},r="put"):(a=JSON.parse(JSON.stringify(t.formObj)),s=[],t.listData.forEach((function(t){s=s.concat(t.order_ids)})),t.$set(a,"order_ids",s),r="post",n=null,a.desc=t.changeInput(a.desc)),a.reason=t.changeInput(a.reason),a.t_deal_suggestion=t.changeInput(a.t_deal_suggestion),a.c_deal_suggestion=t.changeInput(a.c_deal_suggestion),t.loadingBtn=!0,e.next=11,Object(l["U"])(r,n,{data:a});case 11:t.$message({message:t.orderNum?"创建成功":"可在不合格处置单管理内查看，创建成功",type:"success",duration:5e3}),t.$emit("submitFun",a),t.formObj={status:"来料",currentDate:Object(o["d"])()},t.loadingBtn=!1,e.next=20;break;case 17:e.prev=17,e.t0=e["catch"](0),t.loadingBtn=!1;case 20:case"end":return e.stop()}}),e,null,[[0,17]])})))()},changeInput:function(t){return t?t.replace(/\r\n/g,"<br>").replace(/\n/g,"<br>").replace(/\s/g,"&nbsp;"):null},changeInputBack:function(t){return t?t.replace(/<br>/g,"\r\n").replace(/<br>/g,"\n").replace(/&nbsp;/g,"s"):""},editOne:function(t,e,a){this.$set(this.formObj,e,this.name),this.$set(this.formObj,a,Object(o["d"])())},editTwo:function(){this.formObj.name=this.name,this.formObj.currentDate=Object(o["d"])()},editThree:function(){this.formObj.name=this.name,this.formObj.currentDate=Object(o["d"])()},exportExcel:function(){var t=this;return Object(s["a"])(regeneratorRuntime.mark((function e(){return regeneratorRuntime.wrap((function(e){while(1)switch(e.prev=e.next){case 0:t.$refs.PDFBtn.style.display="none",document.getElementsByClassName("el-dialog__headerbtn")[0].style.display="none",window.print(),t.$refs.PDFBtn.style.display="block",document.getElementsByClassName("el-dialog__headerbtn")[0].style.display="block";case 5:case"end":return e.stop()}}),e)})))()}}},f=u,p=(a("e6be"),a("2877")),_=Object(p["a"])(f,r,n,!1,null,null,null);e["a"]=_.exports}}]);