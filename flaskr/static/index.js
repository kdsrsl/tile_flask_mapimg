let view;
let map;
let myTileLayer;
let refreshMapTileFunction;

//使用arcgis.js
require([
        "esri/Map",
        "esri/views/SceneView",
        "esri/views/MapView",
        "esri/layers/TileLayer",
        "esri/layers/BaseTileLayer",
        "esri/Color",
        "esri/request",
    ],
    (Map, SceneView, MapView,TileLayer,BaseTileLayer, Color, esriRequest) => {

    // *******************************************************
    // 自定义图层类代码
    // 创建一个BaseTileLayer的子类
    // *******************************************************

    const TintLayer = BaseTileLayer.createSubclass({
      properties: {
        urlTemplate: null,
        tint: {
          value: null,
          type: Color,
        },
      },

      //为LayerView提供的给定级别、行和列生成tile url
      getTileUrl: function (level, row, col) {
        return this.urlTemplate.replace("{z}", level).replace("{x}", col).replace("{y}", row);
      },

      // 此方法获取指定级别和大小的瓦片
      // 重写此方法以处理从服务器返回的数据
      fetchTile: function (level, row, col, options) {
        // 调用getTileUrl（）方法来构造tiles的URL
        // 对于LayerView提供的给定级别、行和列
        const url = this.getTileUrl(level, row, col);
        // 基于生成的url请求平铺
        // the signal option 确保废弃的请求被中止
        return esriRequest(url, {
          responseType: "image",
          signal: options && options.signal,
        }).then(
          function (response) {
            // esri请求解析成功时
            // 从响应中获取图像
            const image = response.data;
            const width = this.tileInfo.size[0];
            const height = this.tileInfo.size[0];

            // 使用二维渲染上下文创建画布
            const canvas = document.createElement("canvas");
            const context = canvas.getContext("2d");
            canvas.width = width;
            canvas.height = height;

            // 将应用程序提供的色调应用于画布
            if (this.tint) {
              // 获取一个rgba形式的CSS颜色字符串，表示tint color实例.
              context.fillStyle = this.tint.toCss();
              context.fillRect(0, 0, width, height);

              // 在画布和steman平铺之间应用“差异”混合操作。差值混合操作从顶层（瓦片）中减去底层（画布），或者反过来总是得到一个正值
              context.globalCompositeOperation = "difference";
            }

            //将混合图像绘制到画布上。
            context.drawImage(image, 0, 0, width, height);

            return canvas;
          }.bind(this)
        );
      },
    });

    let centerPoint = [116.404177,39.909651]; //大概是北京天安门的经纬度

    // 创建一个瓦片图层实例
    myTileLayer = new TintLayer({
//      urlTemplate: "http://webst02.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}",
      urlTemplate: "/mapImg/{z}/{x}/{y}",
      title: "高德",
    });


    //底层
    map = new Map({
            layers : [myTileLayer]
    });
    //3D容器
     view = new MapView({
        container: "viewDiv", //与html元素绑定
        map: map, //设置底层
        zoom: 15, //初始地图距离大小
        center: centerPoint //中心点(可以取小数) ，这里设置的北京
    });

    $("#mapLatitude").val(view.center.latitude)
    $("#mapLongitude").val(view.center.longitude)
    view.on("drag", function(event){
        $("#mapLatitude").val(view.center.latitude)
        $("#mapLongitude").val(view.center.longitude)
    });
    // 刷新瓦片
    refreshMapTileFunction = function (){
        map.remove(myTileLayer)
        myTileLayer = new TintLayer({
          urlTemplate: "/mapImg/{z}/{x}/{y}",
          title: "高德",
        });
        map.add(myTileLayer)
    }
})

function init(){
    getCurrentMapSetting()
}
init()

