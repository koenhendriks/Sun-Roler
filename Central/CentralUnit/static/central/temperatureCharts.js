var temperatureChart;
$(function () {
    temperatureChart = Highcharts.chart('temperature-chart', {
        chart: {
            type: 'area',
            width: 320,
            height: 200
        },
        title: {
            text: ''
        },
        xAxis: {
            categories: [''],
            tickmarkPlacement: 'on',
            title: {
                enabled: false
            }
        },
        yAxis: {
            min: 15,
            title: {
                text: '℃',
                rotation: 0
            },
            labels: {

                formatter: function () {
                    return this.value;
                }
            }
        },
        tooltip: {
            formatter: function () {
                return this.y + '℃'
            }
        },
        plotOptions: {
            area: {
                stacking: 'normal',
                lineColor: '#666666',
                lineWidth: 1,
                marker: {
                    lineWidth: 1,
                    lineColor: '#666666'
                }
            }
        },
        series: [{
            showInLegend: false,
            data: [0]
        }]
    });
});