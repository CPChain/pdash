import QtQuick 2.6
import QtQuick.Window 2.2
import QtQuick.Layouts 1.11
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Controls 2.4
import QtCharts 2.2

import "../cpchain" as CPC

Rectangle {
    id: preview
    width: 650
    height: 480

    property real min_: 0
    property real max_: 0

    property real val_min: 0
    property real val_max: 0
    property real x_tick_count: 1
    
    property int x_pos: 0
    Connections {
        target: self
        onTickComing: {
            // Raw Data
            raw.tick(tick)
            // Find Temperature
            var temperature = parseInt(tick.match(/temperature:(\d+)/)[1])
            // Find Huminity
            var huminity = parseInt(tick.match(/huminity:(\d+)/)[1])
            console.log(temperature, huminity)
            chart.append(x_pos, temperature)
            chart2.append(x_pos, huminity)
            x_pos += 1
        }
    }
    
    

    ColumnLayout {
        spacing: 10
        id: content
        TabBar {
            id: bar
            spacing: 0
            TabButton {
                width: 100
                Rectangle {
                    anchors.fill: parent
                    color: ( !parent.checked ? "white" : "black" )
                    border.color: "black"

                    Text {
                        anchors.centerIn: parent
                        text: qsTr("Visualization")
                        color: ( !parent.parent.checked ? "black" : "white" )
                    }
                }
            }
            TabButton {
                width: 100
                Rectangle {
                    anchors.fill: parent
                    color: ( !parent.checked ? "white" : "black" )
                    border.color: "black"

                    Text {
                        anchors.centerIn: parent
                        text: qsTr("Raw")
                        color: ( !parent.parent.checked ? "black" : "white" )
                    }
                }
            }
        }

        StackLayout {
            width: parent.width
            currentIndex: bar.currentIndex
            Item {
                id: vtab
                width: preview.width
                height: preview.height - bar.height
                Flickable {
                    anchors.fill: parent
                    contentWidth: 600
                    contentHeight: 900

                    ScrollBar.vertical: ScrollBar { }
                    ColumnLayout {
                        id: test
                        CPC.AreaChart {
                            id: chart
                            width: 600
                            height: 380
                            chart_color: "#00ffff"
                            chart_opacity: 0.6
                            title: "Temperature Data"
                            series_name: "Temperature"
                        }
                        CPC.AreaChart {
                            id: chart2
                            width: 600
                            height: 380
                            chart_color: "#8a2be2"
                            chart_opacity: 0.6
                            title: "Huminity Data "
                            series_name: "Huminity"
                            x_format: "%.0f%"
                        }

                        property int year: 0
                        function testAdd() {
                            var val = Math.round(Math.random() * 20)
                            chart.append(year, val)
                            chart2.append(year, val)
                            year += 1
                        }

                        Timer {
                            interval: 1000; running: true; repeat: true
                            // onTriggered: test.testAdd()
                        }
                    }
                }
            }
            Item {
                id: rawTab
                CPC.Raw {
                    id: raw
                    width: preview.width
                    height: preview.height - bar.height
                }
                property int num: 0
                function testAdd() {
                    var val = Math.round(Math.random() * 20)
                    raw.tick("data item - " + num)
                    num += 1
                }

                Timer {
                    interval: 1000;
                    running: true;
                    repeat: true
                    // onTriggered: rawTab.testAdd()
                }
            }
        }
    }
}