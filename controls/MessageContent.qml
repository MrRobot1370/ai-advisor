import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import QtQml

Item {
    id: messageContent
    Layout.fillWidth: true
    implicitHeight: contentColumn.height

    property alias text: messageParser.text
    property color textColor: "#2C3E50"
    property color codeBackgroundColor: "#F8F9FA"
    property color codeBorderColor: "#E9ECEF"
    property color linkColor: "#3498DB"
    property real fontSize: 13
    property real codeFontSize: 12

    // Text parser to detect code blocks and regular text
    QtObject {
        id: messageParser
        property string text: model.message || ""
        property var parsedContent: []

        function parseMessage() {
            parsedContent = []
            if (!text || text.length === 0) {
                return
            }

            let remainingText = text
            let blockIndex = 0

            // More robust regex for code blocks
            const codeBlockRegex = /```(\w+)?\s*\n?([\s\S]*?)```/g
            const codeBlocks = []
            let match

            // Find all code blocks
            while ((match = codeBlockRegex.exec(remainingText)) !== null) {
                codeBlocks.push({
                    start: match.index,
                    end: match.index + match[0].length,
                    language: (match[1] || "text").toLowerCase(),
                    code: match[2] || "",
                    fullMatch: match[0]
                })
            }

            // Sort code blocks by position
            codeBlocks.sort((a, b) => a.start - b.start)

            // Process text with code blocks
            if (codeBlocks.length > 0) {
                let currentPos = 0

                for (let i = 0; i < codeBlocks.length; i++) {
                    const block = codeBlocks[i]

                    // Add text before code block
                    if (block.start > currentPos) {
                        const beforeText = remainingText.substring(currentPos, block.start).trim()
                        if (beforeText.length > 0) {
                            parsedContent.push({
                                type: "text",
                                content: beforeText,
                                index: blockIndex++
                            })
                        }
                    }

                    // Add code block (only if it has content)
                    const cleanCode = block.code.trim()
                    if (cleanCode.length > 0) {
                        parsedContent.push({
                            type: "code",
                            content: cleanCode,
                            language: block.language,
                            index: blockIndex++
                        })
                    }

                    currentPos = block.end
                }

                // Add remaining text after last code block
                if (currentPos < remainingText.length) {
                    const afterText = remainingText.substring(currentPos).trim()
                    if (afterText.length > 0) {
                        parsedContent.push({
                            type: "text",
                            content: afterText,
                            index: blockIndex++
                        })
                    }
                }
            } else {
                // No code blocks, treat as regular text
                const cleanText = remainingText.trim()
                if (cleanText.length > 0) {
                    parsedContent.push({
                        type: "text",
                        content: cleanText,
                        index: 0
                    })
                }
            }

            // Update the model
            contentRepeater.model = parsedContent
        }

        onTextChanged: parseMessage()
        Component.onCompleted: parseMessage()
    }

    Column {
        id: contentColumn
        width: parent.width
        spacing: 12

        Repeater {
            id: contentRepeater
            model: messageParser.parsedContent

            delegate: Loader {
                width: contentColumn.width
                sourceComponent: modelData.type === "code" ? codeBlockComponent : textBlockComponent
                property var blockData: modelData
            }
        }
    }

    // Component for regular text
    Component {
        id: textBlockComponent

        SelectableText {
            width: parent.width
            text: blockData.content
            color: messageContent.textColor
            font.pixelSize: messageContent.fontSize
            wrapMode: Text.Wrap
            selectByMouse: true
            textFormat: Text.PlainText

            MouseArea {
                anchors.fill: parent
                acceptedButtons: Qt.NoButton
                cursorShape: parent.hoveredLink ? Qt.PointingHandCursor : Qt.IBeamCursor
            }
        }
    }

    // Component for code blocks
    Component {
        id: codeBlockComponent

        Rectangle {
            width: parent.width
            height: codeBlockLayout.implicitHeight + 20
            color: messageContent.codeBackgroundColor
            border.color: messageContent.codeBorderColor
            border.width: 1
            radius: 8

            ColumnLayout {
                id: codeBlockLayout
                anchors.fill: parent
                anchors.margins: 12
                spacing: 8

                // Header with language and copy button
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 28

                    Rectangle {
                        Layout.preferredWidth: Math.max(60, languageText.implicitWidth + 16)
                        Layout.preferredHeight: 22
                        color: Qt.darker(messageContent.codeBackgroundColor, 1.05)
                        border.color: messageContent.codeBorderColor
                        border.width: 1
                        radius: 11

                        Text {
                            id: languageText
                            anchors.centerIn: parent
                            text: blockData.language.toUpperCase()
                            font.pixelSize: 9
                            font.weight: Font.DemiBold
                            color: messageContent.textColor
                            opacity: 0.8
                        }
                    }

                    Item { Layout.fillWidth: true }

                    CopyButton {
                        textColor: messageContent.textColor
                        textToCopy: blockData.content
                    }
                }

                // Code content area
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: codeText.implicitHeight + 16

                    color: "transparent"
                    clip: true

                    SelectableText {
                        id: codeText
                        anchors.fill: parent
                        anchors.margins: 8
                        width: Math.max(parent.width, implicitWidth)

                        color: messageContent.textColor
                        font.family: "Consolas, 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Menlo, 'DejaVu Sans Mono', monospace"
                        font.pixelSize: messageContent.codeFontSize
                        // Conditional wrapping - wrap for text, no wrap for code
                        wrapMode: (blockData.language.toLowerCase() === "text" ||
                                   blockData.language.toLowerCase() === "txt" ||
                                   blockData.language.toLowerCase() === "") ? Text.Wrap : Text.NoWrap
                        selectByMouse: true
                        textFormat: Text.RichText

                        text: syntaxHighlighter.highlight(blockData.content, blockData.language)

                        MouseArea {
                            anchors.fill: parent
                            acceptedButtons: Qt.NoButton
                            cursorShape: Qt.IBeamCursor
                        }
                    }
                }
            }
        }
    }

    // Enhanced syntax highlighter
    QtObject {
        id: syntaxHighlighter

        property var languageKeywords: ({
            "python": ["def", "class", "import", "from", "if", "else", "elif", "for", "while", "try", "except", "finally", "with", "as", "return", "yield", "lambda", "and", "or", "not", "in", "is", "True", "False", "None", "async", "await", "self", "super", "__init__"],
            "javascript": ["function", "var", "let", "const", "if", "else", "for", "while", "do", "switch", "case", "break", "continue", "return", "try", "catch", "finally", "class", "extends", "import", "export", "default", "async", "await", "true", "false", "null", "undefined", "this", "new"],
            "cpp": ["#include", "#define", "#ifdef", "#ifndef", "#endif", "namespace", "using", "class", "struct", "public", "private", "protected", "virtual", "static", "const", "constexpr", "if", "else", "for", "while", "do", "switch", "case", "break", "continue", "return", "try", "catch", "throw", "true", "false", "nullptr", "auto", "template", "typename"],
            "c": ["#include", "#define", "#ifdef", "#ifndef", "#endif", "int", "char", "float", "double", "void", "struct", "union", "enum", "typedef", "static", "extern", "const", "if", "else", "for", "while", "do", "switch", "case", "break", "continue", "return", "sizeof", "NULL"],
            "java": ["public", "private", "protected", "static", "final", "abstract", "class", "interface", "extends", "implements", "import", "package", "if", "else", "for", "while", "do", "switch", "case", "break", "continue", "return", "try", "catch", "finally", "throw", "throws", "true", "false", "null", "this", "super", "new"],
            "csharp": ["public", "private", "protected", "internal", "static", "readonly", "const", "class", "struct", "interface", "namespace", "using", "if", "else", "for", "foreach", "while", "do", "switch", "case", "break", "continue", "return", "try", "catch", "finally", "throw", "true", "false", "null", "this", "new", "var", "async", "await"],
            "qml": ["import", "property", "signal", "function", "var", "let", "const", "if", "else", "for", "while", "do", "switch", "case", "break", "continue", "return", "try", "catch", "finally", "true", "false", "null", "undefined", "this", "parent", "anchors", "width", "height", "color", "visible", "enabled"]
        })

        property var colorScheme: ({
            keyword: "#8E44AD",      // Purple for keywords
            string: "#27AE60",       // Green for strings
            comment: "#95A5A6",      // Gray for comments
            number: "#E67E22",       // Orange for numbers
            type: "#3498DB",         // Blue for types
            operator: "#E74C3C"      // Red for operators
        })

        function highlight(code, language) {
            if (!code || code.length === 0) {
                return ""
            }

            const lang = language.toLowerCase()

            // Work with original code for pattern matching
            let highlighted = code
            let placeholders = []
            let placeholderIndex = 0

            function createPlaceholder(content) {
                const placeholder = `__PLACEHOLDER_${placeholderIndex}__`
                placeholders.push({ placeholder: placeholder, content: content })
                placeholderIndex++
                return placeholder
            }

            // Track positions of existing highlights to avoid conflicts
            let protectedRanges = []

            function addProtectedRange(start, end) {
                protectedRanges.push({start: start, end: end})
                protectedRanges.sort((a, b) => a.start - b.start)
            }

            function isProtected(start, end) {
                return protectedRanges.some(range =>
                    (start >= range.start && start < range.end) ||
                    (end > range.start && end <= range.end) ||
                    (start < range.start && end > range.end)
                )
            }

            // 1. Highlight strings first (highest priority)
            const stringPatterns = [
                /"""[\s\S]*?"""/g,  // Python triple quotes
                /'''[\s\S]*?'''/g,  // Python single triple quotes
                /"(?:[^"\\]|\\.)*"/g, // Double quotes
                /'(?:[^'\\]|\\.)*'/g  // Single quotes
            ]

            stringPatterns.forEach(pattern => {
                highlighted = highlighted.replace(pattern, (match, offset) => {
                    if (!isProtected(offset, offset + match.length)) {
                        addProtectedRange(offset, offset + match.length)
                        const styledContent = `<span style="color: ${colorScheme.string};">${escapeHtml(match)}</span>`
                        return createPlaceholder(styledContent)
                    }
                    return match
                })
            })

            // 2. Highlight comments
            const commentPatterns = []
            if (lang === "python") {
                commentPatterns.push(/#[^\n\r]*/g)
            } else if (["javascript", "cpp", "c", "java", "csharp", "qml"].includes(lang)) {
                commentPatterns.push(/\/\/[^\n\r]*/g)  // Single line
                commentPatterns.push(/\/\*[\s\S]*?\*\//g)  // Multi line
            }

            commentPatterns.forEach(pattern => {
                highlighted = highlighted.replace(pattern, (match, offset) => {
                    if (!isProtected(offset, offset + match.length)) {
                        addProtectedRange(offset, offset + match.length)
                        const styledContent = `<span style="color: ${colorScheme.comment}; font-style: italic;">${escapeHtml(match)}</span>`
                        return createPlaceholder(styledContent)
                    }
                    return match
                })
            })

            // 3. Highlight keywords
            const keywords = languageKeywords[lang] || []
            keywords.forEach(keyword => {
                const pattern = new RegExp(`\\b${escapeRegExp(keyword)}\\b`, 'g')
                highlighted = highlighted.replace(pattern, (match, offset) => {
                    if (!isProtected(offset, offset + match.length)) {
                        const styledContent = `<span style="color: ${colorScheme.keyword}; font-weight: bold;">${escapeHtml(match)}</span>`
                        return createPlaceholder(styledContent)
                    }
                    return match
                })
            })

            // 4. Highlight numbers
            const numberPattern = /\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\b/g
            highlighted = highlighted.replace(numberPattern, (match, offset) => {
                if (!isProtected(offset, offset + match.length)) {
                    const styledContent = `<span style="color: ${colorScheme.number};">${escapeHtml(match)}</span>`
                    return createPlaceholder(styledContent)
                }
                return match
            })

            // 5. Escape remaining HTML in the unhighlighted parts
            highlighted = escapeHtml(highlighted)

            // 6. Replace placeholders with actual styled content
            placeholders.forEach(({ placeholder, content }) => {
                highlighted = highlighted.replace(placeholder, content)
            })

            // 7. Convert newlines to <br> and preserve only leading indentation
            {
                const lines = highlighted.split('\n')
                const processedLines = lines.map(line => {
                    const leadingSpaces = (line.match(/^ */)[0] || '').length
                    const indent = '&nbsp;'.repeat(leadingSpaces)
                    const content = line.substring(leadingSpaces)
                    return indent + content
                })
                highlighted = processedLines.join('<br>')
            }
            return highlighted
        }

        function escapeRegExp(string) {
            return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
        }

        function escapeHtml(text) {
            return text.replace(/&/g, "&amp;")
                      .replace(/</g, "&lt;")
                      .replace(/>/g, "&gt;")
                      .replace(/"/g, "&quot;")
                      .replace(/'/g, "&#x27;")
        }
    }
}
