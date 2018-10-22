import QtQuick 2.6
import QtQuick.Window 2.2
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.0
import QtCharts 2.2

ChartView {
    property real limit: 10
    property string x_format: "%.0f&deg;C"
    property string y_format: "%.0f"
    property string chart_color: "#00bfff"
    property string series_name: "Series"
    property var chart_opacity: 1

    property real min_: 0
    property real max_: 0
    property real val_min: -100000
    property real val_max: 0
    property real x_tick_count: 1


    function append(x, y) {
        if(data1.count >= limit) {
            data1.remove(0)
            val_min = data1.at(0).y
            val_max = data1.at(0).y
            for(var i = 1; i < data1.count; i++) {
                var item = data1.at(i)
                val_min = Math.min(val_min, item.y)
                val_max = Math.max(val_max, item.y + 1)
            }
            min_ += 1
        } else {
            x_tick_count = data1.count
        }
        if(val_min == -100000) {
            val_min = y
        } else {
            val_min = Math.min(val_min, y)
        }
        val_max = Math.max(val_max, y + 1)
        if(x > 0) {
            max_ += 1
        }
        data1.append(x, y)
    }


    width: width
    height: height
    title: title
    legend.alignment: Qt.AlignBottom
    antialiasing: true

    ValueAxis {
        id: valueAxis
        min: min_
        max: max_
        tickCount: x_tick_count
        labelFormat: y_format
    }

    ValueAxis {
        id: temperature1
        min: val_min
        max: val_max
        labelFormat: x_format
    }

    AreaSeries {
        name: series_name
        axisX: valueAxis
        axisY: temperature1
        opacity: chart_opacity
        color: chart_color
        
        upperSeries:LineSeries {
            id: data1
            pointsVisible: true
        }
    }
}
