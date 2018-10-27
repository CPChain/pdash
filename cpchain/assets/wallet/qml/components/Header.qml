import QtQuick 2.3
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.0
import "../cpchain" as CPC


Rectangle {
    id: header;
    width: 1002;
    height: 90
    color: "#006bcf"
    
    ColumnLayout {
        anchors.fill: parent
        RowLayout {
            anchors.fill: parent
            CPC.Image {
                Layout.alignment: Qt.AlignRight
                source: closeArea.containsMouse ? self.close_icon_hover : self.close_icon
                width: 15
                height: 15

                MouseArea {
                    id: closeArea
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    acceptedButtons: Qt.AllButtons
                    hoverEnabled: true

                    onPressed: {
                        self.close()
                    }
                }
            }
        }
        RowLayout {

        }
    }

    Component.onCompleted: {
        console.log(self.close_icon)
    }

}
