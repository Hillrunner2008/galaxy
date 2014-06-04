define(['plugin/charts/highcharts/common/config'], function(config) {

return $.extend(true, {}, config, {
    title       : 'Stacked horizontal',
    category    : 'Bar diagrams',
    keywords    : 'default highcharts',
    settings    : {
        x_axis_type : {
            init : 'hide'
        }
    },
    columns     : {
        x : {
            title       : 'Values for x-axis',
            is_label    : true,
            is_auto     : true
        },
        y : {
            title       : 'Values for y-axis',
            is_numeric  : true
        }
    }
});

});