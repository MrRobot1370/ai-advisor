import QtQuick
import QtQuick.Window
import QtQuick.Controls.Basic
import QtQuick.Layouts
import QtQml

import "controls"

ApplicationWindow {
    id: root
    visible: true
    width: 1000
    height: 750
    minimumWidth: 800
    minimumHeight: 600
    title: qsTr("AI Advisor - v0.2.0")

    // Modern color scheme
    readonly property color primaryColor: "#2C3E50"
    readonly property color accentColor: "#3498DB"
    readonly property color backgroundColor: "#F8F9FA"
    readonly property color surfaceColor: "#FFFFFF"
    readonly property color textColor: "#2C3E50"
    readonly property color borderColor: "#E9ECEF"
    readonly property color successColor: "#27AE60"
    readonly property color warningColor: "#F39C12"
    readonly property color codeBackgroundColor: "#F4F4F4"
    readonly property color codeBorderColor: "#DDD"

    function enableUserInterface() {
        inputAreaRect.enabled = true
        aiLogoTextRect.opacity = 1
        advisorProgressBar.visible = false
    }

    function disableUserInterface() {
        inputAreaRect.enabled = false
        advisorProgressBar.visible = true
    }

    Component.onCompleted: {
        enableUserInterface()
    }

    Connections {
        target: appController
        function onExecutionDone(status) {
            if (status) {
                enableUserInterface()
            } else {
                tokenCountLabel.text = ""
                disableUserInterface()
            }
        }

        function onVoiceProcessed() {
            playVoice.isPlaying = false
        }

        function onPostAnswer(answerText) {
            chatHistory.appendMessage("Assistant", answerText, false)
        }

        function onPostNumTokens(numTokens) {
            if (numTokens > 0) {
                tokenCountLabel.text = qsTr("Tokens used: %1").arg(numTokens)
            }
        }
    }

    // Component for chat messages
    Component {
        id: chatMessageComponent

        Rectangle {
            id: messageContainer
            property var messageData

            // Make width responsive to parent's width changes
            width: parent ? parent.width : 0
            height: messageColumn.height + 30
            color: messageData.isUser ? Qt.lighter(root.accentColor, 1.9) : "transparent"
            radius: 12
            border.color: messageData.isUser ? Qt.lighter(root.accentColor, 1.5) : root.borderColor
            border.width: messageData.isUser ? 1 : 0

            ColumnLayout {
                id: messageColumn
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.margins: 15
                anchors.verticalCenter: parent.verticalCenter
                spacing: 8

                RowLayout {
                    Layout.fillWidth: true

                    Rectangle {
                        Layout.preferredWidth: 24
                        Layout.preferredHeight: 24
                        color: messageData.isUser ? root.accentColor : root.successColor
                        radius: 12

                        Text {
                            anchors.centerIn: parent
                            text: messageData.isUser ? "U" : "A"
                            color: "white"
                            font.pixelSize: 10
                            font.weight: Font.Bold
                        }
                    }

                    Text {
                        text: messageData.sender
                        font.weight: Font.Bold
                        font.pixelSize: 14
                        color: messageData.isUser ? root.accentColor : root.primaryColor
                    }

                    Item { Layout.fillWidth: true }

                    CopyButton {
                        textColor: root.textColor
                        textToCopy: messageData.message
                    }

                    Text {
                        text: messageData.timestamp
                        font.pixelSize: 10
                        color: root.textColor
                        opacity: 0.6
                    }
                }

                // Message content with code detection
                MessageContent {
                    Layout.fillWidth: true
                    text: messageData.message
                    textColor: root.textColor
                    codeBackgroundColor: root.codeBackgroundColor
                    codeBorderColor: root.codeBorderColor
                }
            }
        }
    }

    // Background gradient
    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: root.backgroundColor }
            GradientStop { position: 1.0; color: Qt.lighter(root.backgroundColor, 1.02) }
        }
    }

    ColumnLayout {
        id: mainLayout
        anchors.fill: parent
        anchors.margins: 20
        spacing: 15

        // Header
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 60
            color: root.surfaceColor
            radius: 12
            border.color: root.borderColor
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.margins: 15

                Rectangle {
                    id: aiLogoTextRect
                    Layout.preferredWidth: 32
                    Layout.preferredHeight: 32
                    color: inputAreaRect.enabled ? root.accentColor : root.warningColor
                    radius: 16

                    Text {
                        anchors.centerIn: parent
                        text: "AI"
                        color: "white"
                        font.pixelSize: 12
                        font.weight: Font.Bold
                    }

                    SequentialAnimation on opacity {
                        running: !inputAreaRect.enabled
                        loops: Animation.Infinite
                        NumberAnimation { to: 0.3; duration: 800 }
                        NumberAnimation { to: 1.0; duration: 800 }
                    }
                }

                Text {
                    text: qsTr("Advisor")
                    font.pixelSize: 22
                    font.weight: Font.Bold
                    color: root.primaryColor
                }

                Item { Layout.fillWidth: true }

                Text {
                    id: tokenCountLabel
                    text: qsTr("")
                    font.pixelSize: 12
                    color: root.textColor
                    opacity: 0.7
                }
            }
        }

        // Chat History Area
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: root.surfaceColor
            radius: 12
            border.color: root.borderColor
            border.width: 1

            ScrollView {
                id: chatScrollView
                anchors.fill: parent
                anchors.margins: 15
                clip: true
                ScrollBar.vertical.policy: ScrollBar.AsNeeded
                ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

                Column {
                    id: chatHistory
                    // Make width responsive to the ScrollView's available width
                    width: chatScrollView.availableWidth
                    spacing: 15

                    property var messages: []

                    function appendMessage(sender, message, isUser) {
                        const messageData = {
                            "sender": sender,
                            "message": message,
                            "isUser": isUser,
                            "timestamp": new Date().toLocaleTimeString()
                        }

                        messages.push(messageData)

                        // Create and add new message component without explicit width
                        const messageItem = chatMessageComponent.createObject(chatHistory, {
                            "messageData": messageData
                        })

                        // Auto-scroll to bottom
                        Qt.callLater(() => {
                            chatScrollView.ScrollBar.vertical.position = 1.0 - chatScrollView.ScrollBar.vertical.size
                        })
                    }

                    function clearMessages() {
                        // Clear all child components
                        for (let i = children.length - 1; i >= 0; i--) {
                            children[i].destroy()
                        }
                        messages = []
                    }
                }
            }
        }

        // Progress Bar
        Rectangle {
            id: advisorProgressBar
            Layout.fillWidth: true
            Layout.preferredHeight: 6
            visible: false
            color: Qt.lighter(root.borderColor, 1.1)
            radius: 3

            Rectangle {
                id: progressIndicator
                height: parent.height
                width: parent.width * 0.3
                color: root.accentColor
                radius: 3

                SequentialAnimation on x {
                    running: advisorProgressBar.visible
                    loops: Animation.Infinite
                    NumberAnimation {
                        from: -progressIndicator.width
                        to: advisorProgressBar.width
                        duration: 1500
                        easing.type: Easing.InOutQuad
                    }
                }
            }
        }

        // Input Area
        Rectangle {
            id: inputAreaRect
            Layout.fillWidth: true
            Layout.preferredHeight: 120
            color: root.surfaceColor
            radius: 12
            border.color: root.borderColor
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.margins: 15
                spacing: 15

                // Text Input
                ScrollView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true

                    TextArea {
                        id: questionTextInput
                        placeholderText: qsTr("Type your question here...")
                        wrapMode: TextArea.Wrap
                        selectByMouse: true
                        font.pixelSize: 13
                        color: root.textColor

                        background: Rectangle {
                            color: "transparent"
                            border.color: questionTextInput.activeFocus ? root.accentColor : root.borderColor
                            border.width: 1
                            radius: 6
                        }

                        Keys.onPressed: (event) => {
                            if (event.key === Qt.Key_Return && event.modifiers === Qt.ControlModifier) {
                                sendButton.clicked()
                                event.accepted = true
                            }
                        }
                    }
                }

                // Control Buttons
                RowLayout {
                    spacing: 8

                    // Send Button
                    Button {
                        id: sendButton
                        Layout.preferredWidth: 45
                        Layout.preferredHeight: 45
                        enabled: questionTextInput.text.trim().length > 0

                        background: Rectangle {
                            color: parent.enabled ?
                                   (parent.hovered ? Qt.lighter(root.primaryColor, 1.5) : root.primaryColor) :
                                   root.borderColor
                            radius: 8
                        }

                        Text {
                            anchors.centerIn: parent
                            text: "📤"
                            font.pixelSize: 16
                        }

                        ToolTip.visible: hovered
                        ToolTip.text: qsTr("Send Message (Ctrl+Enter)")

                        onClicked: {
                            const userMessage = questionTextInput.text.trim()
                            if (userMessage.length > 0) {
                                disableUserInterface()
                                chatHistory.appendMessage("You", userMessage, true)
                                appController.getQuestion(userMessage)
                                questionTextInput.text = ""
                            }
                        }
                    }

                    // Voice Input Button
                    Button {
                        id: getVoice
                        visible: false
                        Layout.preferredWidth: 45
                        Layout.preferredHeight: 45

                        background: Rectangle {
                            color: parent.enabled ?
                                   (parent.hovered ? Qt.lighter(root.primaryColor, 1.5) : root.primaryColor) :
                                   root.borderColor
                            radius: 8
                        }

                        Text {
                            anchors.centerIn: parent
                            text: "🎤"
                            font.pixelSize: 16
                        }

                        ToolTip.visible: hovered
                        ToolTip.text: qsTr("Voice Input")

                        onClicked: {
                            appController.convertVoiceToText()
                            questionTextInput.text = appController.questionText
                        }
                    }

                    // Play Voice Button
                    Button {
                        id: playVoice
                        visible: false
                        Layout.preferredWidth: 45
                        Layout.preferredHeight: 45

                        property bool isPlaying: false
                        property string iconSource: "▶️"

                        background: Rectangle {
                            color: parent.enabled ?
                                   (parent.hovered ? Qt.lighter(root.primaryColor, 1.5) : root.primaryColor) :
                                   root.borderColor
                            radius: 8
                        }

                        Text {
                            anchors.centerIn: parent
                            text: playVoice.isPlaying ? "⏸️" : "▶️"
                            font.pixelSize: 14
                        }

                        ToolTip.visible: hovered
                        ToolTip.text: qsTr("Play Response")

                        onClicked: {
                            isPlaying = true
                            appController.convertTextToVoice(appController.answerText)
                        }
                    }

                    // Reset Button
                    Button {
                        id: resetButton
                        Layout.preferredWidth: 45
                        Layout.preferredHeight: 45

                        background: Rectangle {
                            color: parent.enabled ?
                                   (parent.hovered ? Qt.lighter(root.primaryColor, 1.5) : root.primaryColor) :
                                   root.borderColor
                            radius: 8
                        }

                        Text {
                            anchors.centerIn: parent
                            text: "🔄"
                            font.pixelSize: 16
                        }

                        ToolTip.visible: hovered
                        ToolTip.text: qsTr("Clear History")

                        onClicked: {
                            chatHistory.clearMessages()
                            const resetText = qsTr("Chat history has been cleared")
                            appController.resetHistory(resetText)
                        }
                    }
                }
            }
        }

        // Model Selection
        ComboBox {
            id: modelComboBox
            Layout.fillWidth: true
            Layout.preferredHeight: 40
            model: appController ? appController.availableModels : []
            currentIndex: appController ? appController.modelIndex : 0

            background: Rectangle {
                color: root.surfaceColor
                border.color: parent.activeFocus ? root.accentColor : root.borderColor
                border.width: 1
                radius: 8
            }

            contentItem: Text {
                text: modelComboBox.displayText
                font.pixelSize: 13
                color: root.textColor
                verticalAlignment: Text.AlignVCenter
                leftPadding: 12
            }

            onCurrentIndexChanged: {
                if (appController) {
                    appController.modelIndex = currentIndex
                }
            }
        }
    }
}
