#include "LocalScriptsController.hxx"
#include "Application.hxx"
#include "ApplicationLogger.hxx"
#include "EditorController.hxx"
#include "SettingsController.hxx"
#include <QFileInfo>
#include <iostream>

namespace Ide::Ui {

LocalScriptsController *LocalScriptsController::instance = nullptr;
qml::RegisterType<LocalScriptsController> LocalScriptsController::Register;

LocalScriptsController::LocalScriptsController()
{
    if (instance != nullptr) {
        throw std::runtime_error("Instance of local_scripts_controller already exists");
    }
    setupProcess();
}

LocalScriptsController *LocalScriptsController::Create()
{
    instance = new LocalScriptsController();
    return instance;
}

void LocalScriptsController::run()
{
    if (m_scriptProcess->state() != QProcess::NotRunning) {
        ApplicationLogger::instance->addEntry("Script is already running.");
        return;
    }

    auto script_path = Ide::Ui::EditorController::instance->getFileUrl();

    if (script_path.size() < 2) {
        ApplicationLogger::instance->addEntry("Unable to start: save script to a .py file first.");
        return;
    }

    if (!QFileInfo::exists(script_path)) {
        ApplicationLogger::instance->addEntry("Unable to start: script file not found: " + script_path);
        return;
    }

    QString py_path = Ide::Ui::SettingsController::instance->getPythonPath();
    if (py_path.isEmpty()) {
        py_path = "python3";
    }

    ApplicationLogger::instance->addEntry("Starting script...");
    ApplicationLogger::instance->addEntry("Python: " + py_path);
    ApplicationLogger::instance->addEntry("Script: " + script_path);
    m_scriptProcess->start(py_path, {"-u", script_path});
    if (!m_scriptProcess->waitForStarted(3000)) {
        ApplicationLogger::instance->addEntry("Failed to start script process.");
        ApplicationLogger::instance->addEntry("Reason: " + m_scriptProcess->errorString());
        return;
    }

    ApplicationLogger::instance->addEntry("Program started.");
    m_pid = m_scriptProcess->processId();

    return;
}

void LocalScriptsController::processOutput() {
    const auto stdout_data = m_scriptProcess->readAllStandardOutput();
    if (!stdout_data.isEmpty()) {
        const auto text = QString::fromUtf8(stdout_data);
        ApplicationLogger::instance->addScriptOutput(text);
        std::cout << text.toStdString() << std::flush;
    }

    const auto stderr_data = m_scriptProcess->readAllStandardError();
    if (!stderr_data.isEmpty()) {
        const auto text = QString::fromUtf8(stderr_data);
        ApplicationLogger::instance->addScriptOutput(text);
        std::cerr << text.toStdString() << std::flush;
    }
}

void LocalScriptsController::processError(QProcess::ProcessError error) {
    ApplicationLogger::instance->addEntry(m_scriptProcess->errorString());
    if (error == QProcess::FailedToStart)
        ApplicationLogger::instance->addEntry("is python3 installed?");
}

void LocalScriptsController::stop()
{
    if (m_scriptProcess->state() == QProcess::NotRunning) {
        return;
    }
    m_scriptProcess->terminate();
}

bool LocalScriptsController::isRunning()
{
    return m_scriptProcess->state() == QProcess::Running;
}

bool LocalScriptsController::isLocal()
{
    return m_isLocal;
}

void LocalScriptsController::setLocal()
{
    m_isLocal = true;
    emit targetStateChanged();
}

void LocalScriptsController::setRemote()
{
    if (isRunning()) {
        m_scriptProcess->kill();
    }

    m_isLocal = false;
    emit targetStateChanged();
}

LocalScriptsController::~LocalScriptsController()
{
    if (m_scriptProcess == nullptr) {
        return;
    }

    if (m_scriptProcess->state() == QProcess::Running) {
        m_scriptProcess->kill();
        m_scriptProcess->waitForFinished();
    }
}

void LocalScriptsController::setupProcess()
{
    m_scriptProcess = new QProcess{};

    connect(m_scriptProcess,
            &QProcess::started,
            this,
            &LocalScriptsController::runningStateChanged);

    connect(m_scriptProcess,
            qOverload<int, QProcess::ExitStatus>(&QProcess::finished),
            this,
            &LocalScriptsController::runningStateChanged);

    connect(m_scriptProcess,
            &QProcess::readyReadStandardOutput,
            this,
            &LocalScriptsController::processOutput);

    connect(m_scriptProcess,
            &QProcess::readyReadStandardError,
            this,
            &LocalScriptsController::processOutput);

    connect(m_scriptProcess,
            &QProcess::errorOccurred,
            this,
            &LocalScriptsController::processError);
}

} 
