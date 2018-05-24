$body = $("body");
var convo;
var comment = 0;
var iden;
var convoid;
//Remember to add in the respective json file if adding new classifications
//TO DO Adding of recommendation admin verification
var classifications = ["Test", "AI", "Bot Profile", "Computers", "Conversations", "Drugs", "DSO",
    "Emotion", "Food", "Gossip", "Greetings", "History", "Humor",
    "Literature", "Money", "Movies", "Politics", "Psychology",
    "Science", "Sports", "Trivia"
];

window.onclick = function(event) {
    if (!event.target.matches('.dropdown-toggle .btn-block')) {
        $("#dropdown-menu").hide(); //Drop down the subnav on click
    }
}

$(window).load(function() {
    $.ajax({
        url: "/retrieve",
        async: true,
        success: function(data) {
            chatsCallback(data);
        }
    });
});



function chatsCallback(_data) {
    if (_data.result.length == 0) {
        $.confirm({
            title: 'Empty Entries',
            content: 'There are no entries in the database. Please get users to converse with the ChatBot. Browser will be redirected to the ChatBot',
            autoClose: 'redirect|8000',
            buttons: {
                redirect: {
                    text: 'Redirect now',
                    action: function() {
                        window.location.replace("http://127.0.0.1:5005");
                    }
                },
            }
        });
    }
    appendChats(_data);
}

function appendChats(result) {
    var ver = document.getElementById('verified');
    var value = ver.options[ver.selectedIndex].value;
    $.each(result, function() {
        $.each(this.reverse(), function() {
            if (value == 'all') {
                $("#chats").append(
                    '<button type="button" class="btn btn-primary btn-lg outline list-group-item list-group-item-action" id=' +
                    this._id + '>' + this.name +
                    '</button>');
                $("#" + this._id).append(
                    '<div class="chatdate">' +
                    this.date + '</div>');
            } else if (value == 'verified' && this.Verified == true) {
                $("#chats").append(
                    '<button type="button" class="btn btn-primary btn-lg outline list-group-item list-group-item-action" id=' +
                    this._id + '>' + this.name +
                    '</button>');
                $("#" + this._id).append(
                    '<div class="chatdate">' +
                    this.date + '</div>');
            } else if (value == 'unverified' && this.Verified == false) {
                $("#chats").append(
                    '<button type="button" class="btn btn-primary btn-lg outline list-group-item list-group-item-action" id=' +
                    this._id + '>' + this.name +
                    '</button>');
                $("#" + this._id).append(
                    '<div class="chatdate">' +
                    this.date + '</div>');
            }
        });
    });
}

$("#chats").on("click", "button",
    function() {
        if ($("#convos").length == 0) {
            $("#convodiv").append('<div class="list-group convos-content" id="convos"></div>');
        }
        $("#chats button").removeClass(
            "active");
        $("#chats button").removeAttr(
            "disabled");
        iden = this.id;
        $('#' + this.id).addClass("active");
        $('#' + this.id).attr("disabled",
            true);
        $("#convos").html('');
        $("#review").html('');
        comment = 0;
        appendConvo(this.id);
    });

function appendConvo(_id) {
    $.get('/retrieve/convo', {
        _id: _id
    }).done(function(data) {
        convoCallback(data)
    });
}

function convoCallback(data) {
    convo = data;
    var i = 0;
    $.each(convo, function() {
        $.each(this, function() {
            if (this.hasOwnProperty(
                    'Response')) {
                $("#convos").append(
                    '<div class="message_res" align="left" id="review' +
                    i +
                    '"><figure class="avatar_res"><img src="static/res/dso_logo.png" /></figure>' +
                    this.Response +
                    '<div class="chatdate">' +
                    this.Time + '</div>' +
                    '</div>');
            } else {
                $("#convos").append(
                    '<div class="message" align="right" id="review' + i + '"><figure class="avatar_entry"><img src="static/res/user.jpg" /></figure>' +
                    this.Entry +
                    '<div class="chatdate" style="text-align:left;">' +
                    this.Time + '</div> ' +
                    '</div>');
            }
            i++;
        });
    });
}

