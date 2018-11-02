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

    Connections {
        target: self
        onTickComing: {
            // Raw Data
            raw.tick(tick)
            // Find Temperature
            var temperature = parseInt(tick.match(/temperature:(\d+)/)[1])
            // Find Huminity
            var huminity = parseInt(tick.match(/huminity:(\d+)/)[1])
            // Timestamp
            var splits = tick.split(' ')
            var timestamp = Date.parse(splits[0] + ' ' + splits[1])
            var x = new Date(timestamp)
            chart.append(x, temperature)
            chart2.append(x, huminity)
        }
    }
    
    Flickable {
        anchors.fill: parent
        contentWidth: content_stack.width
        contentHeight: 900

        ScrollBar.vertical: ScrollBar { }
    
        ColumnLayout {
            spacing: 10
            id: content
            TabBar {
                id: bar
                spacing: 0
                anchors.top: parent.top
                anchors.topMargin: 15
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
                id: content_stack
                width: parent.width
                currentIndex: bar.currentIndex
                Item {
                    id: vtab
                    width: preview.width
                    height: preview.height - bar.height
                    ColumnLayout {
                        id: test
                        CPC.AreaChart {
                            id: chart
                            limit: 10
                            width: 600
                            height: 380
                            chart_color: "#00ffff"
                            chart_opacity: 0.6
                            title: "Temperature"
                            series_name: "Temperature"
                        }
                        CPC.AreaChart {
                            id: chart2
                            limit: 10
                            width: 600
                            height: 380
                            chart_color: "#8a2be2"
                            chart_opacity: 0.6
                            title: "Huminity"
                            series_name: "Huminity"
                            x_format: "%.0f%"
                        }
                    }
                }
                Item {
                    id: rawTab
                    anchors.top: parent.top
                    anchors.topMargin: 10
                    CPC.Raw {
                        id: raw
                        width: preview.width
                        height: preview.height - bar.height
                    }
                }
            }
        }
    }
}