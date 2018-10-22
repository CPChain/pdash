import QtQuick.Controls 2.4

TabButton {
    width: 100
    Rectangle {
        anchors.fill: parent
        color: ( parent.checked ? "white" : "black" )
        border.color: "black"

        Text {
            anchors.centerIn: parent
            text: qsTr("Visualization")
            color: ( parent.parent.checked ? "black" : "white" )
        }
    }
}