$("#convodiv").on("click", "div div",
    function() {
        $("#review").html('');
        $("#convos div").removeClass(
            "disabledbutton");
        if (this.className.includes("message_res")) {
            $("#" + this.id).addClass(
                'disabledbutton');
        }
        convoid = (this.id).replace(/\D/g,
            '');
        convoid = convoid / 2; //adding 1 to string
        convoid++; //adding 1 to string
        comment = 0;
        var number = this.id.replace(
            /[^\d]/g, '');
        if (this.className.includes(
                "message_res") && this.id != 'review0') {
            $.get('/retrieve/convo/review', {
                number: number
            }).done(function(data) {
                reviewCallback(data)
            });
            $("#review").append(
                '<div align="Center" id="label"><div class="page-subheader">Response Quality:</div></div>'
            );
            $("#label").append(
                '<label><input type="radio" id="QOR1" name="optradio">Totally Off</label>'
            );
            $("#label").append(
                '<label><input type="radio" id="QOR2" name="optradio">Somewhat Off</label>'
            );
            $("#label").append(
                '<label><input type="radio" id="QOR3" name="optradio">Bot-Like</label>'
            );
            $("#label").append(
                '<label><input type="radio" id="QOR4" name="optradio">Not Sure</label>'
            );
            $("#label").append(
                '<label><input type="radio" id="QOR5" name="optradio">Human-Like</label>'
            );
            $("#review").append(
                '<textarea class="scrollbar" rows="3" id="explain" placeholder="Please Justify Your reasons."></textarea>'
            );
            $("#review").append(
                '<div class="dropdown" id="classficationdiv"><button class="btn btn-primary dropdown-toggle btn-block" type="button" ' +
                'data-toggle="dropdown" id="classfication" >Select Classification' +
                '</button><ul class="dropdown-menu dropdown-menu-right list-group" role="menu" id="dropdown-menu">' +
                '</ul></div>'
            );
            $.each(classifications, function() {
                $("#dropdown-menu").append('<li class="list-group-item">' + this + '</li>')
            });
            $("#review").append(
                '<div align="left" id="altr" style="margin-bottom:5px;">Alternative Response:</div>'
            );
            $("#altr").append(
                '<button type="button" class="float-right btn btn-primary btn-sm outline"> + </button>'
            );
            $("#review").append(
                '<div class="text-center"><button type="button" id="submitbtn" class="btn btn-primary btn-sm outline">Submit</button></div>'
            );

        } else {
            $("#review").html('');
            comment = 0;
        }
    });

function reviewCallback(data) {
    $.each(data, function() {
        switch (this.Label) {
            case 1:
                $("#QOR1").attr('checked', true);
                break;
            case 2:
                $("#QOR2").attr('checked', true);
                break;
            case 3:
                $("#QOR3").attr('checked', true);
                break;
            case 4:
                $("#QOR4").attr('checked', true);
                break;
            case 5:
                $("#QOR5").attr('checked', true);
                break;
            default:
                break;

        }
        $('#explain').html(this.Explaination);
        corpus = this.Corpus;
        if (this.Classification != null) {
            $('#classfication').html(this.Classification);
        } else {
            $('#classfication').html('Select Classification');
        }
        if ($('#classfication').html() != "Select Classification") {
            if ($("#corpusbox").length == 0) {
                $("#altr").prepend(
                    '<div class="form-group"><select multiple="" class="form-control scrollbar" id="corpusbox" size="10" >' +
                    '</select></div>'
                );
            }
            $.get('/retrieve/corpus', {
                classification: $('#classfication').html()
            }).done(function(data) {
                corpusLoadback(data, corpus)
            });
        }
        if (this.Alternative != null) {
            $.each(this.Alternative, function() {
                $("#review").append(
                    '<textarea class="form-control scrollbar" rows="3" id="comment' +
                    comment + '">' + this +
                    '</textarea>');
                $("#review").append(
                    '<div class="text-right" ><button type="button" class="btn btn-danger btn-sm outline" id="deletebtn' +
                    comment +
                    '">Delete</button></div>');
                var $btn = $("#submitbtn").detach();
                $("#review").append($btn);
                comment++;
            });
        }
    });
}

