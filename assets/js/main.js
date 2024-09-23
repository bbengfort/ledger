/*
 * main.js
 * Main entry point for the ledger application
 */

$(document).ready(function() {
  App.init(); // Initialize the Beagle App

  // Bind the logout action
  $(".logout").click(function(e) {
    e.preventDefault();
    $("#logoutForm").submit();
    return false;
  });

  // Fetch the version info from the API
  $.get("/api/status/")
    .done(function(data) {
      if (data.status == "ok") {
        $("#statusLightInfo").addClass("text-success");
      } else {
        $("#statusLightInfo").addClass("text-danger");
      }
      $("#versionInfo").text(data.version);
      $("#revisionInfo").text(data.revision);

      console.log(data);
    })
    .fail(function(data) {
      $("#statusLightInfo").addClass("text-danger");
      console.log(data);
    });
});