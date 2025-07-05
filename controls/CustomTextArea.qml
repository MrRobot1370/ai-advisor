import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ScrollView {
    property alias text: textArea.text
    property alias readOnly: textArea.readOnly

    function textAppend(txt) {
        textArea.append(txt)
    }

    TextArea {
        id: textArea

        Layout.fillWidth: true
        topPadding: 10
        leftPadding: 10
        rightPadding: 10
        bottomPadding: 10
        Layout.alignment: Qt.AlignRight
        horizontalAlignment: Text.AlignLeft
        verticalAlignment: Text.AlignTop
        selectionColor: "#1E90FF"
        selectedTextColor: "#ffffff"
        selectByMouse: true
        wrapMode: TextArea.WordWrap
    }
}
