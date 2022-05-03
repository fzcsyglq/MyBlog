$(function() {
    $.ajax({
        url: '/getBlog',
        type: 'GET',
        success: function(res) {
            var blogObj = JSON.parse(res);
            $('#listTemplate').tmpl(blogObj).appendTo('#ulist');                        
        },
        error: function(error) {
            console.log(error);
        }
    });
    $("#btnUpdate").on("click", function() {
        $.ajax({
            url: "/updateBlog",
            data: {
                title: $("#editTitle").val(),
                description: $("#editDescription").val(),
                id: localStorage.getItem("editId"),
                filepath: $("#filePath").val(),
                private_: $("#chkPrivate").prop("checked")
            },
            type: "POST",
            success: function(res) {
                $("#editModal").modal("hide");
                GetBlogs();
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
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
});
function Edit(elm) {
    localStorage.setItem("editId", $(elm).attr("data-id"));
    $.ajax({
        url: "/getBlogById",
        data: {
            id: $(elm).attr("data-id")
        },
        type: "POST",
        success: function(res) {
            var data = JSON.parse(res);
            $("#editTitle").val(data[0]["Title"]);
            $("#editDescription").val(data[0]["Description"]);
            $("#editModal").modal("show");
            $("#imgUpload").attr("src", data[0]["FilePath"]);
            if(data[0]["Private"]=="1") {
                $("#chkPrivate").attr("checked","checked");
            }            
            console.log(res);
        },
        error: function(error) {
            console.log(error);
        }
    });
}
function GetBlogs() {
    $.ajax({
        url: "/getBlog",
        type: "GET",
        success: function(res) {
            var blogObj = JSON.parse(res);
            $("#ulist").empty();
            $("#listTemplate").tmpl(blogObj).appendTo("#ulist");
        },
        error: function(error) {
            console.log(error);
        }
    });
}
function ConfirmDelete(elm) {
    localStorage.setItem("deleteId", $(elm).attr("data-id"));
    $("#deleteModal").modal("show");
}
function Delete() {
    $.ajax({
        url: "/deleteBlog",
        data: {
            id: localStorage.getItem("deleteId")
        },
        type: "POST",
        success: function(res) {
            var result = JSON.parse(res);
            if(result.status == "OK") {
                $("#deleteModal").modal("hide");
                GetBlogs();
            } else {
                alert(result.status);
            }
        },
        error: function(error) {
            console.log(error);
        }
    })
}

