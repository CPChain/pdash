import QtQuick 2.6
import QtQuick.Window 2.2
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.0
import QtCharts 2.2

ChartView {
    property var is_first: true
    property real limit: 10
    property string x_format: "%.0f&deg;C"
    property string y_format: "%.0f"
    property string chart_color: "#00bfff"
    property string series_name: "Series"
    property var chart_opacity: 1

    property var min_: new Date()
    // property var max_: new Date(2018, 11, 1, 18, 07, 0)
    property var max_ : new Date()
    property real val_min: 0
    property real val_max: 30
    property real x_tick_count: 1

    function append(x, y) {
        if(is_first) {
            is_first = false
            min_ = x
        }
        if(data1.count >= limit) {
            data1.remove(0)
            min_ = new Date(data1.at(0).x)
            for(var i = 1; i < data1.count; i++) {
                var item = data1.at(i)
                val_max = Math.max(val_max, item.y + 1)
            }
        } else {
            x_tick_count = data1.count
        }
        val_max = Math.max(val_max, y + 1)
        max_ = x
        console.log(x.getTime())
        data1.append(x.getTime(), y)
    }


    width: width
    height: height
    title: title
    legend.alignment: Qt.AlignBottom
    antialiasing: true

    AreaSeries {
        name: series_name
        axisX: DateTimeAxis {
            format: "mm:ss"
            tickCount: 5
            min: min_
            max: max_
        }
        axisY: ValueAxis {
            min: val_min
            max: val_max
            labelFormat: x_format
        }
        opacity: chart_opacity
        color: chart_color
        
        upperSeries:LineSeries {
            id: data1
            pointsVisible: true
        }
    }
}
