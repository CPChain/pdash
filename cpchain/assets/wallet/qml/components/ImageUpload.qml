import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.0
import QtQuick.Shapes 1.0
import QtQuick.Dialogs 1.3

import "../cpchain" as CPC


Shape {
    id: uploader
    width: self.width
    height: self.height
    property var radius : 6;
    property var _size: 0
    property var _MAX: 1

    property var gap: self.gap
    property var _radius : radius;
    property var _start_x: 1
    property var _start_y: 1
    property var _width: self.width - 1
    property var _height: self.height - 1

    property var file_path: null

    function to_file_path(filepath) {
        if(Qt.platform.os == "windows"){
                file_path = filepath.slice(8);
        }else{
            file_path = filepath.slice(7);
        }
        var pos = file_path.lastIndexOf('.')
        if(pos >= 0) {
            var suffix = file_path.substr(pos + 1)
            if(suffix) {
                var suffixs = ['jpg', 'jpeg', 'png']
                for(var i in suffixs) {
                    if(suffix.toLowerCase() == suffixs[i]) {
                        self.file = file_path
                        add_image(file_path)
                    }
                }
            }
        }
    }

    ListModel {
        id: images
    }

    function add_image(src) {
        if(_size < _MAX) {
            _size += 1
            images.append({"src": src})
        } else {
            images.set(0, {"src": src})
        }
    }

    DropArea {
        id: dropArea;
        anchors.fill: parent;
        onDropped: {
            to_file_path(drop.text)
        }
    }

    FileDialog {
        id: fileDialog;
        title: qsTr("Please choose a file");
        nameFilters: [
            "*.jpg",
            "*.png"
        ];
        onAccepted: {
            to_file_path(new String(fileUrl));
        }
    }
    
    Rectangle {
        id: target
        anchors.centerIn: parent
        width: parent.width - 20
        height: parent.height - 20
        color: "transparent"

        Flickable {

            anchors.fill: parent
            contentWidth: parent.width
            contentHeight: images_grid.height

            ScrollBar.vertical: ScrollBar { }

            Grid {
                id: images_grid
                columns: 4
                spacing: 7
                Repeater {
                    model: images
                    Rectangle {
                        width: 126
                        height: 79
                        Image {
                            source: src
                            anchors.fill: parent
                        }
                    }
                     

                }
                Rectangle {
                    width: 126
                    height: 79
                    visible: _size < _MAX
                    Row {
                        anchors.centerIn: parent
                        spacing: 10
                        Image {
                            anchors.verticalCenter: parent.verticalCenter
                            source: self.icon
                            width: 36
                            height: 35
                        }
                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            text: ".jpg/png"
                            color: "#bbbbbb"
                        }

                    }
                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor

                        onClicked: function(e) {
                            if(_size < _MAX) {
                                fileDialog.open()
                            }
                        }
                    }
                }
            }
        }
    }
    
    

    ShapePath {
        visible: _size < _MAX
        strokeWidth: 1
        strokeColor: self.background
        fillColor: self.background
        strokeStyle: ShapePath.DashLine
        startX: 0
        startY: 0
        PathLine { x: _width + gap + 1; y: 0 }
        PathLine { x: _width + gap + 1; y: _height + 1}
        PathLine { x: 0; y: _height + 1 }
        PathLine { x: 0; y: 0 }
    }
    
    ShapePath {
        visible: _size < _MAX
        strokeWidth: 1
        strokeColor: "#bbb"
        fillColor: "#fcfcfc"
        strokeStyle: ShapePath.DashLine
        dashPattern: [3, 6]
        startX: _start_x + radius
        startY: _start_y
        PathLine { x: _width - _radius + gap - 1; y: _start_y }
        PathArc {
            x: _width + gap - 1
            y: _radius
            radiusX: _radius
            radiusY: _radius
        }
        PathLine { x: _width + gap - 1; y: _height - _radius }
        PathArc {
            x: _width - _radius + gap - 1
            y: _height
            radiusX: _radius
            radiusY: _radius
        }
        PathLine { x: _start_x + _radius; y: _height }
        PathArc {
            x: _start_x
            y: _height - radius
            radiusX: _radius
            radiusY: _radius
        }
        PathLine { x: _start_x; y: _start_y + radius }
        PathArc {
            x: _start_x + radius
            y: _start_y
            radiusX: _radius
            radiusY: _radius
        }
    }


    Component.onCompleted: function() {

    }
    
}
