function load_score() {
    $.post('/jwc/score',
    {
        'year': $("#year-score").val(),
        'term': $("#term-score").val()
    },
    function(data, status) {
        var content = '';
        for (var i in data.items) {
            var obj = data.items[i];
            content += '<tr><td>' + obj.name + '</td><td>' + obj.credit + '</td><td>' + obj.gpa + '</td><td>'
            + obj.usual + '</td><td>' + obj.exam + '</td><td>' + obj.total + '</td></tr>';
        }
        $('#content-score').html(content);
        if (data.info) {
            var info = '<p>总学分： ' + data.info.sum + '</p><p>最高分数： ' + data.info.max + '</p><p>最低分数： '
            + data.info.min + '</p><p>平均绩点： ' + data.info.ave + '</p>';
            $('#info-score').html(info);
        } else {
            $('#info-score').html('');
        }
        $('#success-alert').fadeIn();
    });
    setTimeout('$("#success-alert").fadeOut()', 1800);
}

function load_schedule() {
    var year = $('#year-schedule').val();
    var term = $('#term-schedule').val();
    if (selected_year !=  year || selected_term != term) {
        $.post('/jwc/schedule',
        {
            'year': year,
            'term': term
        },
        function(data, status) {
            $('#content-schedule').html(data.table);
            $('#success-alert').fadeIn();
        });
        setTimeout('$("#success-alert").fadeOut()', 1800);
        selected_year = year;
        selected_term = term;
    }
}