import QtQuick 2.12

Item {
    id: root;

    default property alias content: container.children;

    property var visibleItem: undefined;
    property int selectedIndex: -1;
    property int itemsCount: container.children.length;

    function applySelection() {
        if (container.children.length === 0) {
            visibleItem = undefined;
            return;
        }

        var index = selectedIndex;
        if (index < 0 || index >= container.children.length) {
            index = 0;
        }

        for (var i = 0; i < container.children.length; i++) {
            container.children[i].visible = (i === index);
        }

        root.selectedIndex = index;
        root.visibleItem = container.children[index];
    }

    function selectTab(index) {
        selectedIndex = index;
        applySelection();
    }

    Item {
        id: container;

        anchors.top: parent.top;
        anchors.left: parent.left;
        anchors.right: parent.right;
        anchors.bottom: footer.top;
    }

    onSelectedIndexChanged: applySelection()
    onItemsCountChanged: applySelection()

    Rectangle {
        id: footer;

        anchors.left: parent.left;
        anchors.right: parent.right;
        anchors.bottom: parent.bottom;

        color: Style.bgDark;

        height: 22;
        clip: true;

        Row {
            anchors.top: parent.top;
            anchors.bottom: parent.bottom;

            Repeater {
                model: container.children.length;

                delegate: Rectangle {
                    id: panel;

                    width: label.width + 24;
                    anchors.top: parent.top;
                    anchors.topMargin: -radius;
                    anchors.bottom: parent.bottom;
                    anchors.bottomMargin: 1;
                    radius: 4;
                    color: index == root.selectedIndex ? Style.bgDarker : Style.bgDark;

                    UiLabel {
                        id: label;

                        anchors.centerIn: parent;
                        anchors.verticalCenterOffset: panel.radius/2;
                        textFormat: Text.RichText;

                        enabled: index == root.selectedIndex;

                        text: container.children[index] && container.children[index].tabTitle
                              ? container.children[index].tabTitle
                              : "Tab " + (index + 1);
                    }

                    MouseArea {
                        anchors.fill: parent;
                        anchors.topMargin: -panel.radius;
                        onClicked: {
                            root.selectedIndex = index;
                        }
                    }
                }
            }
        }

        Rectangle {
            anchors.left: parent.left;
            anchors.right: parent.right;
            anchors.top: parent.top;

            height: 1;
            color: Style.bgDarker
        }
    }

    Component.onCompleted: {
        root.selectedIndex = 0;
        applySelection();
    }
}