//获取当前Map设置
function getCurrentMapSetting(){
    $.ajax({
        url: '/mapTile/currentMapSetting', // 替换为你的API端点
        type: 'GET', // 请求类型
        dataType: 'json', // 期望从服务器返回的数据类型
        success: function(response) {
            console.log('Response:', response);
            getMapList(response)
        },
        error: function(xhr, status, error) {
            // 请求失败时的回调函数
            console.error('Error:', error);
            alert('/mapTile/currentMapSetting-Error:', error);
        }
    });
}

//获取服务器可以选择的Map类型
function getMapList(currentMapSet){
    $.ajax({
        url: '/mapTile/mapList',
        type: 'GET', // 请求类型
        dataType: 'json', // 期望从服务器返回的数据类型
        success: function(response) {
            console.log('/mapTile/mapList--Response:', response);
            renderMapUrlSelectionDiv(currentMapSet["data"],response["data"])
        },
        error: function(xhr, status, error) {
            // 请求失败时的回调函数
            console.error('Error:', error);
            alert('/mapTile/currentMapSetting-Error:', error);
        }
    });
}

// 渲染地图源选择框
function renderMapUrlSelectionDiv(currentMapSet,mapList){
    //mapList 全部mapList
    //currentMapSet 当前选择的设置
    let mapURLDiv = $("#mapURLDiv")
    let mapURLChooseDiv = $("#mapURLChooseDiv")

    // 清空子节点
    mapURLDiv.empty()
    mapURLChooseDiv.empty()

    let labelHtml = $("<label for='mapUrl'>地图源:</label>")
    mapURLDiv.append(labelHtml)
    let selectHtmlStart = $("<select id='mapUrl' name='mapUrl'>")
    mapURLDiv.append(selectHtmlStart)
    let selectHtmlEnd = $("</select>")
    mapURLDiv.append(selectHtmlEnd)

    let mapUrl = $("#mapUrl")
    for(let i=0 ;i<mapList["mapURLValue"].length;i++){
        let selectHtml = ""
        if (currentMapSet["mapURLValue"] === mapList["mapURLValue"][i]){
             selectHtml = $("<option value='"+mapList["mapURLValue"][i]+"' selected>"+mapList["mapURLName"][i]+"</option>")
        }else{
             selectHtml = $("<option value='"+mapList["mapURLValue"][i]+"' >"+mapList["mapURLName"][i]+"</option>")
        }
        mapUrl.append(selectHtml)
    }

    // 监听变化
    mapUrl.change(function(){
        // 当选项改变时，这里的代码会被执行
//        alert('Selected value: ' + $(this).val());
        if($(this).val() == "AMap"){
            renderMapURLChooseDivAMap(null, mapList["AMap"])
        }else if ($(this).val() == "googleMap"){
            renderMapURLChooseDivGoogleMap(null, mapList["googleMap"])
        }else if ($(this).val() == "customMap"){
            renderMapURLChooseDivCoustomMap(null, mapList["customMap"])
        }
    });

    renderMapURLChooseDiv(currentMapSet,mapList)
}
// 渲染地图参数选择框,初次渲染
function renderMapURLChooseDiv(currentMapSet,mapList){
    if(currentMapSet["mapURLValue"] == "AMap"){
        renderMapURLChooseDivAMap(currentMapSet,mapList["AMap"])
    }else if (currentMapSet["mapURLValue"] == "googleMap"){
        renderMapURLChooseDivGoogleMap(currentMapSet,mapList["googleMap"])
    }else if (currentMapSet["mapURLValue"] == "customMap"){
        renderMapURLChooseDivCoustomMap(currentMapSet, mapList["customMap"])
    }
}
// 渲染google选择
function renderMapURLChooseDivGoogleMap(currentMapSet,mapListGoogleMap){
    console.log("GOOGLE===",currentMapSet,mapListGoogleMap)
    //===================
    renderMapURLChooseDivComm(currentMapSet,mapListGoogleMap)

    let mapURLChooseDiv = $("#mapURLChooseDiv")

    let labelHtml = "<label for='glType'>国家码:</label>"
    mapURLChooseDiv.append(labelHtml)
    let selectHtmlStart = "<select id='glType' name='glType'>"
    let selectHtmlEnd = "</select>"
    mapURLChooseDiv.append(selectHtmlStart)
    mapURLChooseDiv.append(selectHtmlEnd)

    let glType = $("#glType")

    for(let i = 0; i < mapListGoogleMap["glValue"].length; i++){
        let optHtml;
        if(currentMapSet!=null
        &&currentMapSet["mapURLgl"]!=null
        &&currentMapSet["mapURLgl"] === mapListGoogleMap["glValue"][i]){
            optHtml = "<option selected value='"+mapListGoogleMap["glValue"][i]+"' >"+mapListGoogleMap["glName"][i]+"</option>"
        }else{
            optHtml = "<option value='"+mapListGoogleMap["glValue"][i]+"' >"+mapListGoogleMap["glName"][i]+"</option>"
        }
        glType.append(optHtml)
    }
    mapURLChooseDiv.append("<br>")

    labelHtml = "<label for='hlType'>本地语言:</label>"
    mapURLChooseDiv.append(labelHtml)
    selectHtmlStart = "<select id='hlType' name='hlType'>"
    selectHtmlEnd = "</select>"
    mapURLChooseDiv.append(selectHtmlStart)
    mapURLChooseDiv.append(selectHtmlEnd)

    let hlType = $("#hlType")

    for(let i = 0; i < mapListGoogleMap["hlValue"].length; i++){
        let optHtml;
        if(currentMapSet!=null
        &&currentMapSet["mapURLhl"]!=null
        &&currentMapSet["mapURLhl"] === mapListGoogleMap["hlValue"][i]){
            optHtml = "<option selected value='"+mapListGoogleMap["hlValue"][i]+"' >"+mapListGoogleMap["hlName"][i]+"</option>"
        }else{
            optHtml = "<option value='"+mapListGoogleMap["hlValue"][i]+"' >"+mapListGoogleMap["hlName"][i]+"</option>"
        }
        hlType.append(optHtml)
    }
    mapURLChooseDiv.append("<br>")

}
// 渲染AMap选择
function renderMapURLChooseDivAMap(currentMapSet,mapListAMap){
    console.log("AMAP===",currentMapSet,mapListAMap)
    renderMapURLChooseDivComm(currentMapSet,mapListAMap)
}
//渲染自定义Map选择
function renderMapURLChooseDivCoustomMap(currentMapSet,mapListCoustomMap){
    //currentMapSet 当前选择的
    //mapListAMap所有选择的值
    let mapURLChooseDiv = $("#mapURLChooseDiv")
    mapURLChooseDiv.empty()

    let labelHtml = "<label for='mapType'>地图类型:</label>"
    mapURLChooseDiv.append(labelHtml)
    let selectHtmlStart = "<select id='mapType' name='mapType'>"
    let selectHtmlEnd = "</select>"
    mapURLChooseDiv.append(selectHtmlStart)
    mapURLChooseDiv.append(selectHtmlEnd)

    let mapType = $("#mapType")
    for(let i = 0; i < mapListCoustomMap["mapTypeValue"].length; i++){
        let optHtml;
        if(currentMapSet!=null
        &&currentMapSet["mapURLStyle"]!=null
        &&currentMapSet["mapURLStyle"] === mapListCoustomMap["mapTypeValue"][i]){
            optHtml = "<option selected value='"+mapListCoustomMap["mapTypeValue"][i]+"' >"+mapListCoustomMap["mapTypeValue"][i]+"</option>"
        }else{
            optHtml = "<option value='"+mapListCoustomMap["mapTypeValue"][i]+"' >"+mapListCoustomMap["mapTypeValue"][i]+"</option>"
        }
        mapType.append(optHtml)
    }
    mapURLChooseDiv.append("<br>")
    //========上传============


    renderMapUploadDivCoustomMap(mapListCoustomMap)

    //============提交上传，完成后，maplist要重新渲染========
}

