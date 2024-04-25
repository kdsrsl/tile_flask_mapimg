//上传文件
function uploadMap(fileTypes){
    let fileMapInput = $("#fileMapInput")
    let mapFile = fileMapInput[0].files[0]
    if(! mapFile){
        alert("请选择文件上传！")
        return
    }
    console.log("mapFile.name:"+mapFile.name)
    console.log("mapFile.size:"+mapFile.size)
    console.log("mapFile.type:"+mapFile.type)
    //校验文件
    //1 大小 现在200MB
    if(mapFile.size/1024/1024>200){
        alert("文件不能超过200MB！")
        return
    }

    //2 压缩包 查看是否是压缩包
    let isZip = false
    let names = mapFile.name.split(".")
    let suffixName = names[names.length-1]
    for(let fileType of fileTypes){
        if(fileType.includes(suffixName)){
            isZip = true
            break
        }
    }
    if(!isZip){
        alert("请上传压缩包")
    }

    console.log("可以上传文件")

    var formData = new FormData();
    formData.append('uploadMapType', $("#uploadMapType").val());
    formData.append('mapFile', mapFile);

    uploadMapPost(formData)

}

function uploadMapPost(formData){
    $.ajax({
        url:"/mapImg/upload",
        type:"POST",
        data: formData,
        contentType: false,
        processData: false,
        dataType: 'json', // 期望从服务器返回的数据类型
        success: function(response) {
            console.log('上传成功:', response);
        },
        error: function() {
            console.log('上传失败');
        }
    });

}