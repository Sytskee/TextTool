// Socket for streaming the log messages during execution
var loggingWebSocket = new WebSocket("ws://localhost:8888/api/v1/logging");

loggingWebSocket.onopen = function() {
    // loggingWebSocket.send("Hello, world");
};

loggingWebSocket.onmessage = function(evt) {
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
        //$("a#start_stop").removeClass("btn-outline-light");
        $("a#start_stop").removeClass("btn-success");
        $("a#start_stop").html('<i class="fas fa-stop mr-2"></i>Stop')
    }
    else {
        $("a#start_stop").removeClass("btn-danger");
        //$("a#start_stop").addClass("btn-outline-light");
        $("a#start_stop").addClass("btn-success");
        $("a#start_stop").html('<i class="fas fa-play mr-2"></i>Start')
    }
}

$(document).ready(function() {
    $('#container_id').fileTree({ root: '/some/folder/' }, function(file) {
        alert(file);
    });
});