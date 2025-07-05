import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Button {
    id: copyButton

    property string textToCopy: ""
    property color textColor: "black"

    property bool copied: false

    Layout.preferredWidth: 30
    Layout.preferredHeight: 24

    background: Rectangle {
        color: "transparent"
        radius: 4
    }

    contentItem: Text {
        anchors.centerIn: parent
        text: copied ? "✅" : "📋"
        font.pixelSize: 12
        font.weight: Font.Medium
        color: textColor
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        opacity: 0.8
    }

    ToolTip.visible: hovered
    ToolTip.text: qsTr("Copy to clipboard")

    onClicked: {
        if (typeof appController !== "undefined") {
            appController.copyToClipboard(textToCopy)
        }
        copied = true
        copyTimer.start()
        copyAnimation.start()
    }

    Timer {
        id: copyTimer
        interval: 1000
        onTriggered: copyButton.copied = false
    }

    SequentialAnimation {
        id: copyAnimation
        PropertyAnimation {
            target: copyButton
            property: "scale"
            to: 1.05
            duration: 80
        }
        PropertyAnimation {
            target: copyButton
            property: "scale"
            to: 1.0
            duration: 80
        }
    }
}
