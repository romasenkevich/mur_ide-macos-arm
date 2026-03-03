#include "LuaOverlay.h"
#include "../Core/QUrhoScene.h"
#include <QDebug>
#include <QFile>
#include <QDir>

namespace QUrho {
    LuaOverlay::LuaOverlay(Urho3D::Context *context, QUrho::QUrhoScene *scene, QObject *parent) :
            QObject{parent},
            Urho3D::Object{context},
            m_scene{scene->GetScene()},
            m_urhoScene{scene} {
    }

    void LuaOverlay::GetPath(){
        lua_path = m_urhoScene->GetSceneDir() + "/Script.lua";
    }

    void LuaOverlay::Run(QString script_path) {
        Q_UNUSED(script_path)
        // LuaScript module is unavailable in the current Urho3D build on macOS.
        // Keep simulator running without embedded Lua automation.
        m_isScriptRunning = true;
    }

    void LuaOverlay::Update(QUrhoInput *input, float timeStep) {
        if (QFile::exists(lua_path)) {
            scriptExists = true;
        }

        if (!m_isScriptRunning && scriptExists){
            this->Run(lua_path);
        }
    }

    void LuaOverlay::RestartScript() {
        m_isScriptRunning = false;
        scriptExists = false;
    }

    void LuaOverlay::DisableNode(Urho3D::String name, bool enable)
    {
        Urho3D::Node* particleNode = m_scene->GetChild(name, true);

        if (particleNode)
            particleNode->SetEnabled(enable);
    }

}

