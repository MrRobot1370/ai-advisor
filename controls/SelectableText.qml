import QtQuick
import QtQuick.Controls.Basic

TextEdit {
    id: selectableText

    readOnly: true
    selectByMouse: true
    selectByKeyboard: true
    wrapMode: TextEdit.Wrap

    // Enable context menu for copy/paste
    MouseArea {
        anchors.fill: parent
        acceptedButtons: Qt.RightButton
        onClicked: contextMenu.popup()

        Menu {
            id: contextMenu

            MenuItem {
                text: qsTr("Copy")
                enabled: selectableText.selectedText.length > 0
                onTriggered: selectableText.copy()
            }

            MenuItem {
                text: qsTr("Select All")
                onTriggered: selectableText.selectAll()
            }
        }
    }

    // Handle keyboard shortcuts
    Keys.onPressed: (event) => {
        if (event.modifiers === Qt.ControlModifier) {
            if (event.key === Qt.Key_C) {
                copy()
                event.accepted = true
            } else if (event.key === Qt.Key_A) {
                selectAll()
                event.accepted = true
            }
        }
    }
}
