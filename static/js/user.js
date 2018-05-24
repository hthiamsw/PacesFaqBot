var $messages = $('.messages-content'),
    d, h, m,
    i = 0;

var name; //Name of user
var _id; //_id of each entry in db
var id = 0; //id of response
var unsure_entry = false;
var unsure_response = '';
var area_verification = false;

$(window).load(function() {
    $messages.mCustomScrollbar();
    var d = new Date();
    var day = d.getDate();
    var month = d.getMonth() + 1;
    var year = d.getFullYear();
    if (day < 10) {
        day = "0" + day;
    }
    if (month < 10) {
        month = "0" + month;
    }
//    name = "test";
    var date = day + "/" + month + "/" + year;
    while (name == null || name == "" || name == "null") {
        name = window.prompt("Please enter your name", "");
    }
    if (name == null || name == "" || name == "null") {
        name = "Unrecognised User";
    }
    $.post('/log', {
        name: name,
        date: date
    }).done(function(data) {
        _id = data;
    });
    setTimeout(function() {
        $('.message.loading').remove();
        var response = "Hi " + name + ", Thank you for using me!"
        $('<div class="message new"><figure class="avatar"><img src="static/res/dso_logo.png" /></figure>' + response + '</div>').appendTo($('.mCSB_container')).addClass('new');
        id++;
        $.post('/log/resp', {
            _id: _id,
            id: id,
            resp: response,
            time: logTime()
        })
    }, 50);
});

$(window).unload(function() {
    name = null;
    delete name;
});

function updateScrollbar() {
    $messages.mCustomScrollbar("update").mCustomScrollbar('scrollTo', 'bottom', {
        scrollInertia: 10,
        timeout: 0
    });
}

function logTime() {
    var d = new Date();
    var h = d.getHours();
    var m = d.getMinutes();
    var s = d.getSeconds();
    if (h < 10) {
        h = "0" + h;
    }
    if (m < 10) {
        m = "0" + m;
    }
    if (s < 10) {
        s = "0" + s;
    }
    var time = h + ":" + m + ":" + s;
    return time;
}

function setDate() {
    d = new Date();
    if (m != d.getMinutes()) {
        m = d.getMinutes();
        $('<div class="timestamp">' + d.getHours() + ':' + m + '</div>').appendTo($('.message:last'));
    }
}

function insertMessage() {
    msg = $('.message-input').val();
    if (msg == '') {
        return;
    }
    if (area_verification == true){
        area_verification = false;
        query = 'can you recommend me an expert in '+ msg;
        $.post('/log/entry', {
            _id: _id,
            entry: query,
            time: logTime()
        }, function(data) {
            responseCallback(data);
        });
    }
    else if (unsure_entry == false) {
        $.post('/log/entry', {
            _id: _id,
            entry: msg,
            time: logTime()
        }, function(data) {
            responseCallback(data);
        });
    } else if (msg.toLowerCase() == 'yes') {
        unsure_entry = false;
        $.post('/log/entry', {
            _id: _id,
            entry: msg,
            confirmed: unsure_response,
            time: logTime()
        }, function(data) {
            responseCallback(data);
        });
    } else if (msg.toLowerCase() == 'no') {
        unsure_entry = false;
        $.post('/log/entry', {
            _id: _id,
            entry: msg,
            time: logTime()
        }, function(data) {
            responseCallback('Sorry I am unable to answer you :(');
        });

    } else {
        $.post('/log/entry', {
            _id: _id,
            entry: msg,
            time: logTime()
        }, function(data) {
            responseCallback('Please answer with yes or no :(');
        });
    }
    if ($.trim(msg) == '') {
        return false;
    }
    $('<div class="message message-personal">' + msg + '</div>').appendTo($('.mCSB_container')).addClass('new');
    setDate();
    $('.message-input').val(null);
    updateScrollbar();
    //setTimeout(function() {
    //	fakeMessage(msg);
    //}, 500 + (Math.random() * 20) * 100);
}

function responseCallback(response) {
    respond_Message(response);
}

function respond_Message(response) {
    area_flag = response.includes("In which domain are you looking at?");
    response = response.split(" ");
    logic = response[response.length - 1];
    if ($('.message-input').val() != '') {
        return false;
    }
    if (area_flag){
        area_verification = true;
    }
    if (logic == 'False') {
        response.splice(-1);
        response = response.join(" ");
        $('<div class="message loading new"><figure class="avatar"><img src="static/res/dso_logo.png" /></figure><span></span></div>').appendTo($('.mCSB_container'));
        updateScrollbar();
        id++;
        setTimeout(function() {
            $('.message.loading').remove();
            $('<div class="message new"><figure class="avatar"><img src="static/res/dso_logo.png" /></figure>' + 'I am not sure, do you mean \"' + response + '\"? Please response with yes or no' + '</div>').appendTo($('.mCSB_container')).addClass('new');
            unsure_entry = true;
            unsure_response = response;
            i++;
            $.post('/log/resp', {
                _id: _id,
                id: id,
                resp: response,
                time: logTime()
            })
            setDate();
            updateScrollbar();
        }, 500 + (Math.random() * 20) * 100);
    } else {
        response = response.join(" ");
        $('<div class="message loading new"><figure class="avatar"><img src="static/res/dso_logo.png" /></figure><span></span></div>').appendTo($('.mCSB_container'));
        updateScrollbar();
        id++;
        setTimeout(function() {
            $('.message.loading').remove();
            $('<div class="message new"><figure class="avatar"><img src="static/res/dso_logo.png" /></figure>' + response + '</div>').appendTo($('.mCSB_container')).addClass('new');
            i++;
            $.post('/log/resp', {
                _id: _id,
                id: id,
                resp: response,
                time: logTime()
            })
            setDate();
            updateScrollbar();
        }, 500 + (Math.random() * 20) * 100);
    }
}

$('.message-submit').click(function() {
    insertMessage();
});

$(window).on('keydown', function(e) {
    if (e.which == 13) {
        insertMessage();
        return false;
    }
})