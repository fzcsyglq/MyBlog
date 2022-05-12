$(function() {
    $.ajax({
        url: "/getHomeBlog",
        type: 'GET',
        success: function(res) {
            var blogObj = JSON.parse(res);
            $('#listTemplate').tmpl(blogObj).appendTo('#ulist');                        
        },
        error: function(error) {
            console.log(error);
        }
    });
    $.ajax({
        type: 'GET',
        url: 'https://v1.hitokoto.cn?c=a',
        dataType: 'json',
        jsonp: 'callback',
        jsonpCallback: 'hitokoto',
        success (data) {
            $("#hitokoto").text(data.hitokoto);
            $("#hitokotofrom").text("——" + data.from);
        },
        error (jqXHR, textStatus, errorThrown) {
            // 错误信息处理
            console.error(textStatus, errorThrown);
        }
    });
});
function fetch163Playlist(playlistId) {
    return new Promise((ok, err) => {
        fetch(`https://v1.hitokoto.cn/nm/playlist/${playlistId}`)
            .then(response => response.json())
            .then(data => {
                const arr = [];
                data.playlist.trackIds.forEach(function (value) { // 参考：https://neteasecloudmusicapi.vercel.app/#/?id=%e8%8e%b7%e5%8f%96%e6%ad%8c%e5%8d%95%e8%af%a6%e6%83%85
                    arr.push(value.id);
                });
                return arr;
            })
            .then(fetch163Songs)
            .then(ok)
            .catch(err);
    });
}

function fetch163Songs(Ids) {
    return new Promise(function (ok, err) {
        let ids;
        switch (typeof Ids) {
        case 'number':
            ids = [Ids];
            break;
        case 'object':
            if (!Array.isArray(Ids)) {
                err(new Error('Please enter array or number'));
                return;
            }
            ids = Ids;
            break;
        default:
            err(new Error('Please enter array or number'));
            return;
            break;
        }  
        fetch(`https://v1.hitokoto.cn/nm/summary/${ids.join(',')}?lyric=true&common=true`)
            .then(response => response.json())
            .then(data => {
                var songs = [];
                data.songs.forEach(function (song) {
                    songs.push({
                        name: song.name,
                        url: song.url,
                        artist: song.artists.join('/'),
                        album: song.album.name,
                        pic: song.album.picture,
                        lrc: song.lyric
                    });
                });                
                return songs;
            })
            .then(ok)
            .catch(err);
    });
}

// 使用测试
/*
fetch163Playlist(7400800757)
    .then(console.log)
    .catch(console.error);

fetch163Playlist(2158283120)
    .then(console.log)
    .catch(console.error);

fetch163Songs([28391863, 22640061])
    .then(console.log)
    .catch(console.error);*/
