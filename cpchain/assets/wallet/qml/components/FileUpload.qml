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

    property var gap: self.gap
    property var _radius : radius;
    property var _start_x: 1
    property var _start_y: 1
    property var _width: self.width - 1
    property var _height: self.height - 1

    property var _TEXT : "<font color=\"#BBBBBB\">" + self.text + "</font><br>" + "<font color=\"#0073df\">" + self.browse_text + "</font> "
    property var _text : _TEXT;
    property var _uploaded: false;
    property var show_delete: false;

    property var file_path: null

    function to_file_path(filepath) {
        if(Qt.platform.os == "windows"){
                file_path = filepath.slice(8);
        }else{
            file_path = filepath.slice(7);
        }
        var target_str = file_path
        var size= 30
        if(target_str.length > size) {
            target_str = target_str.substr(0, size)
            target_str = target_str + '...'
        }
        _text = "<font color=\"#BBBBBB\">" + target_str + "</font> "
        _uploaded = true
        show_delete = true
        self.file = file_path
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
            "*"
        ];
        onAccepted: {
            to_file_path(new String(fileUrl));
        }
    }
    
    Rectangle {
        id: target
        anchors.centerIn: parent
        width: parent.width - 46
        height: 60
        color: "transparent"

        Row {
            anchors.verticalCenter: parent.verticalCenter
            spacing: 15
            Image {
                id: icon
                source: self.icon
                width: 36
                height: 35
                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                }
            }
            Row {
                id: text_parent
                anchors.verticalCenter: target.verticalCenter
                Column {
                    anchors.verticalCenter: target.verticalCenter
                    spacing: 0
                    Text {
                        id: file_text
                        width: 136
                        height: _uploaded? 16: 32
                        textFormat: Text.RichText;
                        wrapMode: _uploaded? Text.NoWrap: Text.WrapAnywhere;
                        text: _text
                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor

                            onClicked: function(e) {
                                fileDialog.open()
                            }
                        }
                    }
                    Text {
                        visible: show_delete
                        text: 'delete'
                        color: "#0073df"
                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor

                            onClicked: function(e) {
                                show_delete = false
                                _uploaded = false
                                _text = _TEXT
                                file_path = ""
                            }
                        }

                    }
                }
                
            }
        }
    }
    
    

    ShapePath {
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
