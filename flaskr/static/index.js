let view;
let map;
let jianyueTileLayer;
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

//    let centerPoint = [116, 39]; //大概是北京的经纬度
    let centerPoint = [113.08755916595523,28.251818487944462]; //大概是北京的经纬度
    // 创建一个瓦片图层实例
    jianyueTileLayer = new TintLayer({
//      urlTemplate: "http://webst02.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}",
      urlTemplate: "/mapImg/{z}/{x}/{y}",
      title: "高德",
    });


    //底层
    map = new Map({
//        basemap: "osm" //查看地图的模式，官方还有其他的模式
//            basemap:  //查看地图的模式，官方还有其他的模式
            layers : [jianyueTileLayer]
    });
    //3D容器
     view = new MapView({
        container: "viewDiv", //与html元素绑定
        map: map, //设置底层
        zoom: 15, //初始地图距离大小
        center: centerPoint //中心点(可以取小数) ，这里设置的北京
    });
    // 刷新瓦片
    refreshMapTileFunction = function refreshMapTile(){
        console.log("刷新。。。")
        // 移除瓦片
//      map.layers.pop(jianyueTileLayer)
        map.remove(jianyueTileLayer)
        jianyueTileLayer = new TintLayer({
          urlTemplate: "/mapImg/{z}/{x}/{y}",
          title: "高德",
        });
        map.add(jianyueTileLayer)

        // 加入瓦片，请求瓦片地图是同一个，但是后端已经改变了
//        map.layers.push(jianyueTileLayer)
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
        url: '/mapTile/mapList', // 替换为你的API端点
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
        alert('Selected value: ' + $(this).val());
        if($(this).val() == "AMap"){
            renderMapURLChooseDivAMap(null, mapList["AMap"])
        }else if ($(this).val() == "googleMap"){
            renderMapURLChooseDivGoogleMap(null, mapList["googleMap"])
        }
    });

    renderMapURLChooseDiv(currentMapSet,mapList)
}
// 渲染地图参数选择框
function renderMapURLChooseDiv(currentMapSet,mapList){
    if(currentMapSet["mapURLValue"] == "AMap"){
        renderMapURLChooseDivAMap(currentMapSet,mapList["AMap"])
    }else if (currentMapSet["mapURLValue"] == "googleMap"){
        renderMapURLChooseDivAMap(currentMapSet,mapList["googleMap"])
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


function renderMapURLChooseDivComm(currentMapSet,mapList){
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
        textareaHtml = "<textarea id='httpProxies' name='httpProxies' rows='4' cols='50'>"+currentMapSet["mapURLProxies"]+"</textarea>"
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
        textareaHtml = "<textarea id='httpHeaders' name='httpHeaders' rows='4' cols='50'>"+currentMapSet["mapURLHeaders"]+"</textarea>"
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
            refreshMapTileFunction()
        },
        error: function(xhr, status, error) {
            // 请求失败时的回调函数
            console.error('Error:', error);
            alert('/mapTile/setMapList-Error:', error);
        }
    });

});
