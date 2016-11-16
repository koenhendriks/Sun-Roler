$(function () {
    Highcharts.chart('temperature-chart', {
        chart: {
            type: 'area',
            width: 320,
            height: 200
        },
        title: {
            text: ''
        },
        xAxis: {
            categories: ['1479305312', '1479305372', '1479305432', '1479305492', '1479305552', '1479305612', '1479305672'],
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
            data: [20, 21, 20, 18, 19]
        }]
    });
});