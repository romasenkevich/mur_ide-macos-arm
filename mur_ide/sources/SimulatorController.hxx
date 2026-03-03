#pragma once

#include "QmlUtils.hxx"

#include <QObject>
#include <QProcess>

namespace Ide::Ui {

class SimulatorController : public QObject
{
    Q_OBJECT
    Q_PROPERTY(bool running READ isRunning NOTIFY runningStateChanged)

public:
    static SimulatorController *instance;
    static SimulatorController *Create();

    void run();
    bool isRunning();
    void processError(QProcess::ProcessError error);

    ~SimulatorController();

signals:
    void runningStateChanged();

private:
    SimulatorController();
    static qml::RegisterType<SimulatorController> Register;

    void setup_process();

    QProcess *m_simulator_process = nullptr;
};

} 
