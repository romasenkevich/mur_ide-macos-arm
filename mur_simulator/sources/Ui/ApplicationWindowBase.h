#pragma once

#include <QMainWindow>
#include <QAction>
#include <QCloseEvent>
#include <QToolBar>
#include <QLabel>
#include <QTimer>
#include <QStandardPaths>

namespace QUrho {

class QUrhoWidget;
class QUrhoScene;
class GraphicsSettingsWidget;

class ApplicationWindowBase : public QMainWindow {
    Q_OBJECT
public:
    explicit ApplicationWindowBase(QWidget *parent = nullptr);

    ~ApplicationWindowBase() override;

    virtual void InitializeEngine() = 0;
    void OpenFile(const QString &file);

protected:
    virtual void OnSceneLoaded(const QString &scene, const QString &scene_dir) = 0;
    virtual void OnSettingAccepted() = 0;
    virtual void OnLuaSettingsAccepted() = 0;
    virtual void UpdateNotification() = 0;

    void OnGraphicsSettingAccepted();
    void OpenScene(const QString &scene, const QString &scene_dir = "");

    QScopedPointer<QWidget> m_centralContainer;
    QScopedPointer<QUrhoWidget> m_urhoWidget;
    QSharedPointer<QUrhoScene> m_scene;
    QScopedPointer<GraphicsSettingsWidget> m_graphicsWidget;
    bool m_remote = true;

    QString scene_cache_path = QStandardPaths::writableLocation(QStandardPaths::CacheLocation) + "/mur_scene/";
};
}




