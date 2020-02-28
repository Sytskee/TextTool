// Socket for streaming the log messages during execution
var loggingWebSocket = new WebSocket("ws://localhost:8888/api/v1/logging");

// Socket for sending and receiving settings
var settingsWebSocket = new WebSocket("ws://localhost:8888/api/v1/settings");

var settings = {}
var USER_SETTINGS = "user";
var PROGRAM_SETTINGS = "program";
var CLASSIFIER_SETTINGS = "classifier";

settingsWebSocket.onopen = function(event) {
    $("a#start_stop").removeClass("disabled");
};

settingsWebSocket.onclose = function(event) {
    $("a#start_stop").addClass("disabled");
};

loggingWebSocket.onmessage = function(event) {
    addLogToTextArea(event.data);
};

function addLogToTextArea(log) {
    var loggingTextArea = $("#logging");
    loggingTextArea.val(loggingTextArea.val() + log);
    loggingTextArea.scrollTop(loggingTextArea[0].scrollHeight);
}

settingsWebSocket.onmessage = function(event) {
    settings = JSON.parse(event.data);

    $("#webapp_settings").text(event.data);

    setInputs();
    setStartStopButton();

    var select_language = $("select#language");

    settings[PROGRAM_SETTINGS]["language_options"].forEach(function(value, index) {
        if (value == settings[USER_SETTINGS]["language"]) {
            var selected = " selected='selected'";
        } else {
            var selected = "";
        }

        select_language.append(`<option value="${value}"${selected}>${value}</option>`);
    });

    var ngrams = $("select#text__vect__ngram_range > optgroup[label='N-grams']");
    var multigrams = $("select#text__vect__ngram_range > optgroup[label='N-multigrams']");

    settings[PROGRAM_SETTINGS]["text__vect__ngram_range_options"].forEach(function(option_value, index) {
        var selected = "";

        for (var value of settings[CLASSIFIER_SETTINGS]["text__vect__ngram_range"]) {
            if (value.toString() == option_value.toString()) {
                selected = " selected='selected'";
                break;
            }
        }

        var option = `<option value="${option_value}"${selected}>(${option_value})</option>`;

        if (option_value[0] == option_value[1]) {
            ngrams.append(option);
        } else {
            multigrams.append(option);
        }
    });
};

function setInputs() {
    $("input[data-settings-category], select[data-settings-category]").each(function(index, element) {
        element = $(element)
        var settingsValue = settings[element.data("settingsCategory")][element.attr("id")];

        if (element.attr("type") == "checkbox") {
            element.prop("checked", settingsValue);
        } else if (element.data("type") != null && element.data("type").startsWith("array")) {
            element.val(settingsValue.toString());
        } else {
            element.val(settingsValue);
        }
    });
}

function handleStartStopClick(event) {
    settings[PROGRAM_SETTINGS]["classifier_running"] = !settings[PROGRAM_SETTINGS]["classifier_running"]

    settings_to_send = {}
    settings_to_send[PROGRAM_SETTINGS] = {"classifier_running": settings[PROGRAM_SETTINGS]["classifier_running"]}
    settingsWebSocket.send(JSON.stringify(settings_to_send));
}

function setStartStopButton(classifier_running) {
    var start_stop = $("a#start_stop");

    if (settings[start_stop.data("settingsCategory")]["classifier_running"]) {
        start_stop
            .addClass("btn-danger")
            .removeClass("btn-success");
        start_stop.children("i")
            .addClass("fa-stop")
            .removeClass("fa-play");

        start_stop.children("span").text("Stop");
        $("#logging").val("");
        $("div.modal").find("form input, form select").prop("disabled", true);
    }
    else {
        start_stop
            .addClass("btn-success")
            .removeClass("btn-danger");
        start_stop.children("i")
            .addClass("fa-play")
            .removeClass("fa-stop");

        start_stop.children("span").text("Start");
        $("div.modal").find("form input, form select").prop("disabled", false);
    }
}

$("#portfolioTrain input, #portfolioTrain select").change(function() {
    updateModelButtons($(this).closest("div.modal"));
});

function updateModelButtons(modal) {
    var dataChanged = false;

    modal.find("input:not([readonly]), select:not([readonly])").each(function(index, element) {
        element = $(element);

        if (element.attr("type") == "checkbox") {
            var inputValue = element.prop("checked");
        } else {
            var inputValue = convertToCorrectType(element.val(), element.data("type"));
        }

        var settingsValue = settings[element.data("settingsCategory")][element.attr("id")];


        if ($.isArray(settingsValue)) {
            if (JSON.stringify(inputValue) != JSON.stringify(settingsValue)) {
                dataChanged = true;
                return false; // break 'each()' loop
            }
        } else if (inputValue != settingsValue) {
            dataChanged = true;
            return false; // break 'each()' loop
        }
    });

    if (dataChanged) {
        modal.find("button.apply")
            .removeClass("disabled")
            .prop("disabled", false);
    } else {
        modal.find("button.apply")
            .addClass("disabled")
            .prop("disabled", true);
    }
}

function saveSettings(event) {
    var modal = $(event).closest("div.modal");
    var changedSettings = {};

    modal.find("input:not([readonly]), select:not([readonly])").each(function(index, element) {
        element = $(element);

        if (element.attr("type") == "checkbox") {
            var inputValue = element.prop("checked");
        } else {
            var inputValue = convertToCorrectType(element.val(), element.data("type"));
        }

        if (inputValue == null) {
            // Reset faulty value
            inputValue = settingsValue;
        }

        var settingsCategory = element.data("settingsCategory");
        var settingsValue = settings[settingsCategory][element.attr("id")];

        if (inputValue != settingsValue) {
            if (! (settingsCategory in changedSettings)) {
                changedSettings[settingsCategory] = {}
            }

            changedSettings[settingsCategory][element.attr("id")] = inputValue;
            settings[settingsCategory][element.attr("id")] = inputValue;
        }
    });

    if (! $.isEmptyObject(changedSettings)) {
        settingsWebSocket.send(JSON.stringify(changedSettings));

        if ($(event).data("dismiss") == "modal") {
            modal.modal('hide'); // Hide manually because hide via 'data-dismiss' does not work after disabling button
        }

        updateModelButtons(modal);
    }
}

function convertToCorrectType(new_value, dataType) {
    if (dataType == null) {
        return new_value;
    }

    var dataTypes = dataType.split("_", 2);

    if (dataTypes[0] == "array") {
        var new_values = new_value.split(",");
        var new_array = [];

        new_values.forEach(function(value, index) {
            converted_value = convertToCorrectType(value, dataTypes[1]);

            if (converted_value == null) {
                new_array = null;
                return;
            }

            new_array.push(converted_value);
        });

        return new_array;
    } else if (dataTypes[0] == "number") {
        var number = Number(new_value);
        if (Number.isNaN(number)) {
            addLogToTextArea("Expected a number but got '" + new_value + "'\r\n");
            return null;
        } else {
            return number;
        }
    } else if (dataTypes[0] == "boolean") {
        return new_value == "true";
    } else if (dataTypes[0] == "tuples") {
        var new_array = [];

        for (element of new_value) {
            var tuple = element.split(",");

            for (index in tuple) {
                tuple[index] = convertToCorrectType(tuple[index], dataTypes[1]);
            }

            new_array.push(tuple)
        }

        return new_array;
    }

    return new_value;
}

function discardSettings(event) {
    setInputs(settings[USER_SETTINGS]);
    setInputs(settings[PROGRAM_SETTINGS]);
    updateModelButtons($(event).closest("div.modal"));
}
