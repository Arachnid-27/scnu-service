// 显示上传模态框
function upload(hid) {
    $('#upload-hid').val(hid);
    $('#homework-upload').modal({
        backdrop: 'static',
        keyboard: false
    });
}

// 显示作业详情
function details(cid, hid) {
    $.get('/scholat/details',
    {
        'cid': cid,
        'hid': hid
    },
    function(data, status) {
        $('#details-body').html(data.content);
        if (data.footer) {
            var str = '';
            for (var i in data.footer) {
                var obj = data.footer[i];
                str += '<p><a href="' + obj.url + '">' + obj.title + '</a></p>';
            }
            $('#details-footer').html(str);
        }
        $('#homework-details').modal('show');
    });
}