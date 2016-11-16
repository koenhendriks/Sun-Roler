var lightChart;
$(function () {
    lightChart = Highcharts.chart('light-chart', {
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
            min: 100,
            title: {
                text: 'lx',
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
                return this.y + 'lx'
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