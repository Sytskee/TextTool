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
    $("#webapp_settings").data(settings);
    $("#webapp_settings").text(event.data);

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
    if (classifier_running) {
        $("a#start_stop").addClass("btn-danger");
        $("a#start_stop").removeClass("btn-success");
        $("a#start_stop").html('<i class="fas fa-stop mr-2"></i>Stop')

        $("#logging").val('')
    }
    else {
        $("a#start_stop").removeClass("btn-danger");
        $("a#start_stop").addClass("btn-success");
        $("a#start_stop").html('<i class="fas fa-play mr-2"></i>Start')
    }
}

$(document).ready(function() {
    $('#container_id').fileTree({ root: '/some/folder/' }, function(file) {
        alert(file);
    });
});
