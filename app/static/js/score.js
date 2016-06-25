function get_score() {
    var arr = $('#opt-score').val().split('&')
    $.post("/score/get",
    {
        'year': arr[0],
        'term': arr[1]
    },
    function(data, status) {
        var str1 = '';
        for (var i in data.items) {
            var obj = data.items[i];
            str1 += '<tr><td>' + obj.name + '</td><td>' + obj.credit + '</td><td>' + obj.usual
            + '</td><td>' + obj.final + '</td><td>' + obj.total + '</td></tr>';
        }
        $('#content-score').html(str1);
        var str2 = '<p>绩点： ' + data.info.points + '</p><p>共修科目数： ' + data.info.all
        + '</p><p>未通过科目数： ' + data.info.unpass + '</p>';
        $("#statistics-score").html(str2);
        $('#success-alert').fadeIn();
        setTimeout("$('#success-alert').fadeOut()", 1800);
    });
}