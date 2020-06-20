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

    if (select_language.html() == "") {
        settings[PROGRAM_SETTINGS]["language_options"].forEach(function(value, index) {
            select_language.append(`<option>${value}</option>`);
        });
    }

    select_language.val(settings[USER_SETTINGS]["language"]);

    var grams_select = $("select#text__vect__ngram_range");
    var ngrams = grams_select.find("optgroup[label='N-grams']");
    var multigrams = grams_select.find("optgroup[label='N-multigrams']");

    if (ngrams.html() == "" && multigrams.html() == "") {
        settings[PROGRAM_SETTINGS]["text__vect__ngram_range_options"].forEach(function(option_value, index) {
            var option = `<option value="${option_value}">(${option_value})</option>`;

            if (option_value[0] == option_value[1]) {
                ngrams.append(option);
            } else {
                multigrams.append(option);
            }
        });
    }

    grams_select.selectpicker("val", settings[CLASSIFIER_SETTINGS]["text__vect__ngram_range"]);

    var select_language = $("select#scoring");

    if (select_language.html() == "") {
        settings[PROGRAM_SETTINGS]["scoring_options"].forEach(function(value, index) {
            select_language.append(`<option>${value}</option>`);
        });
    }

    select_language.selectpicker("val", settings[CLASSIFIER_SETTINGS]["scoring"]);
};

function setInputs() {
    $("input[data-settings-category], select[data-settings-category]").each(function(index, element) {
        element = $(element)
        var settingsValue = settings[element.data("settingsCategory")][element.attr("id")];

        if (element.attr("type") == "checkbox") {
            element.prop("checked", settingsValue);
        } else if (element.hasClass("selectpicker")) {
            if (element.attr("id") == "text__vect__ngram_range" && $.isArray(settingsValue)) {
                var converted_value = settingsValue.map(function(val) {
                    return val.toString();
                });
                element.selectpicker("val", converted_value);
            } else {
                element.selectpicker("val", settingsValue);
            }

        } else if (element.data("type") != null && element.data("type").startsWith("array")) {
            element.val(settingsValue.toString());
        } else {
            element.val(settingsValue);
        }

        if (element.hasClass("selectpicker")) {
            element.selectpicker("render");
        }
    });
}

function handleStartStopClick(event) {
    var whatToStart = $("section#running_section input[name='whatToStart']:checked").val();
    settings[PROGRAM_SETTINGS][whatToStart] = !settings[PROGRAM_SETTINGS][whatToStart]

    settings_to_send = {}
    settings_to_send[PROGRAM_SETTINGS] = {[whatToStart]: settings[PROGRAM_SETTINGS][whatToStart]}
    settingsWebSocket.send(JSON.stringify(settings_to_send));
}

function setStartStopButton() {
    var start_stop = $("a#start_stop");
    var category = start_stop.data("settingsCategory");

    var anyExecutorRunning = settings[category]["executors"].some(executor => settings[category][executor]);

    if (anyExecutorRunning) {
        start_stop
            .addClass("btn-danger")
            .removeClass("btn-success");
        start_stop.children("i")
            .addClass("fa-stop")
            .removeClass("fa-play");

        start_stop.children("span").text("Stop");
        $("#logging").val("");
        $("div.modal").find("form input, form select").prop("disabled", true);
    } else {
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

$("div.portfolio-modal input, div.portfolio-modal select").change(function() {
    updateModelButtons($(this).closest("div.modal"));
});

function updateModelButtons(modal) {
    var dataChanged = false;

    modal.find("input:not([readonly]), select:not([readonly])").each(function(index, element) {
        element = $(element);

        if (element.attr("type") == "checkbox") {
            var inputValue = element.prop("checked");
        } else if (element.hasClass("selectpicker")) {
            var inputValue = convertToCorrectType(element.selectpicker('val'), element.data("type"));
        } else {
            var inputValue = convertToCorrectType(element.val(), element.data("type"));
        }

        var settingsValue = settings[element.data("settingsCategory")][element.attr("id")];

        if (inputValueChanged(settingsValue, inputValue)) {
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
    var currentModal = $(event).closest("div.modal");
    var changedSettings = {};

    currentModal.find("input:not([readonly]), select:not([readonly])").each(function(index, element) {
        element = $(element);

        if (element.attr("type") == "checkbox") {
            var inputValue = element.prop("checked");
        } else {
            var inputValue = convertToCorrectType(element.val(), element.data("type"));
        }

        var settingsCategory = element.data("settingsCategory");
        var settingsValue = settings[settingsCategory][element.attr("id")];

        if (inputValue == null) {
            // Reset faulty value
            inputValue = settingsValue;
        }

        if (inputValueChanged(settingsValue, inputValue)) {
            if (!(settingsCategory in changedSettings)) {
                changedSettings[settingsCategory] = {}
            }

            changedSettings[settingsCategory][element.attr("id")] = inputValue;
            settings[settingsCategory][element.attr("id")] = inputValue;
        }
    });

    if (!$.isEmptyObject(changedSettings)) {
        settingsWebSocket.send(JSON.stringify(changedSettings));

        if ($(event).data("dismiss") == "modal") {
            currentModal.modal('hide'); // Hide manually because hide via 'data-dismiss' does not work after disabling button
        }

        updateModelButtons(currentModal);
    }
}

function inputValueChanged(currentValue, inputValue) {
    if ($.isArray(currentValue)) {
        if (JSON.stringify(inputValue) != JSON.stringify(currentValue)) {
            return true;
        }
    } else if (inputValue != currentValue) {
        return true;
    }

    return false;
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