//渲染上传自定义上传
function renderMapUploadDivCoustomMap(mapListCoustomMap){
    let opt = $("#opt")
    let uploadMapDivHtml = "<div id='uploadMapDiv'></div>"
    opt.append(uploadMapDivHtml)

    let uploadMapDiv = $("#uploadMapDiv")
    let formAction = "/mapImg/upload"
    let formHtml = "<form id='uploadForm' action='"+formAction+"' method='post' enctype='multipart/form-data'></form>"
    uploadMapDiv.append("<hr>")
    uploadMapDiv.append(formHtml);

    //1.选择合并到那个地图类型中，可以不合并，新建一个地图类型
    let uploadForm = $("#uploadForm")
    let labelHtml = "<label for='uploadMapType'>是否合并地图类型:</label>"
    uploadForm.append(labelHtml)
    let selectHtml = "<select id='uploadMapType' name='uploadMapType'></select>"
    uploadForm.append(selectHtml)

    let uploadMapType = $("#uploadMapType")
    let optHtml = "<option value=''>新地图类型</option>"
    uploadMapType.append(optHtml)
    for(let i = 0; i < mapListCoustomMap["mapTypeValue"].length; i++){
        let optHtml = "<option value='"+mapListCoustomMap["mapTypeValue"][i]+"' >合并"+mapListCoustomMap["mapTypeValue"][i]+"类型</option>"
        uploadMapType.append(optHtml)
    }

    //2.压缩包
    let inputUploadHtml = '<br><br><label for="file-input">选择资源压缩包：</label>';
    let acceptFileType = "";
//    for(let zipType of mapListCoustomMap["zipTypes"]){
//        acceptFileType+=zipType+","
//    }
    for(let index in mapListCoustomMap["zipTypes"]){
        if(index == mapListCoustomMap["zipTypes"].length-1){
            acceptFileType+=mapListCoustomMap["zipTypes"][index]
        }else{
            acceptFileType+=mapListCoustomMap["zipTypes"][index]+","
        }
    }

    inputUploadHtml += '<input type="file" id="file-input" name="file" accept="'+acceptFileType+'">';
    uploadForm.append(inputUploadHtml)

    let submitBtn = '<br><br><button type="submit">上传文件</button>';
    uploadForm.append(submitBtn)
}


