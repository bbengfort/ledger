/*
 balance.js

 Controller and helper for balance sheet javascripts.
*/

_.templateSettings.variable = "rc";

$(document).ready(function() {

  // Add the click event for any table row
  $('[data-toggle="balance"]').click(function(e) {
    row = $(this);
    modalId = row.data("target");
    endpoint = row.data("url");

    // Fetch the data from the endpoint
    $.get(endpoint)
      .done(function (data) {
        showBalanceModal(modalId, data);
      })
      .fail(function(jqXHR, textStatus, errorThrown) {
        console.log(textStatus, errorThrown);
      });
  });

  function showBalanceModal(modalId, data) {
    // Add the title to the modal
    $("#balanceModalLabel").html(data.account)

    // Create the template from the script body
    var template = _.template(
        $( "script#balanceModalBody" ).html()
    );

    // Ensure the amount format closure is created and execute template
    data.amountfmt = accounting_amount(data.currency);
    $("#balanceModal .modal-body").html(template(data));

    // Show the modal when complete
    $(modalId).modal()
  }

  // Amount formatting
  var amount = new Intl.NumberFormat('en-US', {
    style: 'decimal',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });

  // Returns the HTML for an accounting amount
  function accounting_amount(currency) {
    return function(value) {
      var data = {currency: currency};

      if (value < 0) {
        data.ams = "(" + amount.format(value * -1) + ")";
      } else if (value == 0) {
        data.ams = "&mdash;";
      } else {
        data.ams = amount.format(value);
      }

      var template = _.template(
        '<span class="pull-left"><%= rc.currency %></span>'
        + '<span class="pull-right"><%= rc.ams %></span>'
        + '<div class="clearfix"></div>'
      );

      return template(data);
    }
  }


});