$("#review").on("click", "button",
    function() {
        if ($(this).hasClass("float-right")) {
            //if((($.trim($('#comment'+(comment-1)).val())).length)>0 || comment==0){
            $("#review").append(
                '<textarea class="form-control scrollbar" rows="3" id="comment' +
                comment + '"></textarea>');
            $("#review").append(
                '<div class="text-right"><button type="button" class="btn btn-danger btn-sm outline" id="deletebtn' +
                comment +
                '">Delete</button></div>');
            var $btn = $("#submitbtn").detach();
            $("#review").append($btn);
            comment++;
            $('#review_cont').scrollTop($(
                '#review').prop("scrollHeight"));
            //}
            // else {
            //	alert("Please Fill up the Alternative response");
            //}
        } else if ($(this).hasClass(
                "btn-danger")) {
            idNum = (this.id).replace(/[^\d.]/g,
                '');
            comment--;
            $("#comment" + idNum).remove();
            $("#deletebtn" + idNum).remove();
        } else if (this.id == 'submitbtn') {
            var quality;
            var altresp = [];
            $.each($("#review textarea.form-control"),
                function() {
                    if ((($.trim($(this).val())).length) >
                        0) {
                        altresp.push($(this).val());
                    }
                });
            if ($("#QOR1").is(":checked")) {
                quality = 1;
            } else if ($("#QOR2").is(":checked")) {
                quality = 2;
            } else if ($("#QOR3").is(":checked")) {
                quality = 3;
            } else if ($("#QOR4").is(":checked")) {
                quality = 4;
            } else if ($("#QOR5").is(":checked")) {
                quality = 5;
            } else {
                $.alert({
                    title: 'Invalid Response Quality',
                    content: 'Please Select Reponse Quality'
                });
                //                alert("Please Select Response Quality");
                return;
            }
            var selectedquestion = $('#convos').find("div.disabledbutton").attr('id'); //manipulation to get the question from the answer
            selectedquestion = selectedquestion.replace(/[^0-9]/g, '') - 1;
            if (selectedquestion != 0) {
                selectedquestion = "review" + selectedquestion;
                selectedquestion = $('#' + selectedquestion).html();
                selectedquestion = selectedquestion.split('<div');
                selectedquestion = selectedquestion[0].split('/figure>'); //ending result question
            }
            if (($("#classfication").text() != "Select Classification") && (altresp.length !== 0 || $('#corpusbox').val() != null)) {
                $body.addClass("loading");
            }
            $.post(
                '/retrieve/convo/review/info', {
                    _id: iden, //id stored in db
                    convoId: iden + "_" + convoid,
                    quality: quality,
                    explain: $('#explain').val(),
                    alternative: altresp,
                    classification: $('#classfication').html(), //classifcation of question
                    question: selectedquestion[1],
                    answer: $('#corpusbox').val() //answer from corpus
                }).done(function(data) {
                $body.removeClass("loading");
            });
        } else if ($(this).hasClass(
                "dropdown-toggle btn-block")) {
            $("#dropdown-menu").slideDown('fast').show(); //Drop down the subnav on click
            $("#dropdown-menu").slideDown('fast').toggle(); //Drop down the subnav on click
        }
    });

$(document).on('click', '.dropdown-menu li', function() {
    $("#corpusbox").html('');
    $.get('/retrieve/corpus', {
        classification: $(this).html()
    }).done(function(data) {
        corpusCallback(data)
    });
    $("#dropdown-menu").slideDown('fast').hide(); //Drop down the subnav on click
    $('#classfication').html($(this).html());
    //    if ($(this).html() != 'Select Classification'
    if ($("#corpusbox").length == 0) {
        $("#altr").prepend(
            '<div class="form-group"><select multiple="" class="form-control scrollbar" id="corpusbox" size="10" style=" overflow:auto;">' +
            '</select></div>'
        );
    }
});

$(document).on('click', '#verified', function() {
    $('.list-group').html('');
    $.ajax({
        url: "/retrieve",
        async: true,
        success: function(data) {
            chatsCallback(data);
        }
    });
});

function corpusCallback(data) {
    var i = 0;
    $.each(data, function() {
        if (this.length == 1) {
            $("#corpusbox").append(
                '<option>' +
                this +
                '</option>');
        } else {
            $.each(this, function() {
                $("#corpusbox").append(
                    '<option>' +
                    this +
                    '</option>');
            });
        }
    });
}

function corpusLoadback(data, corpus) {
    var i = 0;
    if (corpus != 0) {
        while (i < corpus.length) {
            $.each(data, function() {
                if (this.length == 1) {
                    if (this == corpus[i]) {
                        $("#corpusbox").append(
                            '<option selected="selected">' +
                            this +
                            '</option>');
                        i += 1;
                    } else {
                        $("#corpusbox").append(
                            '<option>' +
                            this +
                            '</option>');
                    }
                } else {
                    $.each(this, function() {
                        if (this == corpus[i]) {
                            $("#corpusbox").append(
                                '<option selected="selected">' +
                                this +
                                '</option>');
                            i += 1;
                        } else {
                            $("#corpusbox").append(
                                '<option>' +
                                this +
                                '</option>');
                        }

                    });
                }
            });
            i++;
        }
    } else {
        $.each(data, function() {
            $("#corpusbox").append(
                '<option>' +
                this +
                '</option>');
        });
    }
}