function renderMapURLChooseDivComm(currentMapSet,mapList){
    let uploadMapDiv = $("#uploadMapDiv")
    if (uploadMapDiv){
        uploadMapDiv.empty()
    }
    let mapURLChooseDiv = $("#mapURLChooseDiv")
    mapURLChooseDiv.empty()

    let labelHtml = "<label for='mapType'>地图类型:</label>"
    mapURLChooseDiv.append(labelHtml)
    let selectHtmlStart = "<select id='mapType' name='mapType'>"
    let selectHtmlEnd = "</select>"
    mapURLChooseDiv.append(selectHtmlStart)
    mapURLChooseDiv.append(selectHtmlEnd)

    let mapType = $("#mapType")
    for(let i = 0; i < mapList["mapTypeValue"].length; i++){
        let optHtml;
        if(currentMapSet!=null
        &&currentMapSet["mapURLStyle"]!=null
        &&currentMapSet["mapURLStyle"] === mapList["mapTypeValue"][i]){
            optHtml = "<option selected value='"+mapList["mapTypeValue"][i]+"' >"+mapList["mapTypeName"][i]+"</option>"
        }else{
            optHtml = "<option value='"+mapList["mapTypeValue"][i]+"' >"+mapList["mapTypeName"][i]+"</option>"
        }
        mapType.append(optHtml)
    }
    mapURLChooseDiv.append("<br>")

    labelHtml = "<label for='httpParameter'>更多参数：</label>"
    let inputHtml = ""
    if(currentMapSet!=null
        &&currentMapSet["mapURLHttpParameter"]!=null){
        inputHtml = "<input id='httpParameter' name='httpParameter' type='text' value='"+currentMapSet["mapURLHttpParameter"]+"'/>"
    }else{
        inputHtml = "<input id='httpParameter' name='httpParameter' type='text'/>"
    }
    mapURLChooseDiv.append(labelHtml)
    mapURLChooseDiv.append(inputHtml)
    mapURLChooseDiv.append("<br>")

    labelHtml = "<label for='httpProxies'>代理端口：</label>"
    let textareaHtml = ""
    if(currentMapSet!=null
        &&currentMapSet["mapURLProxies"]!=null){
        textareaHtml = "<textarea id='httpProxies' name='httpProxies' rows='4' cols='50'>"+JSON.stringify(currentMapSet["mapURLProxies"])+"</textarea>"
    }else{
        textareaHtml = "<textarea id='httpProxies' name='httpProxies' rows='4' cols='50'></textarea>"
    }
    mapURLChooseDiv.append(labelHtml)
    mapURLChooseDiv.append(textareaHtml)
    mapURLChooseDiv.append("<br>")

    labelHtml = "<label for='httpHeaders'>请求头设置：</label>"
    textareaHtml = ""
    if(currentMapSet!=null
        &&currentMapSet["mapURLHeaders"]!=null){
        textareaHtml = "<textarea id='httpHeaders' name='httpHeaders' rows='4' cols='50'>"+JSON.stringify(currentMapSet["mapURLHeaders"])+"</textarea>"
    }else{
        textareaHtml = "<textarea id='httpHeaders' name='httpHeaders' rows='4' cols='50'></textarea>"
    }
    mapURLChooseDiv.append(labelHtml)
    mapURLChooseDiv.append(textareaHtml)
    mapURLChooseDiv.append("<br>")
}


