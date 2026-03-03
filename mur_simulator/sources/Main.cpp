#include "Application.h"
#include <QGuiApplication>

int main(int argc, char **argv) {
  qputenv("LC_ALL", "C");
  // Keep simulator rendering in 1:1 logical pixels on macOS to avoid
  // quarter-screen viewport issues with external NSView embedding.
  qputenv("QT_ENABLE_HIGHDPI_SCALING", "0");
  qputenv("QT_AUTO_SCREEN_SCALE_FACTOR", "0");
  qputenv("QT_SCALE_FACTOR", "1");
  int result = QUrho::Application::execute(argc, argv);
  return result;
}