import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.0
import "./cpchain" as CPC


Rectangle {
    id: product;
    width: self.width
    height: self.height
    
    Item {
        anchors.centerIn: parent
        width: self.width
        height: self.height
        Image {
            source: self.src
            width: self.width
            height: self.height
            fillMode: Image.Stretch
            anchors.centerIn: parent

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
        }
    }

    Component.onCompleted: {

    }

}
