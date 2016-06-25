function renew(barcode) {
    $.get('/library/renew',
    {
        'barcode': barcode
    },
    function (data, status) {
        if (data.success) {
            $('#success-alert').fadeIn();
            setTimeout("$('#success-alert').fadeOut()", 1000);
            setTimeout('location.reload()', 1200);
        } else {
            $('#fail-alert').html('<strong>续借失败！</strong>' + data.msg)
            $('#fail-alert').fadeIn();
            setTimeout("$('#fail-alert').fadeOut()", 1000);
        }
    });
}