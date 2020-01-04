function init_ratings_chart(values) {

  var colors = [];

  $.each(values, function(index, value ) {
    if (value >= 80)
      colors[index] = "green";
    else if (value >= 50)
      colors[index] = "gray";
    else
      colors[index] = "#f64f4f";
  });

  if ($('#ratings-chart').length) {

    var ctx = document.getElementById("ratings-chart");
    var chart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: [["Tests"], ["Cloud reqs"], ["Maintenance"], ["Compliance"]],
        datasets: [{
          barThickness: 50,
          label: 'Rating',
          backgroundColor: colors,
          data: values
        }]
      },
      options: {
        "hover": {
          "animationDuration": 0
        },
        "animation": {
          "duration": 1,
          "onComplete": function() {
            var chartInstance = this.chart,
            ctx = chartInstance.ctx;

            ctx.font = Chart.helpers.fontString(Chart.defaults.global.defaultFontSize,
                                                Chart.defaults.global.defaultFontStyle,
                                                Chart.defaults.global.defaultFontFamily);
            ctx.textAlign = 'center';
            ctx.textBaseline = 'bottom';

            this.data.datasets.forEach(function(dataset, i) {
              var meta = chartInstance.controller.getDatasetMeta(i);
              meta.data.forEach(function(bar, index) {
                var data = dataset.data[index];
                ctx.fillText(data + "%", bar._model.x, bar._model.y - 1);
              });
            });
          }
        },
        tooltips: { "enabled": false },
        legend: { display: false },
        scales: {
          yAxes: [{
//          display: false,
            gridLines: {
//            display: false
            },
            ticks: {
              max: 125,
              stepSize: 25,
            display: false,
              beginAtZero: true
            }
          }],
          xAxes: [{
            gridLines: {
              display: false
            },
            ticks: {
              beginAtZero: true
            }
          }]
        } 
      }
    });
  }
}
init_ratings_chart([55, 44, 23, 100]);
