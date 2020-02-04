/*
 overview.js

 Controller and helper for overview javascripts.
*/

_.templateSettings.variable = "rc";

$(document).ready(function () {
  // Bind the create sheet form to its handler
  $("form.create-sheet").submit(createBalanceSheet);

  var cashFlowWidget = $("#cashflow-bar-chart-widget");

  function refreshCashFlowChart() {
    cashFlowWidget.addClass('be-loading-active');
    $.get("/api/cashflow/")
      .done(function (data) {
        cashFlowChart(data.reverse());
        cashFlowWidget.removeClass('be-loading-active');
      })
      .fail(function (jqXHR, textStatus, errorThrown) {
        // TODO: add alert to the UI
        console.log(textStatus, errorThrown);
        cashFlowWidget.removeClass('be-loading-active');
      });
  }

  // Fetch the cash-flow data to draw the chart
  refreshCashFlowChart();

  // Refresh tax-return data and redraw barchart on refresh button click
  $('#refresh-cashflow-bar-chart').on('click', refreshCashFlowChart);

  function cashFlowChart(data) {
    // Set the chart colors
    var cRed = tinycolor(App.color.danger);
    var cGreen = tinycolor(App.color.success);

    var ctx = document.getElementById('cashvdebt').getContext('2d');
    var labels = _.map(_.pluck(data, "date"), fmtDate);

    new Chart(ctx, {
      // The type of chart we want to create
      type: 'bar',

      // The data for our dataset
      data: {
        labels: labels,
        datasets: [{
          label: "Net Cash",
          data: _.pluck(data, "net_ending"),
          type: "line",
          borderColor: "#333333",
          fill: false,
        }, {
          label: "Cash (ending)",
          borderColor: cGreen.toString(),
          backgroundColor: cGreen.setAlpha(.8).toString(),
          data: _.pluck(data, "cash_ending"),
        }, {
          label: "Debt (ending)",
          borderColor: cRed.toString(),
          backgroundColor: cRed.setAlpha(.8).toString(),
          data: _.pluck(data, "debt_ending"),
        }]
      },

      // Configuration options go here
      options: {
        aspectRatio: 1.75,
        legend: {
          display: true,
        },
        scales: {
          xAxes: [{
            stacked: true
          }],
          yAxes: [{
            stacked: true
          }]
        },
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
      },
    });
  }

  function fmtDate(s) {
    // Don't forget to subtract 1 from the month?!
    const [year, month, day] = s.split("-")
    return new Date(year, month - 1, day).toLocaleDateString("en-US", { "month": "short", "year": "numeric" });
  }

  function createBalanceSheet(e) {
    e.preventDefault();
    var form = $(e.target);

    // Disable the submit button
    form.find(":submit").attr("disabled", true)

    // Get the data from the form and post it
    // Note that reduce requires the empty object as a second argument
    var data = form.serializeArray().reduce(function (obj, item) {
      obj[item.name] = item.value;
      return obj;
    }, {});

    console.log(data);

    $.post(form.attr("action"), data)
      .done(function (data) {
        window.location.href = data["href"];
      })
      .fail(function (jqXHR, textStatus, errorThrown) {
        console.log(textStatus, errorThrown);
        console.log(jqXHR.responseText);

        form.find(":submit")
          .removeClass("btn-success")
          .addClass("btn-danger")
          .text(errorThrown);
      });

    // prevent form from submitting
    return false;
  }

  var investmentsWidget = $("#investments-line-chart-widget");

  function refreshInvestmentsChart() {
    investmentsWidget.addClass('be-loading-active');
    $.get("/api/investments/")
      .done(function (data) {
        investmentsChart(data.reverse());
        investmentsWidget.removeClass('be-loading-active');
      })
      .fail(function (jqXHR, textStatus, errorThrown) {
        // TODO: add alert to the UI
        console.log(textStatus, errorThrown);
        investmentsWidget.removeClass('be-loading-active');
      });
  }

  // Fetch the cash-flow data to draw the chart
  refreshInvestmentsChart();

  // Refresh tax-return data and redraw barchart on refresh button click
  $('#refresh-investments-line-chart').on('click', refreshInvestmentsChart);

  function investmentsChart(data) {
    // Set the chart colors
    var color = tinycolor(App.color.primary);

    var ctx = document.getElementById('investments').getContext('2d');

    new Chart(ctx, {
      // The type of chart we want to create
      type: 'line',

      // The data for our dataset
      data: {
        labels: _.pluck(data, "date"),
        datasets: [{
          label: "Ending Balance",
          data: _.pluck(data, "investment"),
          borderColor: color.toString(),
          backgroundColor: color.setAlpha(0.75).toString(),
        }]
      },

      // Configuration options go here
      options: {
        aspectRatio: 1.5,
        legend: {
          display: false,
        },
        tooltips: {
          position: 'average',
          callbacks: {
            label: function (tooltipItem, data) {
              return tooltipItem.yLabel.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
            }
          }
        }
      },
    });
  }

  // Top tile widgets
  function sparklines() {
    var color1 = tinycolor(App.color.primary);
    var color2 = tinycolor(App.color.warning);
    var color3 = tinycolor(App.color.success);

    $.get("/api/creditscore/")
      .done(function(data) {
        $("#creditScoreSpark").sparkline(_.pluck(data, "score").reverse(), {
          width: '85',
          height: '35',
          lineColor: color2.toString(),
          highlightSpotColor: color2.toString(),
          highlightLineColor: color2.toString(),
          fillColor: color2.setAlpha(0.5).toString(),
          spotColor: false,
          minSpotColor: false,
          maxSpotColor: false,
          lineWidth: 1.15
        });
      })
      .fail(function(jqXHR, textStatus, errorThrown) {
        // TODO: add alert to the UI
        console.log(textStatus, errorThrown);
      })

    $.get("/api/returns/")
      .done(function (data) {
        $("#incomeSpark").sparkline(_.pluck(data, "income").reverse(), {
          type: 'bar',
          width: '85',
          height: '35',
          barWidth: 4,
          barSpacing: 3,
          chartRangeMin: 0,
          barColor: color3
        });
      })
      .fail(function (jqXHR, textStatus, errorThrown) {
        // TODO: add alert to the UI
        console.log(textStatus, errorThrown);
      })

    $.get("/api/savings/")
      .done(function (data) {
        $("#savingsSpark").sparkline(_.pluck(data, "savings").reverse(), {
          type: 'bar',
          width: '85',
          height: '35',
          barWidth: 4,
          barSpacing: 1,
          chartRangeMin: 0,
          barColor: color3
        });
      })
      .fail(function (jqXHR, textStatus, errorThrown) {
        // TODO: add alert to the UI
        console.log(textStatus, errorThrown);
      })

    $.get("/api/investments/")
      .done(function (data) {
        $("#investmentsSpark").sparkline(_.pluck(data, "investment").reverse(), {
          width: '85',
          height: '35',
          lineColor: color1.toString(),
          highlightSpotColor: color1.toString(),
          highlightLineColor: color1.toString(),
          fillColor: color1.setAlpha(0.5).toString(),
          spotColor: false,
          minSpotColor: false,
          maxSpotColor: false,
          lineWidth: 1.15
        });
      })
      .fail(function (jqXHR, textStatus, errorThrown) {
        // TODO: add alert to the UI
        console.log(textStatus, errorThrown);
      })
  }

  sparklines();

});