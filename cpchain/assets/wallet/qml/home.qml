import QtQuick 2.6
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.0
import "./cpchain" as CPC


Rectangle {
    id: main;
    color: "#fafafa"
    width: 803
    height: 248
    
    RowLayout {
        x: 41;
        y: 33;
        spacing: 14

        CPC.Image {
            source: self.icon;
            width: 102;
            height: 102;
        }
        Rectangle {
            x: 116
            y: 0
            CPC.Text {
                x: 0
                y: 0
                text: self.username;
                font.pixelSize: 24
            }
            RowLayout {
                x: 0
                y: 48
                CPC.Text {
                    text: self.amount;
                    font.pixelSize: 20
                }
                CPC.Text {
                    text: "CPC";
                }
            }
            CPC.Text {
                x: 0
                y: 80
                text: "View Wallet"
                color: "#0073df"
                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    acceptedButtons: Qt.AllButtons

                    onPressed: {
                        self.to_wallet()
                    }
                }
            }
        }
    }

    Rectangle {
        x: 0
        y: 167
        width: 800
        height: 1
        color: '#cccccc'
        opacity: 0.41
    }

    CPC.Text {
        x: 41
        y: 199
        text: "My Products"
        font.pixelSize: 24;
        color: "#000000";
    }

    Component.onCompleted: {
        
    }

}
