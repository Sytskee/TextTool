// Socket for streaming the log messages during execution
var loggingWebSocket = new WebSocket("ws://localhost:8888/api/v1/logging");

loggingWebSocket.onopen = function(event) {
    $("a#start_stop").removeClass("disabled");
};

loggingWebSocket.onclose = function(event) {
    $("a#start_stop").addClass("disabled");
};

loggingWebSocket.onmessage = function(event) {
    var loggingTextArea = $("#logging");
    loggingTextArea.val(loggingTextArea.val() + event.data)
    loggingTextArea.scrollTop(loggingTextArea[0].scrollHeight)
};

// Socket for sending and receiving settings
var settingsWebSocket = new WebSocket("ws://localhost:8888/api/v1/settings");

settingsWebSocket.onmessage = function (event) {
    var settings = JSON.parse(event.data);
    localStorage.setItem('settings', event.data);

    $("#webapp_settings").data(settings);
    $("#webapp_settings").text(event.data);

    Object.keys(settings).forEach(function(key) {
        var input = $("input#" + key)
        if (input.attr("type") == "checkbox") {
            input.prop("checked", settings[key])
        } else {
            input.val(settings[key])
        }
    })

    setStartStopButton($("#webapp_settings").data("classifier_running"));
};

$("a#start_stop").click(handleStartStopClick)

function handleStartStopClick(event) {
    var classifier_running = $("#webapp_settings").data("classifier_running");

    if (event != null) {
        // Triggered by button click
        classifier_running = !classifier_running
        $("#webapp_settings").data("classifier_running", classifier_running);
        settingsWebSocket.send(JSON.stringify({"classifier_running": classifier_running}));
    }
}

function setStartStopButton(classifier_running) {
    var start_stop = $("a#start_stop")

    if (classifier_running) {
        start_stop
            .addClass("btn-danger")
            .removeClass("btn-success")
        start_stop.children("i")
            .addClass("fa-stop")
            .removeClass("fa-play")

        start_stop.children("span").text("Stop")
        //start_stop.html("<i class='fas fa-stop mr-2'></i>Stop")

        $("#logging").val("")
    }
    else {
        start_stop
            .addClass("btn-success")
            .removeClass("btn-danger")
        start_stop.children("i")
            .addClass("fa-play")
            .removeClass("fa-stop")

        start_stop.children("span").text("Start")
        //start_stop.html("<i class="fas fa-play mr-2"></i>Start")
    }
}

$(document).ready(function() {
    $("#container_id").fileTree({ root: "/some/folder/" }, function(file) {
        alert(file);
    });
});

$("div.portfolio-modal input").change(function() {
    var dataChanged = false

    $("div.portfolio-modal input").each(function() {
        if ($(this).attr("type") == "checkbox") {
            var inputValue = $(this).prop("checked")
        } else {
            var inputValue = $(this).val()
        }

        var settings = JSON.parse(localStorage.getItem("settings"))
        var settingsValue = settings[$(this).attr("id")]

        if (inputValue != settingsValue) {
            dataChanged = true
            return false // break 'each()' loop
        }
    })

    if (dataChanged) {
        $(this).closest("form").siblings("button.apply").removeClass("disabled");
    } else {
        $(this).closest("form").siblings("button.apply").addClass("disabled");
    }
}); 
