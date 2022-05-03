$(function(){
    $("#fileupload").fileupload({
        url: "upload",
        dataType: "json",
        replaceFileInput:false,
        add: function(e, data) {
            data.submit();
        },
        success: function(res, status) {
            console.log(res);
            var filePath = "/static/Uploads/" + res.filename;
            console.log(filePath);
            $("#imgUpload").attr("src", filePath);
            $("#filePath").val(filePath);
        },
        error: function(error) {
            console.log(error);
        }
    });
})