$("#setMapProp").click(function(){
    let mapUrl = $("#mapUrl").val()
    let glType = ""
    let hlType = ""
    if(mapUrl == "googleMap"){
        glType = $("#glType").val()
        hlType = $("#hlType").val()
    }
    let requestData = {
        "mapUrl": mapUrl,
        "mapType": $("#mapType").val(),
        "httpParameter": $("#httpParameter").val(),
        "httpProxies": $("#httpProxies").val(),
        "httpHeaders": $("#httpHeaders").val(),
        "glType": glType,
        "hlType": hlType
    }

    $.ajax({
        url: '/mapTile/setMapList', // 替换为你的API端点
        type: 'POST', // 请求类型
        headers: {
            'Content-Type': 'application/json'
        },
        data: JSON.stringify(requestData),
        dataType: 'json', // 期望从服务器返回的数据类型
        success: function(response) {
            console.log('/mapTile/setMapList-Response:', response);
            if(response["code"]!=200){
                alert('/mapTile/setMapList-Error:'+response["msg"]);
            }else{
                refreshMapTileFunction()
            }
        },
        error: function(xhr, status, error) {
            // 请求失败时的回调函数
            console.error('Error:', error);
            alert('/mapTile/setMapList-Error:'+error);
        }
    });

});


$("#setMapCenterBtn").click(function(){
    let setLongitude = parseFloat($("#mapLongitude").val());
    let setLatitude = parseFloat($("#mapLatitude").val());

    let latitude = view.center.latitude
    let longitude = view.center.longitude

    let distance = Math.sqrt((setLongitude-longitude)**2 + (setLatitude-latitude)**2)
    console.log("distance："+distance)
    let duration = distance/0.1 * 100;
    duration = duration>3000 ? 3000: duration
    console.log("duration："+duration)
    let opts = {
        duration: duration
    };
    // 有过度动画
    view.goTo({
        center: [setLongitude, setLatitude],
//        zoom: 10
    },opts)

    //无过度动动画
//    view.set({
//        center: [parseFloat($("#mapLongitude").val()), parseFloat($("#mapLatitude").val())]
//    })
})
