# CivicFlow Mobile — Flutter Environment Setup

This document details the configuration for the portable, self-contained Flutter development environment created specifically for the CivicFlow project.

To avoid system-wide state pollution and version conflicts, the entire SDK toolchain is nested under the `flutter-sdk/` directory.

---

## 1. Environment Variables
To use Flutter from your command line, ensure the following environment variables are set in your current session (or permanently added to your system path):

```text
FLUTTER_HOME = <ProjectRoot>\flutter-sdk\flutter
ANDROID_HOME = <ProjectRoot>\flutter-sdk\android-sdk
ANDROID_SDK_ROOT = <ProjectRoot>\flutter-sdk\android-sdk
```

### PATH Additions
Add the following directories to your system `PATH`:
- `<ProjectRoot>\flutter-sdk\flutter\bin`
- `<ProjectRoot>\flutter-sdk\android-sdk\platform-tools`
- `<ProjectRoot>\flutter-sdk\android-sdk\cmdline-tools\latest\bin`

---

## 2. VS Code Configuration
We recommend using Visual Studio Code for development. The repository is pre-configured with workspace settings (`.vscode/settings.json`) that point exactly to this portable SDK.

### Required Extensions
- `Dart-Code.flutter`
- `Dart-Code.dart-code`
- `usernamehw.errorlens`
- `eamodio.gitlens`
- `PKief.material-icon-theme`

*(VS Code should prompt you to install these automatically when you open the repository).*

---

## 3. SDK Versions
- **Flutter SDK**: Stable Channel (Latest, e.g., 3.22.x)
- **Dart SDK**: Bundled with Flutter
- **Android Platform Tools**: Latest
- **Android Build Tools**: 35.0.0
- **Android API**: 35

---

## 4. Commands Executed During Setup
The following commands were run automatically via the `setup_flutter_env.ps1` script to bootstrap this environment:

1. Downloaded and extracted Flutter to `flutter-sdk/flutter`.
2. Downloaded and extracted Android cmdline-tools to `flutter-sdk/android-sdk/cmdline-tools/latest`.
3. `sdkmanager "platform-tools" "build-tools;35.0.0" "platforms;android-35" "emulator" --sdk_root="flutter-sdk/android-sdk"`
4. `sdkmanager --licenses --sdk_root="flutter-sdk/android-sdk"`
5. `flutter doctor -v`
6. `flutter create frontend-mobile`

---

## 5. How to Run the Flutter App

### Connecting a Physical Android Device
Because downloading system images for Android emulators requires massive disk space and RAM, using a physical device via USB debugging is highly recommended.

1. Enable **Developer Options** on your Android device (Tap "Build Number" 7 times in Settings).
2. Enable **USB Debugging**.
3. Connect the phone via USB.
4. Open the command line and run:
   ```bash
   flutter devices
   ```
   *(Your phone should be listed).*
5. Navigate to the project directory:
   ```bash
   cd frontend-mobile
   ```
6. Run the application:
   ```bash
   flutter run
   ```

### Using an Emulator
If you prefer an emulator and have the hardware capabilities, you can create one using the AVD manager:
```bash
avdmanager create avd -n test_avd -k "system-images;android-35;google_apis;x86_64"
emulator -avd test_avd
```

---

## 6. Troubleshooting

- **`flutter: command not found`**: Ensure your terminal session has loaded the `PATH` additions described in section 1.
- **Java Exception running `sdkmanager`**: The Android command-line tools require a JDK (Java Development Kit) installed on your system. If `sdkmanager` crashes, install OpenJDK 17, and set the `JAVA_HOME` environment variable.
- **License issues in `flutter doctor`**: If Android licenses are not accepted, run:
  ```bash
  flutter doctor --android-licenses
  ```
