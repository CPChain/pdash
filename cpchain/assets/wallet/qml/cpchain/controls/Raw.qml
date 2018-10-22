import QtQuick 2.0

Rectangle {
    width: 180;
    height: 100

    function tick(item) {
        data.insert(0, {
            "item": item
        })
    }

    ListModel {
        id: data
    }

    Component {
        id: contactsDelegate
        Rectangle {
            id: wrapper
            width: parent.width
            height: contactInfo.height
            Text {
                id: contactInfo
                text: item
            }
        }
    }

    ListView {
        id: list
        anchors.fill: parent
        model: data
        delegate: contactsDelegate
        highlight: Rectangle { color: "lightsteelblue"; radius: 5 }
        focus: true
    }
}