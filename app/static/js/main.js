function account() {
    $.get('/account',
    function(data, status) {
        $('#sch-status').html(get_span(data.sch.status));
        $('#sch-operate').html(get_button(data.sch.status, data.sch.url));
        $('#lib-status').html(get_span(data.lib.status));
        $('#lib-operate').html(get_button(data.lib.status, data.lib.url));
        $('#sco-status').html(get_span(data.sco.status));
        $('#sco-operate').html(get_button(data.sco.status, data.sco.url));
        $('#account-modal').modal('show');
    });
}

function get_span(status) {
    if (status) {
        return '<span class="label label-success label-align">已登录</span>';
    } else {
        return '<span class="label label-info label-align">未登录</span>';
    }
}

function get_button(status, url) {
    var str = '<button type="button" class="btn btn-default btn-xs" onclick="location.href=\'' + url + '\'">';
    if (status) {
        return str + '<span class="glyphicon glyphicon-send"></span> 登出</button>';
    } else {
        return str + '<span class="glyphicon glyphicon-user"></span> 登陆</button>';
    }
}