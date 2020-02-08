$(function() {
  // price history chart
  var ctx = document.getElementById('price-history').getContext('2d');
  var priceHistory = new Chart(ctx, {
    type: 'line',
    data: {datasets: price_history},
    options: {
      color: 'white',
      legend: {position: 'bottom'},
      elements: {
        point: {radius: 3, hitRadius: 200, hoverRadius: 3}
      },
      tooltips: {
        callbacks: {label: function(tooltipItem, data) {
          var label = data.datasets[tooltipItem.datasetIndex].label || '';
          if (label) {label += ': ';}
          label += '$' + tooltipItem.yLabel;
          return label;
        }
      }},
      scales: {
        xAxes: [
          {
            type: 'time',
            time: {
              minUnit: 'day',
              displayFormats: {
                day: 'DD-MM-YY',
                week: 'DD-MM-YY',
                month: 'MMM Y',
                quarter: '[Q]Q Y',
                year: 'Y',
              },
              tooltipFormat: 'DD-MM-YY ha Z',
              max: new Date(),
            }
          }
        ],
        yAxes: [{ticks: {
          callback: function(value, index, values) {return '$' + value;}
        }}]
      }
    }
  });
});
