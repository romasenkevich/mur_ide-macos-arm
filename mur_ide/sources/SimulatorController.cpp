#include "SimulatorController.hxx"
#include "SettingsController.hxx"
#include "Application.hxx"
#include "ApplicationLogger.hxx"
#include <QDebug>
#include <QFileInfo>

namespace Ide::Ui {

SimulatorController *SimulatorController::instance = nullptr;
qml::RegisterType<SimulatorController> SimulatorController::Register;

SimulatorController::SimulatorController()
{
    if (instance != nullptr) {
        throw std::runtime_error("Instance of simulator_controller already exists");
    }
    setup_process();
}

void SimulatorController::setup_process()
{
    m_simulator_process = new QProcess{};

    connect(m_simulator_process,
            &QProcess::started,
            this,
            &SimulatorController::runningStateChanged);

    connect(m_simulator_process,
            qOverload<int, QProcess::ExitStatus>(&QProcess::finished),
            this,
            &SimulatorController::runningStateChanged);

    connect(m_simulator_process,
            &QProcess::errorOccurred,
            this,
            &SimulatorController::processError);
}

SimulatorController *Ide::Ui::SimulatorController::Create()
{
    instance = new SimulatorController{};
    return instance;
}

void SimulatorController::run()
{
    if (m_simulator_process->state() != QProcess::NotRunning) {
        return;
    }

    auto sim_path = Ide::Ui::SettingsController::instance->getSimulatorPath();
    ApplicationLogger::instance->addEntry("Starting simulator...");
    ApplicationLogger::instance->addEntry("Simulator: " + sim_path);

    if (!QFileInfo::exists(sim_path)) {
        ApplicationLogger::instance->addEntry("Simulator binary not found.");
        ApplicationLogger::instance->addEntry("Set Paths/simulator to a valid executable path.");
        return;
    }

    m_simulator_process->setProgram(sim_path);
    m_simulator_process->start();
    if (!m_simulator_process->waitForStarted(3000)) {
        ApplicationLogger::instance->addEntry("Failed to start simulator.");
        ApplicationLogger::instance->addEntry("Reason: " + m_simulator_process->errorString());
    }
}

void SimulatorController::processError(QProcess::ProcessError)
{
    ApplicationLogger::instance->addEntry("Simulator process error: " + m_simulator_process->errorString());
}

bool SimulatorController::isRunning()
{
    return m_simulator_process->state() == QProcess::Running;
}

SimulatorController::~SimulatorController()
{
    if (m_simulator_process == nullptr) {
        return;
    }

    if (m_simulator_process->state() == QProcess::Running) {
        m_simulator_process->kill();
        m_simulator_process->waitForFinished();
    }
}

} 
