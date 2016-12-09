/**
 * Created by clemensk on 07.12.16.
 */
// smaller points if the data array is too big
function set_linewidth(graph, data) {
    var range = graph.xAxisRange();
    var data_points = 0
    for (var i = 0; i < data.length; i++) {
        var x = data[i][0];
        //if (x > minDate && x < maxDate)
        if (x > range[0] && x < range[1])
            data_points++;
    }
    var new_opts = {};
    if (data_points > 2000) {
        new_opts.pointSize = 0.5;
        new_opts.strokeWidth = 0.33;
    }
    else if (data_points > 900) {
        new_opts.pointSize = 1;
        new_opts.strokeWidth = 0.5;
    } else {
        new_opts.pointSize = 1.5;
        new_opts.strokeWidth = 1.;
    }
    graph.updateOptions(new_opts);
}
function updateGraph(data, graph, items) {
    data.push(items);
    graph.updateOptions({'file': data});
}

function setupRefresh(url, graphs, options) {
    window.intervalId = setInterval(function () {
        $.post(url, function (data) {
            var date = new Date(JSON.parse(data.date) * 1000.);
            if (date > graphs["graph_cpu"].data[graphs["graph_cpu"].data.length - 1][0]) {
                for (var id in graphs) {
                    var graph = graphs[id];
                    var list = [date];
                    for (var i in graph.keywords) {
                        list.push(JSON.parse(data[graph.keywords[i]] / graph.factors[i]))
                    }
                    updateGraph(graph.data, graph.graph, list);
                }
                $("#server_table").replaceWith(data.table_html);
            }
        });
    }, options.update_period);
    window.intervalId = setInterval(function () {
        $.post("{% url 'monitcollector.views.load_system_table' server.id %}", function (data) {
            $("#server_table").replaceWith(data.table_html);
        });
    }, 2000);
}
function createGraph(dates, graph, elementID, options) {
    for (var i = 0; i < dates.length; i++) {
        var list = [new Date(dates[i] * 1000.)];
        for (var j = 0; j <graph.values.length; j++) {
            list.push(graph.values[j][i] / graph.factors[j])
        }
        graph.data.push(list);
    }
    graph.graph = new Dygraph(document.getElementById(elementID), graph.data,
        {
            legend: 'always', // show always
            labelsDivWidth: '140', // default 250
            labelsSeparateLines: true,
            ylabel: graph.labels.ylabel,
            xlabel: 'Time',
            drawPoints: true,
            pointSize: options.point_size,
            strokeWidth: options.stroke_width,
            //showRoller: true,  // for a rolling average over values
            labels: graph.labels.labels,
            axisLabelColor: '#CCC',
            axisLineColor: '#CCC',
            colors: ["#7FDD00", "#00FFFF", "#DAA520", "#008080"],
            zoomCallback: function () { // (minDate, maxDate)
                set_linewidth(graph.graph, graph.data);
            }
        });
    set_linewidth(graph.graph, graph.data);
    return graph;
}
function createGraphs(graphs, dates, options) {
    for (var id in graphs){
            createGraph(dates, graphs[id], id, options);
        }
    return graphs;
}
