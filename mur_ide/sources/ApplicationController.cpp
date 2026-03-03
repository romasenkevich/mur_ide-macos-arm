#include "ApplicationController.hxx"
#include "ApplicationLogger.hxx"
#include "ApplicationMenu.hxx"
#include "EditorController.hxx"
#include "RemoteController.hxx"
#include "LocalScriptsController.hxx"
#include "NetworkController.hxx"
#include "SimulatorController.hxx"
#include "UpdateController.hxx"
#include "SettingsController.hxx"
#include <QApplication>
#include <QDir>
#include <QFileInfo>
#include <QFile>

namespace Ide::Ui {

ApplicationController *ApplicationController::instance = nullptr;
qml::RegisterType<ApplicationController> ApplicationController::Register;

ApplicationController::ApplicationController()
{
    if (instance != nullptr) {
        throw std::runtime_error("Instance of application_controller already exists");
    }
}

EditorController *ApplicationController::getEditor()
{
    return EditorController::instance;
}

ApplicationMenu *ApplicationController::getMenu()
{
    return ApplicationMenu::instance;
}

NetworkController *ApplicationController::getNetwork()
{
    return NetworkController::instance;
}

SimulatorController *ApplicationController::getSimulator()
{
    return SimulatorController::instance;
}

ApplicationLogger *ApplicationController::getLogger()
{
    return ApplicationLogger::instance;
}

LocalScriptsController *ApplicationController::getScripts()
{
    return LocalScriptsController::instance;
}

RemoteController *ApplicationController::getRemote()
{
    return RemoteController::instance;
}

UpdateController *ApplicationController::getUpdates()
{
    return UpdateController::instance;
}

Joystick *ApplicationController::getJoystick()
{
    return Joystick::instance;
}

SettingsController *ApplicationController::getSettings()
{
    return SettingsController::instance;
}

QString ApplicationController::getHelpUrl()
{
    QStringList candidates;

    if (SettingsController::instance != nullptr) {
        candidates.append(SettingsController::instance->getResourcePath() + "/help/help.html");
    }

    const auto app_dir = QDir(QApplication::applicationDirPath());
    candidates.append(app_dir.absoluteFilePath("../resources/help/help.html"));
    candidates.append(app_dir.absoluteFilePath("resources/help/help.html"));

    for (const auto &path : candidates) {
        QFileInfo help_file(path);
        if (help_file.exists() && help_file.isFile() && help_file.isReadable()) {
            return QUrl::fromLocalFile(help_file.absoluteFilePath()).toString();
        }
    }

    return "qrc:/help/help.html";
}

QString ApplicationController::getHelpText()
{
    QStringList candidates;

    if (SettingsController::instance != nullptr) {
        candidates.append(SettingsController::instance->getResourcePath() + "/help/help.md");
    }

    const auto app_dir = QDir(QApplication::applicationDirPath());
    candidates.append(app_dir.absoluteFilePath("../resources/help/help.md"));
    candidates.append(app_dir.absoluteFilePath("resources/help/help.md"));
    candidates.append(":/help/help.md");

    for (const auto &path : candidates) {
        QFile file(path);
        if (file.open(QIODevice::ReadOnly | QIODevice::Text)) {
            return QString::fromUtf8(file.readAll());
        }
    }

    return "Help is unavailable.";
}


Keyboard *ApplicationController::getKeyboard()
{
    return Keyboard::instance;
}

ApplicationController *ApplicationController::Create()
{
    instance = new ApplicationController();
    return instance;
}

bool ApplicationController::developerMode()
{
    QSettings settings("settings.ini", QSettings::IniFormat);
    bool mode = settings.value("DevMode/active", false).toBool();
    return mode;
}

} 
