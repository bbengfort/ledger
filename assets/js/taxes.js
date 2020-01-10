/*
 taxes.js

 Controller and helper for taxes javascripts.
*/

_.templateSettings.variable = "rc";

$(document).ready(function () {

  var taxesWidget = $("#taxes-bar-chart-widget");

  function refreshTaxesBarChart() {
    taxesWidget.addClass('be-loading-active');
    $.get("/api/returns/")
      .done(function (data) {
        taxReturnChart(data);
        taxesWidget.removeClass('be-loading-active');
      })
      .fail(function (jqXHR, textStatus, errorThrown) {
        // TODO: add alert to the UI
        console.log(textStatus, errorThrown)
        taxesWidget.removeClass('be-loading-active');
      })
  }

  // Fetch the tax-return data to draw the bar chart.
  refreshTaxesBarChart()

  // Refresh tax-return data and redraw barchart on refresh button click
  $('#refresh-taxes-bar-chart').on('click', refreshTaxesBarChart);


  function taxReturnChart(data) {
    // Data is expected to be ordered by year descending
    data.reverse();

    // Set the chart colors
    var color1 = tinycolor(App.color.primary);
    var color2 = tinycolor(App.color.success);

    // Get the canvas element
    var ctx = document.getElementById("taxes-bar-chart");
    var data = {
      labels: _.pluck(data, "year"),
      datasets: [{
        label: "Income",
        borderColor: color1.toString(),
        backgroundColor: color1.setAlpha(.8).toString(),
        data: _.map(_.pluck(data, "income"), parseFloat)
      }, {
        label: "AGI",
        borderColor: color2.toString(),
        backgroundColor: color2.setAlpha(.8).toString(),
        data: _.map(_.pluck(data, "agi"), parseFloat)
      }]
    };

    var bar = new Chart(ctx, {
      type: 'bar',
      data: data,
      options: {
        aspectRatio: 2,
        elements: {
          rectangle: {
            borderWidth: 2,
            borderColor: 'rgb(0, 255, 0)',
            borderSkipped: 'bottom'
          }
        },
        tooltips: {
          callbacks: {
            label: function (tooltipItem, data) {
              return tooltipItem.yLabel.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
            }
          }
        }
      }
    });
  }
});