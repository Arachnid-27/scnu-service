var cur_bar_code;
var cur_check;

function renew() {
    $.get('/library/renew',
    {
        'barcode': cur_bar_code,
        'code': $('#renew-input-code').val(),
        'check': cur_check
    },
    function (data, status) {
        $('#renew-verify').modal('hide');
        $('#renew-input-code').val('');
        fresh_popover();
        if (data.success) {
            $('#success-alert').fadeIn();
            setTimeout("$('#success-alert').fadeOut()", 1000);
            setTimeout('location.reload()', 1200);
        } else {
            $('#fail-alert').html('<strong>续借失败！</strong>' + data.msg);
            $('#fail-alert').fadeIn();
            setTimeout("$('#fail-alert').fadeOut()", 1000);
        }
    });
}

function show_verify(barcode, check) {
    cur_bar_code = barcode;
    cur_check = check;
    $('#renew-verify').modal('show');
}

function fresh_popover() {
    $('#renew-get-code').remove();
    $('#renew-get-code').popover('destroy');
    $('#renew-get-code-group').html('<button id="renew-get-code" class="btn btn-default" type="button">获取验证码</button>')
    $('#renew-get-code').popover({
        html : true,
        placement : 'right',
        content : '<img src="' + renew_verify_url + '?r=' + parseInt(Math.random().toFixed(5) * 10000) + '">'
    })
}
