(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-bf72cdf4"],{"4c72":function(t,e,a){"use strict";a.r(e);var l=function(){var t=this,e=t.$createElement,a=t._self._c||e;return a("div",{staticStyle:{"margin-top":"25px"}},[a("el-form",{attrs:{inline:!0}},[a("el-form-item",{attrs:{label:"工程名"}},[a("el-input",{attrs:{placeholder:"密炼",disabled:!0},model:{value:t.projectName,callback:function(e){t.projectName=e},expression:"projectName"}})],1),a("el-form-item",{attrs:{label:"日期"}},[a("el-date-picker",{attrs:{type:"date",placeholder:"选择日期",format:"yyyy-MM-dd","value-format":"yyyy-MM-dd"},on:{change:t.performanceDateChange},model:{value:t.performanceDate,callback:function(e){t.performanceDate=e},expression:"performanceDate"}})],1),a("el-form-item",{attrs:{label:"机台"}},[a("el-select",{attrs:{clearable:"",placeholder:"请选择"},on:{change:t.equipNoChange,"visible-change":t.equipNoVisibleChange},model:{value:t.equipNo,callback:function(e){t.equipNo=e},expression:"equipNo"}},t._l(t.equipNoOptions,(function(t){return a("el-option",{key:t.equip_no,attrs:{label:t.equip_no,value:t.equip_no}})})),1)],1)],1),a("el-table",{staticStyle:{width:"100%"},attrs:{data:t.tableData,border:""}},[a("el-table-column",{attrs:{label:"处理",width:"40"}}),a("el-table-column",{attrs:{prop:"equip_no",label:"机型"}}),a("el-table-column",{attrs:{prop:"product_no",width:"180px",label:"胶料代码"},scopedSlots:t._u([{key:"default",fn:function(e){return[a("span",{staticStyle:{"margin-left":"10px"},domProps:{textContent:t._s(e.row.product_no)}}),a("el-button",{staticStyle:{float:"right",width:"25%"},attrs:{icon:"el-icon-search",type:"text",size:"mini"},on:{click:function(a){return t.clickProductNo(e.row)}}})]}}])}),a("el-table-column",{attrs:{prop:"plan_weight",label:"标准重量"}}),a("el-table-column",{attrs:{prop:"plan_trains",label:"日计划"}}),a("el-table-column",{attrs:{prop:"actual_trains",label:"日结果"}}),a("el-table-column",{attrs:{align:"center",prop:"mr_material_requisition_classes",label:"早班"}},[a("el-table-column",{attrs:{prop:"classes_data[0].plan_trains",label:"计划"}}),a("el-table-column",{attrs:{prop:"classes_data[0].actual_trains",label:"结果"}})],1),a("el-table-column",{attrs:{align:"center",prop:"mr_material_requisition_classes",label:"中班"}},[a("el-table-column",{attrs:{prop:"classes_data[1].plan_trains",label:"计划"}}),a("el-table-column",{attrs:{prop:"classes_data[1].actual_trains",label:"结果"}})],1),a("el-table-column",{attrs:{align:"center",prop:"mr_material_requisition_classes",label:"夜班"}},[a("el-table-column",{attrs:{prop:"classes_data[2].plan_trains",label:"计划"}}),a("el-table-column",{attrs:{prop:"classes_data[2].actual_trains",label:"结果"}})],1),a("el-table-column",{attrs:{prop:"download",label:"操作"}})],1),a("el-dialog",{attrs:{title:"胶料产出反馈",visible:t.dialogVisibleRubber,width:"900px"},on:{"update:visible":function(e){t.dialogVisibleRubber=e}}},[a("el-form",{attrs:{inline:!0}},[a("el-form-item",{attrs:{label:"胶料区分: "}},[t._v(" "+t._s(t.palletFeedObj.hasOwnProperty("stage")?t.palletFeedObj.stage:"--")+" ")]),a("el-form-item",{attrs:{label:"胶料编码: "}},[t._v(" "+t._s(t.palletFeedObj.product_no)+" ")]),a("el-form-item",{attrs:{label:"班次: "}},[t._v(" "+t._s(t.palletFeedObj.classes)+" ")]),a("el-form-item",{attrs:{label:"机台: "}},[t._v(" "+t._s(t.palletFeedObj.equip_no)+" ")])],1),a("el-table",{staticStyle:{width:"100%"},attrs:{data:t.palletFeedList,border:""}},[a("el-table-column",{attrs:{prop:"lot_no",label:"LOT"},scopedSlots:t._u([{key:"default",fn:function(e){return[t._v(" "+t._s(e.row.lot_no||"--")+" ")]}}])}),a("el-table-column",{attrs:{prop:"product_no",label:"胶料编码",width:"140px"}}),a("el-table-column",{attrs:{prop:"equip_no",label:"机台"}}),a("el-table-column",{attrs:{label:"BAT"},scopedSlots:t._u([{key:"default",fn:function(e){return[a("div",{staticStyle:{color:"#1989fa",cursor:"pointer"},on:{click:function(a){return t.clickBAT(e.row)}}},[t._v(" "+t._s(e.row.begin_trains)+"--"+t._s(e.row.end_trains))])]}}])}),a("el-table-column",{attrs:{prop:"actual_weight",label:"生产重量"}}),a("el-table-column",{attrs:{label:"生产时间"},scopedSlots:t._u([{key:"default",fn:function(e){return[t._v(" "+t._s(e.row.end_time.split(" ")[1])+" ")]}}])}),a("el-table-column",{attrs:{prop:"classes",label:"班次"}}),a("el-table-column",{attrs:{prop:"operation_user",label:"作业者"}})],1),a("page",{attrs:{total:t.totalRubber,"current-page":t.pageRubber},on:{currentChange:t.currentChangeRubber}})],1),a("el-dialog",{attrs:{title:"BAT查询",visible:t.dialogVisibleBAT,width:"900px"},on:{"update:visible":function(e){t.dialogVisibleBAT=e}}},[a("div",{staticStyle:{position:"relative"}},[a("el-form",{staticStyle:{"margin-right":"100px"},attrs:{inline:!0}},[a("el-form-item",{attrs:{label:"胶料区分: "}},[t._v(" "+t._s(t.BATObj.stage)+" ")]),a("el-form-item",{attrs:{label:"胶料编码: "}},[t._v(" "+t._s(t.BATObj.product_no)+" ")]),a("el-form-item",{attrs:{label:"班次: "}},[t._v(" "+t._s(t.BATObj.classes)+" ")]),a("el-form-item",{attrs:{label:"机台: "}},[t._v(" "+t._s(t.BATObj.equip_no)+" ")]),a("el-form-item",{attrs:{label:"车次: "}},[t._v(" "+t._s(t.BATObj.begin_trains)+" -- "+t._s(t.BATObj.end_trains)+" ")])],1)],1),a("el-table",{staticStyle:{width:"100%"},attrs:{data:t.BATList}},[a("el-table-column",{attrs:{prop:"equip_no",label:"机台"}}),a("el-table-column",{attrs:{prop:"name",label:"日期",width:"110"},scopedSlots:t._u([{key:"default",fn:function(e){return[t._v(" "+t._s(e.row.end_time.split(" ")[0])+" ")]}}])}),a("el-table-column",{attrs:{prop:"classes",label:"班次"}}),a("el-table-column",{attrs:{prop:"product_no",label:"胶料编码"}}),a("el-table-column",{attrs:{prop:"actual_trains",label:"车次"}}),a("el-table-column",{attrs:{prop:"actual_weight",label:"胶"}}),a("el-table-column",{attrs:{prop:"end_time-begin-time",label:"时间",width:"160"},scopedSlots:t._u([{key:"default",fn:function(e){return[t._v(" "+t._s(e.row.begin_time)+" -- "+t._s(e.row.end_time)+" ")]}}])}),a("el-table-column",{attrs:{prop:"equip_status.temperature",label:"温度"}}),a("el-table-column",{attrs:{prop:"equip_status.energy",label:"电量"}}),a("el-table-column",{attrs:{prop:"equip_status.rpm",label:"RPM"}}),a("el-table-column",{attrs:{label:"操作"},scopedSlots:t._u([{key:"default",fn:function(e){return[a("el-button",{attrs:{size:"mini"},on:{click:function(a){return t.clickView(e.row,e.$index)}}},[t._v("查看图表")])]}}])})],1)],1),a("el-dialog",{attrs:{title:"分析图表",modal:!0,"close-on-click-modal":!1,"modal-append-to-body":!1,width:"900px",visible:t.dialogVisibleGraph},on:{"update:visible":function(e){t.dialogVisibleGraph=e}}},[a("ve-line",{attrs:{height:"500px",data:t.chartData,settings:t.chartSettings,"after-set-option":t.afterSetOption}})],1)],1)},r=[],i=(a("4160"),a("b0c0"),a("ac1f"),a("1276"),a("159b"),a("b775")),n=a("99b1");function o(t){return Object(i["a"])({url:n["a"].EquipUrl,method:"get",params:t})}function s(t){return Object(i["a"])({url:n["a"].PalletFeedBacksUrl,method:"get",params:t})}function c(t){return Object(i["a"])({url:n["a"].TrainsFeedbacksUrl,method:"get",params:t})}function u(t){return Object(i["a"])({url:n["a"].EchartsListUrl,method:"get",params:t})}function p(t){return Object(i["a"])({url:n["a"].ProductActualUrl,method:"get",params:t})}function b(t){return Object(i["a"])({url:n["a"].PalletFeedbacksUrl,method:"get",params:t})}function d(t){return Object(i["a"])({url:n["a"].ProductDayPlanNoticeUrl,method:"post",id:t})}var m=a("3e51"),_=a("ed08"),h={components:{page:m["a"]},data:function(){return this.chartSettings={labelMap:{created_date_date:"时间",power:"功率",temperature:"温度",energy:"能量",pressure:"压力",rpm:"转速"},axisSite:{right:["temperature","rpm","energy","pressure"]}},{tableData:[],performanceDate:"",projectName:"",equipNo:"",equipNoOptions:[],dialogAddMaterialBaseInfoVisible:!1,palletFeedObj:{},palletFeedList:[],BATObj:{},BATList:[],dialogVisibleRubber:!1,tableDataRubber:[],tableDataBAT:[],dialogVisibleBAT:!1,dialogVisibleGraph:!1,currentPage:1,total:0,totalRubber:0,pageRubber:1,getParams:{page:1},chartData:{columns:["created_date_date","power","temperature","energy","pressure","rpm"],rows:[]},options:{title:{show:!0,text:"主标题",textAlign:"left"},yAxis:[{min:0,max:2500,splitNumber:5,interval:500},{min:0,max:200,splitNumber:5,interval:40}],toolbox:{itemSize:20,itemGap:30,right:50,feature:{dataZoom:{yAxisIndex:"none"},saveAsImage:{name:"",pixelRatio:2}}}}}},created:function(){this.getSearchTime(),this.currentChange(1)},methods:{downloadClick:function(t){},performanceDateChange:function(){this.currentChange(1)},equipNoVisibleChange:function(t){if(t){var e=this;o({all:1,category_name:"密炼设备"}).then((function(t){e.equipNoOptions=t.results}))}},equipNoChange:function(){this.currentChange(1)},clickProductNo:function(t){this.dialogVisibleRubber=!0,this.palletFeedObj=t,this.pageRubber=1,this.getRubberCoding()},getRubberCoding:function(){var t=this,e=this.performanceDate;e||(e=Object(_["b"])()),s({page:t.pageRubber,product_no:t.palletFeedObj.product_no,equip_no:t.palletFeedObj.equip_no,day_time:e,ordering:"-product_time"}).then((function(e){t.totalRubber=e.count,t.palletFeedList=e.results||[]}))},currentChangeRubber:function(t){this.pageRubber=t,this.getRubberCoding()},clickBAT:function(t){this.dialogVisibleBAT=!0,this.BATObj=t,this.getBATList()},getBATList:function(){var t=this;c({plan_classes_uid:t.BATObj.plan_classes_uid,equip_no:t.BATObj.equip_no,actual_trains:t.BATObj.begin_trains+","+t.BATObj.end_trains}).then((function(e){t.BATList=e.results||[]}))},clickView:function(t){this.dialogVisibleGraph=!0,this.getEchartsList(t)},getEchartsList:function(t){var e=this;u({product_no:t.product_no,plan_classes_uid:t.plan_classes_uid,equip_no:t.equip_no,st:t.begin_time,et:t.end_time}).then((function(a){var l=a.results;l.forEach((function(t){t.created_date_date=t.product_time.split(" ")[1]?t.product_time.split(" ")[1]:t.product_time})),e.chartData.rows=l,e.options.title.text=e.chartData.rows.length>0&&e.chartData.rows[0].hasOwnProperty("product_time")?e.chartData.rows[0].product_time.split(" ")[0]:"",e.options.toolbox.feature.saveAsImage.name="工艺曲线_"+(t.equip_no||"")+"-"+(t.product_no||"")+"-"+(t.begin_time||"")})).catch((function(){}))},afterSetOption:function(t){t.setOption(this.options)},currentChange:function(t){var e=this;this.beforeGetData(),this.getParams["page"]=t,this.tableData=[],p(this.getParams).then((function(t){e.tableData=t.data}))},beforeGetData:function(){this.getParams["search_time"]=this.performanceDate,this.getParams["equip_no"]=this.equipNo},getSearchTime:function(){var t=new Date,e=t.getFullYear(),a=t.getMonth()+1,l=a<10?"0"+a:a,r=t.getDate(),i=r<10?"0"+r:r;this.performanceDate=e+"-"+l+"-"+i},detailsClick:function(t){this.getDetailsParams["product_no"]=t.product_no,this.getDetailsParams["equip_no"]=t.equip_no;var e=this;b(this.getDetailsParams).then((function(t){e.tableDataRubber=t.results})),this.dialogVisibleRubber=!0},opens:function(){var t=this;this.$nextTick((function(){t.pie1()}))},pie1:function(){},sendToAu:function(t){var e=this;d(t.id).then((function(t){e.$message("发送成功")})).catch((function(){e.$message("发送失败")}))}}},f=h,g=a("2877"),v=Object(g["a"])(f,l,r,!1,null,"6baace01",null);e["default"]=v.exports},ed08:function(t,e,a){"use strict";a.d(e,"b",(function(){return r})),a.d(e,"a",(function(){return n}));a("4160"),a("c975"),a("a9e3"),a("b64b"),a("d3b7"),a("4d63"),a("ac1f"),a("25f0"),a("4d90"),a("5319"),a("1276"),a("159b");var l=a("53ca");function r(t,e,a){var l=t?new Date(t):new Date,r={y:l.getFullYear(),m:i(l.getMonth()+1),d:i(l.getDate()),h:i(l.getHours()),i:i(l.getMinutes()),s:i(l.getSeconds()),a:i(l.getDay())};return e?r.y+"-"+r.m+"-"+r.d+" "+r.h+":"+r.i+":"+r.s:a&&"continuation"===a?r.y+r.m+r.d+r.h+r.i+r.s:r.y+"-"+r.m+"-"+r.d}function i(t){return t=Number(t),t<10?"0"+t:t}function n(t){if(!t&&"object"!==Object(l["a"])(t))throw new Error("error arguments","deepClone");var e=t.constructor===Array?[]:{};return Object.keys(t).forEach((function(a){t[a]&&"object"===Object(l["a"])(t[a])?e[a]=n(t[a]):e[a]=t[a]})),e}}}]);