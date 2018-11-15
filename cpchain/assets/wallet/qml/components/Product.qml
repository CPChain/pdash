import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtGraphicalEffects 1.0
import QtQuick.Controls 2.0
import "../cpchain" as CPC

Rectangle {
    id: product;
    width: self.width
    height: self.height
    
    Item {
        anchors.centerIn: parent
        width: self.width
        height: self.height
        Image {
            id: img
            source: self.src
            width: self.width
            height: self.height
            fillMode: Image.Stretch
            anchors.centerIn: parent

            property bool rounded: true

            layer.enabled: rounded
            layer.effect: OpacityMask {
                maskSource: Item {
                    width: img.width
                    height: img.height
                    Rectangle {
                        anchors.centerIn: parent
                        width: img.width
                        height: img.height
                        radius: 5
                    }
                }
            }

            MouseArea {
                id: image
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                acceptedButtons: Qt.AllButtons
                hoverEnabled: true

                onPressed: {
                    self.clickImage()
                }
            }

            Rectangle {
                anchors.centerIn: parent
                color: "#666"
                opacity: 0.5
                width: self.width
                height: self.height
                z: 1
                visible: self.need_mask
            }
            
            AnimatedImage {
                property var w : 180
                property var h : 40
                property var scale : 1.5
                
                source: self.downloading_gif
                visible: self.is_downloading
                width: w / scale
                height: h / scale
                x: 24
                y: 27
                fillMode: Image.Stretch
                opacity: 1
                z: 2
            }

            CPC.Text {
                text: self.show_text
                visible: self.show_text != ""
                rightPadding: 15
                bottomPadding: 35
                anchors.centerIn: parent
                color: "#ffffff"
                z: 2
            }

        }
    }

    Component.onCompleted: {

    }

}
