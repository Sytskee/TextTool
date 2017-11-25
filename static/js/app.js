// Socket for streaming the log messages during execution
var loggingWebSocket = new WebSocket("ws://localhost:8888/api/v1/logging");

loggingWebSocket.onopen = function() {
    loggingWebSocket.send("Hello, world");
};

loggingWebSocket.onmessage = function (evt) {
    var loggingTextArea = $("#logging");
    loggingTextArea.append(evt.data);
    loggingTextArea.scrollTop(loggingTextArea[0].scrollHeight)
};

// Socket for sending and receiving settings
var settingsWebSocket = new WebSocket("ws://localhost:8888/api/v1/settings");

settingsWebSocket.onmessage = function (evt) {
    var settings = JSON.parse(evt.data);
    $("#webapp_settings").data(settings);
    $("#webapp_settings").text(evt.data);

    handleStartStopClick(null);
};

$("button#start_stop").click(handleStartStopClick)
function handleStartStopClick(event) {
    var classifier_running = $("#webapp_settings").data("classifier_running");

    if (event != null) {
        // Triggered by button click
        classifier_running = !classifier_running
        $("#webapp_settings").data("classifier_running", classifier_running);
        settingsWebSocket.send(JSON.stringify({"classifier_running": classifier_running}));
    }

    if (classifier_running) {
        $("button#start_stop").addClass("btn-danger");
        $("button#start_stop").removeClass("btn-success");
        $("button#start_stop").html("Stop")
    }
    else {
        $("button#start_stop").removeClass("btn-danger");
        $("button#start_stop").addClass("btn-success");
        $("button#start_stop").html("Start")
    }
}

$(document).ready( function() {
    $('#container_id').fileTree({ root: '/some/folder/' }, function(file) {
        alert(file);
    });
});