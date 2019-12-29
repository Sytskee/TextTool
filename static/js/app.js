// Socket for streaming the log messages during execution
var loggingWebSocket = new WebSocket("ws://localhost:8888/api/v1/logging");

// Socket for sending and receiving settings
var settingsWebSocket = new WebSocket("ws://localhost:8888/api/v1/settings");

var settings = {}

loggingWebSocket.onopen = function(event) {
    $("a#start_stop").removeClass("disabled");
};

loggingWebSocket.onclose = function(event) {
    $("a#start_stop").addClass("disabled");
};

loggingWebSocket.onmessage = function(event) {
    var loggingTextArea = $("#logging");
    loggingTextArea.val(loggingTextArea.val() + event.data);
    loggingTextArea.scrollTop(loggingTextArea[0].scrollHeight);
};

settingsWebSocket.onmessage = function(event) {
    settings = JSON.parse(event.data);

    $("#webapp_settings").text(event.data);

    setInputs(settings);
    setStartStopButton(settings["classifier_running"]);

};

function setInputs(keyValues) {
    Object.keys(keyValues).forEach(function(key) {
        var input = $("input#" + key);
        if (input.attr("type") == "checkbox") {
            input.prop("checked", keyValues[key]);
        } else {
            input.val(keyValues[key]);
        }
    });
}

function handleStartStopClick(event) {
    settings["classifier_running"] = !settings["classifier_running"]
    settingsWebSocket.send(JSON.stringify({"classifier_running": settings["classifier_running"]}));
}

function setStartStopButton(classifier_running) {
    var start_stop = $("a#start_stop");

    if (classifier_running) {
        start_stop
            .addClass("btn-danger")
            .removeClass("btn-success");
        start_stop.children("i")
            .addClass("fa-stop")
            .removeClass("fa-play");

        start_stop.children("span").text("Stop");
        $("#logging").val("");
        $("div.modal").find("form").find(":input").attr("disabled", true);
    }
    else {
        start_stop
            .addClass("btn-success")
            .removeClass("btn-danger");
        start_stop.children("i")
            .addClass("fa-play")
            .removeClass("fa-stop");

        start_stop.children("span").text("Start");
        $("div.modal").find("form").find(":input").attr("disabled", false);
    }
}

$("div.portfolio-modal input").change(function() {
    updateModelButtons($(this).closest("div.modal"));
});

function updateModelButtons(modal) {
    var dataChanged = false;

    modal.find("input").each(function() {
        if ($(this).attr("type") == "checkbox") {
            var inputValue = $(this).prop("checked");
        } else {
            var inputValue = $(this).val();
        }

        var settings = JSON.parse(localStorage.getItem("settings"));
        var settingsValue = settings[$(this).attr("id")];

        if (inputValue != settingsValue) {
            dataChanged = true;
            return false; // break 'each()' loop
        }
    });

    if (dataChanged) {
        modal.find("button.apply")
            .removeClass("disabled")
            .attr("disabled", false);
    } else {
        modal.find("button.apply")
            .addClass("disabled")
            .attr("disabled", true);
    }
}

function saveSettings(event) {
    var modal = $(event).closest("div.modal");
    var changedSettings = {};

    modal.find("input").each(function() {
        if ($(this).attr("type") == "checkbox") {
            var inputValue = $(this).prop("checked");
        } else {
            var inputValue = $(this).val();
        }

        var settings = JSON.parse(localStorage.getItem("settings"));
        var settingsValue = settings[$(this).attr("id")];

        if (inputValue != settingsValue) {
            changedSettings[$(this).attr("id")] = inputValue;
        }
    });

    if (! $.isEmptyObject(changedSettings)) {
        settingsWebSocket.send(JSON.stringify(changedSettings));
    }
}

function discardSettings(event) {
    setInputs(settings);
    updateModelButtons($(event).closest("div.modal"));
}
