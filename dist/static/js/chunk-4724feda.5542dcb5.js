(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-4724feda"],{5588:function(e,t,a){},bc9f:function(e,t,a){"use strict";a.r(t);var r=function(){var e=this,t=e.$createElement,a=e._self._c||t;return a("div",[a("el-form",{attrs:{inline:!0}},[a("el-form-item",{attrs:{label:"时间"}},[a("el-date-picker",{attrs:{type:"daterange","range-separator":"至","start-placeholder":"开始日期","end-placeholder":"结束日期","value-format":"yyyy-MM-dd"},on:{change:e.searchDate},model:{value:e.dateValue,callback:function(t){e.dateValue=t},expression:"dateValue"}})],1),a("el-form-item",{attrs:{label:"原因编辑"}},[a("el-select",{attrs:{clearable:"",placeholder:"请选择"},on:{change:e.reasonChange},model:{value:e.search.reason,callback:function(t){e.$set(e.search,"reason",t)},expression:"search.reason"}},e._l(e.options,(function(e){return a("el-option",{key:e.name,attrs:{label:e.name,value:e.bool}})})),1)],1),a("el-form-item",{attrs:{label:"技术处理"}},[a("el-select",{attrs:{clearable:"",placeholder:"请选择"},on:{change:e.reasonChange},model:{value:e.search.t_deal_suggestion,callback:function(t){e.$set(e.search,"t_deal_suggestion",t)},expression:"search.t_deal_suggestion"}},e._l(e.options,(function(e){return a("el-option",{key:e.name,attrs:{label:e.name,value:e.bool}})})),1)],1),a("el-form-item",{attrs:{label:"检查处理"}},[a("el-select",{attrs:{clearable:"",placeholder:"请选择"},on:{change:e.reasonChange},model:{value:e.search.c_deal_suggestion,callback:function(t){e.$set(e.search,"c_deal_suggestion",t)},expression:"search.c_deal_suggestion"}},e._l(e.options,(function(e){return a("el-option",{key:e.name,attrs:{label:e.name,value:e.bool}})})),1)],1)],1),a("el-table",{staticStyle:{width:"100%"},attrs:{data:e.tableData,border:"","tooltip-effect":"dark"}},[a("el-table-column",{attrs:{type:"index",width:"50",label:"No"}}),a("el-table-column",{attrs:{label:"处置单号","show-overflow-tooltip":""},scopedSlots:e._u([{key:"default",fn:function(t){return[a("el-link",{attrs:{type:"primary"},on:{click:function(a){return e.clickOrderNum(t.$index,t.row)}}},[e._v(e._s(t.row.unqualified_deal_order_uid))])]}}])}),a("el-table-column",{attrs:{prop:"created_date",label:"创建时间"},scopedSlots:e._u([{key:"default",fn:function(t){var a=t.row;return[e._v(" "+e._s(a.created_date.split(" ")[0])+" ")]}}])}),a("el-table-column",{attrs:{prop:"department",label:"发生部门"}}),a("el-table-column",{attrs:{prop:"reason",label:"不合格原因","show-overflow-tooltip":""},scopedSlots:e._u([{key:"default",fn:function(t){var a=t.row;return[e._v(" "+e._s(e.changeInputBack(a.reason))+" ")]}}])}),a("el-table-column",{attrs:{prop:"t_deal_suggestion",label:"技术不合格原因","show-overflow-tooltip":""},scopedSlots:e._u([{key:"default",fn:function(t){var a=t.row;return[e._v(" "+e._s(e.changeInputBack(a.t_deal_suggestion))+" ")]}}])}),a("el-table-column",{attrs:{prop:"c_deal_suggestion",label:"检查不合格原因","show-overflow-tooltip":""},scopedSlots:e._u([{key:"default",fn:function(t){var a=t.row;return[e._v(" "+e._s(e.changeInputBack(a.c_deal_suggestion))+" ")]}}])}),a("el-table-column",{attrs:{label:"原因编辑"},scopedSlots:e._u([{key:"default",fn:function(t){return[a("el-button",{directives:[{name:"permission",rawName:"v-permission",value:["unqualified_order","reason"],expression:"['unqualified_order','reason']"}],attrs:{size:"small"},on:{click:function(a){return e.editReason(t.$index,t.row,1)}}},[e._v("编辑")])]}}])}),a("el-table-column",{attrs:{label:"技术处理"},scopedSlots:e._u([{key:"default",fn:function(t){return[a("el-button",{directives:[{name:"permission",rawName:"v-permission",value:["unqualified_order","tech"],expression:"['unqualified_order','tech']"}],attrs:{size:"small"},on:{click:function(a){return e.editReason(t.$index,t.row,2)}}},[e._v("编辑")])]}}])}),a("el-table-column",{attrs:{label:"检查处理"},scopedSlots:e._u([{key:"default",fn:function(t){return[a("el-button",{directives:[{name:"permission",rawName:"v-permission",value:["unqualified_order","check"],expression:"['unqualified_order','check']"}],attrs:{size:"small"},on:{click:function(a){return e.editReason(t.$index,t.row,3)}}},[e._v("编辑")])]}}])}),a("el-table-column",{attrs:{prop:"deal_user",label:"原因编辑人"}}),a("el-table-column",{attrs:{prop:"t_deal_user",label:"技术处理人"}}),a("el-table-column",{attrs:{prop:"c_deal_user",label:"检查处理人"}}),a("el-table-column",{attrs:{prop:"deal_date",label:"原因编辑时间"}}),a("el-table-column",{attrs:{prop:"t_deal_date",label:"技术处理时间"}}),a("el-table-column",{attrs:{prop:"c_deal_date",label:"检查处理时间"}})],1),a("page",{attrs:{total:e.total,"current-page":e.search.page},on:{currentChange:e.currentChange}}),a("el-dialog",{attrs:{fullscreen:!0,visible:e.handleCardDialogVisible},on:{"update:visible":function(t){e.handleCardDialogVisible=t}}},[a("excel",{ref:"handleCard",attrs:{"order-row":e.currentRow,"edit-type":e.editType,show:e.handleCardDialogVisible},on:{submitFun:e.submitFun}})],1)],1)},n=[],s=(a("ac1f"),a("5319"),a("841c"),a("96cf"),a("1da1")),l=a("3e51"),o=a("f5b4"),i=a("1f6c"),c=a("ed08"),d={components:{excel:o["a"],page:l["a"]},data:function(){return{tableData:[],search:{value:[],page:1},total:0,options:[{name:"已处理",bool:!1},{name:"未处理",bool:!0}],handleCardDialogVisible:!1,currentRow:{},editType:null,dateValue:[Object(c["d"])(),Object(c["d"])()]}},created:function(){this.search.st=Object(c["d"])(),this.search.et=Object(c["d"])(),this.getList()},methods:{getList:function(){var e=this;return Object(s["a"])(regeneratorRuntime.mark((function t(){var a;return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:return t.prev=0,t.next=3,Object(i["U"])("get",null,{params:e.search});case 3:a=t.sent,e.tableData=a.results,e.total=a.count,t.next=10;break;case 8:t.prev=8,t.t0=t["catch"](0);case 10:case"end":return t.stop()}}),t,null,[[0,8]])})))()},changeInputBack:function(e){return e?e.replace(/<br>/g,"\r\n").replace(/<br>/g,"\n").replace(/&nbsp;/g,"s"):""},editReason:function(e,t,a){this.handleCardDialogVisible=!0,this.currentRow=t,this.editType=a},clickOrderNum:function(e,t){this.handleCardDialogVisible=!0,this.currentRow=t,this.editType=null},currentChange:function(e){this.search.page=e,this.getList()},searchDate:function(e){this.search.st=e?e[0]:"",this.search.et=e?e[1]:"",this.search.page=1,this.getList()},submitFun:function(){this.handleCardDialogVisible=!1,this.getList()},reasonChange:function(){this.search.page=1,this.getList()}}},u=d,p=a("2877"),_=Object(p["a"])(u,r,n,!1,null,null,null);t["default"]=_.exports},cf05:function(e,t,a){e.exports=a.p+"static/img/logo.9485082b.png"},e6be:function(e,t,a){"use strict";var r=a("5588"),n=a.n(r);n.a},e935:function(e,t,a){"use strict";a("4160"),a("d3b7"),a("6062"),a("3ca3"),a("ddb0");var r=a("2909");t["a"]={methods:{setTrains:function(e){var t=this;if(e&&0!==e.length){var a=Object(r["a"])(new Set(JSON.parse(JSON.stringify(e))));a.sort((function(e,t){return e-t}));for(var n=[],s=[],l=0;l<a.length;l++)if(a[l+1]&&a[l]+1===a[l+1])s.push(a[l]),s.push(a[l+1]);else{if(s.push(a[l]),!s||0===s.length)return;n.push(s),s=[]}var o="",i=0;return n.forEach((function(e,a){if(t.getArrMin(e)===t.getArrMax(e))return i++,void(o+=(i>1?",":"")+t.getArrMin(e));i++,o+=(i>1?",":"")+t.getArrMin(e)+"-"+t.getArrMax(e)})),o}},getArrMax:function(e){return Math.max.apply(null,e)},getArrMin:function(e){return Math.min.apply(null,e)}}}},f5b4:function(e,t,a){"use strict";var r=function(){var e=this,t=e.$createElement,a=e._self._c||t;return a("div",{staticClass:"card-container"},[a("div",{ref:"PDFBtn",staticStyle:{"text-align":"right","margin-bottom":"10px"}},[e.orderNum&&!e.editType?a("el-button",{directives:[{name:"permission",rawName:"v-permission",value:["unqualified_order","export"],expression:"['unqualified_order','export']"}],on:{click:e.exportExcel}},[e._v("另存为PDF")]):a("el-button",{attrs:{loading:e.loadingBtn},on:{click:e.submitFun}},[e._v("保存")])],1),a("div",{attrs:{id:"out-table"}},[a("table",{staticClass:"info-table",attrs:{border:"1",bordercolor:"black"}},[a("thead",[a("tr",[a("th",{attrs:{colspan:4}},[e._m(0)])]),e.orderNum?a("tr",[a("td",{staticStyle:{"text-align":"right","padding-right":"15px"},attrs:{colspan:4}},[a("div",[e._v("质检编码："+e._s(e.formObj.unqualified_deal_order_uid))])])]):e._e()]),a("tbody",[a("tr",[a("td",{staticStyle:{"text-align":"left","padding-left":"25px",width:"108px"}},[e._v("发生部门： ")]),a("td",[e.orderNum?a("span",[e._v(e._s(e.formObj.deal_department))]):a("div",{staticClass:"deal_department"},[a("el-radio",{attrs:{label:"分厂"},model:{value:e.formObj.deal_department,callback:function(t){e.$set(e.formObj,"deal_department",t)},expression:"formObj.deal_department"}},[e._v("分厂")]),a("el-radio",{attrs:{label:"车间"},model:{value:e.formObj.deal_department,callback:function(t){e.$set(e.formObj,"deal_department",t)},expression:"formObj.deal_department"}},[e._v("车间")])],1)]),a("td",{staticStyle:{width:"300px"}},[e._v("胶料筹备组 炼胶")]),a("td",{staticStyle:{width:"125px"}},[e._v("日期："+e._s(e.orderNum&&e.formObj.created_date?e.formObj.created_date.split(" ")[0]:e.formObj.currentDate))])]),a("tr",{staticStyle:{"text-align":"left"}},[a("td",{staticStyle:{"padding-left":"25px"},attrs:{colspan:"4"}},[e._v("不合格品状态： "),e.orderNum?a("span",e._l(e.stateList,(function(t,r){return a("span",{key:r},[t===e.formObj.status?a("span",[e._v("☑")]):a("span",[e._v("☐")]),e._v(" "+e._s(t)+" ")])})),0):a("span",e._l(e.stateList,(function(t,r){return a("el-radio",{key:r,attrs:{label:t},model:{value:e.formObj.status,callback:function(t){e.$set(e.formObj,"status",t)},expression:"formObj.status"}},[e._v(" "+e._s(t)+" ")])})),1)])]),a("tr",{staticStyle:{"text-align":"left"}},[a("td",{staticStyle:{"padding-left":"25px"},attrs:{colspan:"4"}},[a("span",[e._v("不合格品信息(发生部门)：")]),e.orderNum?a("span",{domProps:{innerHTML:e._s(e.formObj.department)}}):a("el-input",{staticStyle:{width:"70%"},attrs:{placeholder:"请输入内容"},model:{value:e.formObj.department,callback:function(t){e.$set(e.formObj,"department",t)},expression:"formObj.department"}})],1)])])]),a("table",{staticClass:"info-table",staticStyle:{"border-top-color":"#fff"},attrs:{border:"1",bordercolor:"black"}},[a("tr",[a("th",{attrs:{rowspan:"2"}},[e._v("序号")]),a("th",{attrs:{rowspan:"2"}},[e._v("生产日期/班次")]),a("th",{attrs:{rowspan:"2"}},[e._v("生产机台")]),a("th",{attrs:{rowspan:"2"}},[e._v("胶料编码")]),a("th",{attrs:{rowspan:"2"}},[e._v("车次")]),a("th",{attrs:{colspan:e.headData.length}},[e._v("不合格项")])]),a("tr",e._l(e.headData,(function(t,r){return a("th",{key:r},[e._v(e._s(t))])})),0),e._l(e.listData,(function(t,r){return a("tr",{key:r},[a("td",[e._v(e._s(Number(r)+1))]),a("td",[e._v(e._s(t.date)+"/"+e._s(t.classes))]),a("td",[e._v(e._s(t.equip_no))]),a("td",[e._v(e._s(t.product_no))]),a("td",[e._v(e._s(e.setTrains(t.actual_trains)))]),e._l(e.headData,(function(r,n){return a("td",{key:n},[t.indicator_data[r]?a("div",[e.getArrMin(t.indicator_data[r])===e.getArrMax(t.indicator_data[r])?a("span",[e._v(" "+e._s(e.getArrMin(t.indicator_data[r]))+" ")]):a("span",[e._v(" "+e._s(e.getArrMin(t.indicator_data[r]))+"- "+e._s(e.getArrMax(t.indicator_data[r]))+" ")])]):e._e()])}))],2)})),a("tr",{staticStyle:{"text-align":"right"}},[a("td",{attrs:{colspan:5+(e.headData.length||1)}},[e._v(" 经办人： "+e._s(e.orderNum?e.formObj.created_username:e.name)+" "),a("span",{staticStyle:{margin:"0 100px"}},[e._v("日期："+e._s(e.orderNum&&e.formObj.created_date?e.formObj.created_date.split(" ")[0]:e.formObj.currentDate))])])]),a("tr",{staticStyle:{"text-align":"left"}},[a("td",{staticStyle:{"padding-left":"25px"},attrs:{colspan:5+(e.headData.length||1)}},[a("div",[e._v("不合格品情况(包括产品生产过程、原因及程度)：")]),e.orderNum&&1!==e.editType?a("div",{staticClass:"deal_suggestion",domProps:{innerHTML:e._s(e.formObj.reason)}}):a("el-input",{staticStyle:{"margin-top":"10px",width:"97%"},attrs:{type:"textarea",rows:5,resize:"none",placeholder:"请输入内容"},on:{change:function(t){return e.editOne(t,"deal_user","deal_date")}},model:{value:e.formObj.reason,callback:function(t){e.$set(e.formObj,"reason",t)},expression:"formObj.reason"}})],1)]),a("tr",{staticStyle:{"text-align":"right"}},[a("td",{attrs:{colspan:5+(e.headData.length||1)}},[e._v(" 经办人："+e._s(e.formObj.deal_user)+" "),a("span",{staticStyle:{margin:"0 100px"}},[e._v("日期："+e._s(e.formObj.deal_date))])])]),a("tr",{staticStyle:{"text-align":"left"}},[a("td",{staticStyle:{"padding-left":"25px"},attrs:{colspan:5+(e.headData.length||1)}},[a("div",[e._v("处理意见(品质技术部工艺技术科)：")]),e.orderNum&&2!==e.editType?a("div",{staticClass:"deal_suggestion",domProps:{innerHTML:e._s(e.formObj.t_deal_suggestion)}}):a("el-input",{staticStyle:{"margin-top":"10px",width:"97%"},attrs:{type:"textarea",rows:5,resize:"none",placeholder:"请输入内容"},on:{change:function(t){return e.editOne(t,"t_deal_user","t_deal_date")}},model:{value:e.formObj.t_deal_suggestion,callback:function(t){e.$set(e.formObj,"t_deal_suggestion",t)},expression:"formObj.t_deal_suggestion"}})],1)]),a("tr",{staticStyle:{"text-align":"right"}},[a("td",{attrs:{colspan:5+(e.headData.length||1)}},[e._v(" 经办人："+e._s(e.formObj.t_deal_user)+" "),a("span",{staticStyle:{margin:"0 100px"}},[e._v("日期："+e._s(e.formObj.t_deal_date))])])]),a("tr",{staticStyle:{"text-align":"left"}},[a("td",{staticStyle:{"padding-left":"25px"},attrs:{colspan:5+(e.headData.length||1)}},[a("div",[e._v("处理意见(品质技术部工艺检查科)：")]),e.orderNum&&3!==e.editType?a("div",{staticClass:"deal_suggestion",domProps:{innerHTML:e._s(e.formObj.c_deal_suggestion)}}):a("el-input",{staticStyle:{"margin-top":"10px",width:"97%"},attrs:{type:"textarea",rows:5,resize:"none",placeholder:"请输入内容"},on:{change:function(t){return e.editOne(t,"c_deal_user","c_deal_date")}},model:{value:e.formObj.c_deal_suggestion,callback:function(t){e.$set(e.formObj,"c_deal_suggestion",t)},expression:"formObj.c_deal_suggestion"}})],1)]),a("tr",{staticStyle:{"text-align":"right"}},[a("td",{attrs:{colspan:5+(e.headData.length||1)}},[e._v(" 经办人："+e._s(e.formObj.c_deal_user)+" "),a("span",{staticStyle:{margin:"0 100px"}},[e._v("日期："+e._s(e.formObj.c_deal_date))])])]),a("tr",{staticStyle:{"text-align":"left"}},[a("td",{staticStyle:{"padding-left":"25px"},attrs:{colspan:5+(e.headData.length||1)}},[a("div",[e._v("备注：")]),e.orderNum?a("div",{staticClass:"deal_suggestion",domProps:{innerHTML:e._s(e.formObj.desc)}}):a("el-input",{staticStyle:{"margin-top":"10px",width:"97%"},attrs:{type:"textarea",rows:5,resize:"none",placeholder:"请输入内容"},model:{value:e.formObj.desc,callback:function(t){e.$set(e.formObj,"desc",t)},expression:"formObj.desc"}}),a("div",{staticStyle:{"margin-top":"10px"}})],1)])],2)])])},n=[function(){var e=this,t=e.$createElement,r=e._self._c||t;return r("div",{staticStyle:{position:"relative"}},[r("div",{staticClass:"logo-style"},[r("img",{staticStyle:{width:"100%",height:"100%"},attrs:{src:a("cf05"),alt:""}})]),r("div",{staticStyle:{flex:"1","text-align":"center","font-size":"1.5em","line-height":"45px"}},[e._v("中策(安吉)不合格品处置单")])])}],s=(a("99af"),a("4160"),a("b0c0"),a("a9e3"),a("ac1f"),a("5319"),a("159b"),a("96cf"),a("1da1")),l=a("5530"),o=a("1f6c"),i=a("ed08"),c=a("2f62"),d=a("e935"),u={mixins:[d["a"]],props:{orderRow:{type:Object,default:function(){return{}}},listDataProps:{type:Array,default:function(){return[]}},formHeadData:{type:Array,default:function(){return[]}},show:{type:Boolean,default:function(){return!1}},editType:{type:Number,default:function(){return null}}},data:function(){return{formObj:{status:"来料",currentDate:Object(i["d"])()},stateList:["来料","半成品","成品","库存"],headData:this.formHeadData,orderNum:null,loadingBtn:!1,listData:this.listDataProps,aaa:""}},computed:Object(l["a"])({},Object(c["b"])(["name"])),watch:{show:function(e){e&&(this.orderNum=this.orderRow.id||null,this.listData=this.listDataProps||[],this.orderNum&&this.getInfo())}},created:function(){this.orderNum=this.orderRow.id||null,this.orderNum&&this.getInfo()},methods:{getInfo:function(){var e=this;return Object(s["a"])(regeneratorRuntime.mark((function t(){var a;return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:return t.prev=0,t.next=3,Object(o["U"])("get",e.orderNum);case 3:a=t.sent,e.formObj=a,e.formObj.reason=1===e.editType?e.changeInputBack(e.formObj.reason):e.formObj.reason,e.formObj.t_deal_suggestion=2===e.editType?e.changeInputBack(e.formObj.t_deal_suggestion):e.formObj.t_deal_suggestion,e.formObj.c_deal_suggestion=3===e.editType?e.changeInputBack(e.formObj.c_deal_suggestion):e.formObj.c_deal_suggestion,e.headData=a.form_head_data,e.listData=a.deal_details,t.next=14;break;case 12:t.prev=12,t.t0=t["catch"](0);case 14:case"end":return t.stop()}}),t,null,[[0,12]])})))()},submitFun:function(){var e=this;return Object(s["a"])(regeneratorRuntime.mark((function t(){var a,r,n,s;return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:return t.prev=0,a={},r="",n=null,e.orderNum?(n=e.formObj.id,a={t_deal_suggestion:e.formObj.t_deal_suggestion,c_deal_suggestion:e.formObj.c_deal_suggestion,reason:e.formObj.reason,deal_user:e.formObj.deal_user,deal_date:e.formObj.deal_date,t_deal_user:e.formObj.t_deal_user,t_deal_date:e.formObj.t_deal_date,c_deal_user:e.formObj.c_deal_user,c_deal_date:e.formObj.c_deal_date},r="put"):(a=JSON.parse(JSON.stringify(e.formObj)),s=[],e.listData.forEach((function(e){s=s.concat(e.order_ids)})),e.$set(a,"order_ids",s),r="post",n=null,a.desc=e.changeInput(a.desc)),a.reason=e.changeInput(a.reason),a.t_deal_suggestion=e.changeInput(a.t_deal_suggestion),a.c_deal_suggestion=e.changeInput(a.c_deal_suggestion),e.loadingBtn=!0,t.next=11,Object(o["U"])(r,n,{data:a});case 11:e.$message({message:e.orderNum?"创建成功":"可在不合格处置单管理内查看，创建成功",type:"success",duration:5e3}),e.$emit("submitFun",a),e.formObj={status:"来料",currentDate:Object(i["d"])()},e.loadingBtn=!1,t.next=20;break;case 17:t.prev=17,t.t0=t["catch"](0),e.loadingBtn=!1;case 20:case"end":return t.stop()}}),t,null,[[0,17]])})))()},changeInput:function(e){return e?e.replace(/\r\n/g,"<br>").replace(/\n/g,"<br>").replace(/\s/g,"&nbsp;"):null},changeInputBack:function(e){return e?e.replace(/<br>/g,"\r\n").replace(/<br>/g,"\n").replace(/&nbsp;/g,"s"):""},editOne:function(e,t,a){this.$set(this.formObj,t,this.name),this.$set(this.formObj,a,Object(i["d"])())},editTwo:function(){this.formObj.name=this.name,this.formObj.currentDate=Object(i["d"])()},editThree:function(){this.formObj.name=this.name,this.formObj.currentDate=Object(i["d"])()},exportExcel:function(){var e=this;return Object(s["a"])(regeneratorRuntime.mark((function t(){return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:e.$refs.PDFBtn.style.display="none",document.getElementsByClassName("el-dialog__headerbtn")[0].style.display="none",window.print(),e.$refs.PDFBtn.style.display="block",document.getElementsByClassName("el-dialog__headerbtn")[0].style.display="block";case 5:case"end":return t.stop()}}),t)})))()}}},p=u,_=(a("e6be"),a("2877")),f=Object(_["a"])(p,r,n,!1,null,null,null);t["a"]=f.exports}}]);