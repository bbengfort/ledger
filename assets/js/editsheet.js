/*
 editsheet.js

 Controller and helper for balance sheet editing javascripts.
*/

_.templateSettings.variable = "rc";

$(document).ready(function () {
    // Compile the alert message template from the embedded script
    var alertTemplate = _.template($("script#alertMessage").html());

    var paymentsForm = $("#paymentsForm");
    var transactionForm = $("#transactionForm");
    var balanceForm = $("#balanceForm");

    // Transaction and Balance handlers
    transactionForm.submit(createNestedResource("transaction"));
    balanceForm.submit(createNestedResource("balance"));

    // Create nested resources
    function createNestedResource(rtype) {
        return function(e) {
            e.preventDefault();
            var form = $(e.target);
            var url = form.attr("action");
            var data = serializeData(form);

            $.post(url, data)
                .fail(onAPIError)
                .done(function(data) {
                    form[0].reset();
                    msg = rtype + " id " + data["id"] + " successfully created";
                    alertMessage("alert-success", rtype + " created", msg);
                });

            console.log(url);
            return false;
        }
    }

    // Payment Handlers
    // Fetch the transaction for the payment, populate the transactions form
    // and redirect user to the trnasactions tab to add the new transaction.
    paymentsForm.submit(function(e) {
        e.preventDefault();
        var url = serializeData(paymentsForm)["payment"];
        if (!url) {
            alertMessage("alert-danger", "could not create payment", "please select a payment first!")
            return false;
        }

        // Get the transaction from the payment and populate the transaction form.
        url = url + "transaction/"
        $.get(url)
            .fail(onAPIError)
            .done(function(data) {
                // Clear current form details
                transactionForm[0].reset();

                // Populate the transaction form
                _.each(data, function(val, key) {
                    console.log(key, val);
                    if (key == "credit" || key == "debit") {
                        var input = $("select[name='" + key + "']");
                        var url = new URL(val['url']);
                        input.val(url.pathname);
                    } else {
                        var input = $("input[name='" + key + "']");
                        if (input.attr("type") == "checkbox") {
                            input.attr("checked", val);
                        } else {
                            input.val(val);
                        }
                    }
                });

                // Send user to the transaction form
                $("#editTabs a[href='#transaction']").tab("show");
            });

        return false;
    });

    // Adds an alert message to the alert div.
    function alertMessage(context, status, message) {
        var elem = $(alertTemplate({status: status, message: message}));
        elem.addClass(context);
        $("#alertMessages").append(elem);
        setTimeout(function () { elem.alert('close'); }, 2000);
    }

    // Helper function to serialize the data in the specified form to a
    // JSON object (using serialize array). I often forget the second
    // argument in the reduce call, which leads to hard to debug errors.
    function serializeData(form) {
        return form.serializeArray().reduce(function(obj, item) {
            obj[item.name] = item.value;
            return obj;
        }, {});
    }

    // Helper function to handle errors during API requests
    function onAPIError(jqXHR, textStatus, errorThrown) {
        if (jqXHR.responseText) {
            // Ensure that the error response can be debugged.
            console.log(jqXHR.responseText);
            var data = JSON.parse(jqXHR.responseText);

            if (_.isArray(data)) {
                // TODO: what if there are more than one error messages?
                alertMessage("alert-danger", "error", data[0]);
            } else {
                _.each(data, function(val, key) {
                    alertMessage("alert-danger", key, val);
                });
            }
        } else {
            // Fallback: just alert the HTTP error
            alertMessage("alert-danger", textStatus, errorThrown);
        }
    }

});
