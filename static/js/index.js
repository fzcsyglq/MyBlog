$(function() {
    $.ajax({
        url: "/getHomeBlog",
        type: 'GET',
        success: function(res) {
            var blogObj = JSON.parse(res);
            console.log(res)
            $('#listTemplate').tmpl(blogObj).appendTo('#ulist');                        
        },
        error: function(error) {
            console.log(error);
        }
    });
});
