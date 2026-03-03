import QtQuick 2.12
import QtQuick 2.11
import QtQuick.Controls 2.12
import QtQml 2.2

Rectangle {
    id: root;

    color: Style.bgBlue;
    property string tabTitle: "Console";
    property bool wrapOutput: false;

    TextArea {
        id: outputArea;
        anchors.left: parent.left;
        anchors.right: parent.right;
        anchors.top: parent.top;
        anchors.bottom: footer.top;
        leftPadding: 6;
        rightPadding: 6;
        topPadding: 4;
            bottomPadding: 4;
            readOnly: true;
        selectByMouse: true;
        wrapMode: root.wrapOutput ? TextArea.Wrap : TextArea.NoWrap;
            color: Style.orange;
            font.family: Style.fontMono;
            font.pixelSize: 12;
        textFormat: Text.PlainText;
            text: Controllers.logger.output;
        background: Rectangle {
            color: Style.bgBlue;
        }
    }

    Rectangle {
        id: footer;
        height: 21;
        anchors.left: parent.left;
        anchors.right: parent.right;
        anchors.bottom: parent.bottom;
        color: Style.bgDark;
        property bool shrink: width < 200;

        Row {
            anchors.right: parent.right;
            anchors.top: parent.top;
            anchors.bottom: parent.bottom;
            anchors.rightMargin: 4;
            spacing: 4;
            visible: footer.width > 80;

            UiButton {
                id: buttonWordWrap;
                property bool active: root.wrapOutput;
                anchors.verticalCenter: parent.verticalCenter;
                icon: active ? icons.fa_indent : icons.fa_align_justify;
                label.text: footer.shrink ? "" : "Word wrap";
                highlight: active;
                onClicked: {
                    root.wrapOutput = !root.wrapOutput;
                    active = root.wrapOutput;
                }
            }

            UiButton {
                id: buttonClearOutput;
                icon: icons.fa_trash_o;
                label.text: footer.shrink ? "" : "Clear";
                anchors.verticalCenter: parent.verticalCenter;
                onClicked: Controllers.logger.clear();
            }
        }
    }

}
