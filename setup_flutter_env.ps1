param (
    [switch]$SkipDownloads
)

$ProgressPreference = 'SilentlyContinue'

    [switch]$SkipDownloads
)

$ErrorActionPreference = "Stop"

$ProjectRoot = (Get-Item .).FullName
$FlutterSdkDir = Join-Path $ProjectRoot "flutter-sdk"
$FlutterDir = Join-Path $FlutterSdkDir "flutter"
$AndroidSdkDir = Join-Path $FlutterSdkDir "android-sdk"
$CmdLineToolsDir = Join-Path $AndroidSdkDir "cmdline-tools"
$LatestCmdLineToolsDir = Join-Path $CmdLineToolsDir "latest"

Write-Host "Creating directory structure..."
New-Item -ItemType Directory -Force -Path $FlutterSdkDir | Out-Null
New-Item -ItemType Directory -Force -Path $AndroidSdkDir | Out-Null
New-Item -ItemType Directory -Force -Path $CmdLineToolsDir | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $AndroidSdkDir "platform-tools") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $AndroidSdkDir "emulator") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $AndroidSdkDir "licenses") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $AndroidSdkDir "cache") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $AndroidSdkDir "temp") | Out-Null

if (-not $SkipDownloads) {
    Write-Host "Downloading Flutter SDK (this may take a while)..."
    $FlutterZipUrl = "https://storage.googleapis.com/flutter_infra_release/releases/stable/windows/flutter_windows_3.22.2-stable.zip"
    $FlutterZipPath = Join-Path $FlutterSdkDir "flutter.zip"
    if (-not (Test-Path $FlutterZipPath)) {
        Invoke-WebRequest -Uri $FlutterZipUrl -OutFile $FlutterZipPath
    }

    Write-Host "Extracting Flutter SDK..."
    if (-not (Test-Path $FlutterDir)) {
        Expand-Archive -Path $FlutterZipPath -DestinationPath $FlutterSdkDir -Force
    }

    Write-Host "Downloading Android SDK Command-line Tools..."
    $AndroidToolsUrl = "https://dl.google.com/android/repository/commandlinetools-win-11076708_latest.zip"
    $AndroidToolsZipPath = Join-Path $AndroidSdkDir "cmdline-tools.zip"
    if (-not (Test-Path $AndroidToolsZipPath)) {
        Invoke-WebRequest -Uri $AndroidToolsUrl -OutFile $AndroidToolsZipPath
    }

    Write-Host "Extracting Android Command-line Tools..."
    if (-not (Test-Path $LatestCmdLineToolsDir)) {
        $TempExtractDir = Join-Path $AndroidSdkDir "temp_extract"
        Expand-Archive -Path $AndroidToolsZipPath -DestinationPath $TempExtractDir -Force
        Move-Item -Path (Join-Path $TempExtractDir "cmdline-tools\*") -Destination $LatestCmdLineToolsDir -Force
        Remove-Item -Recurse -Force $TempExtractDir
    }

    Write-Host "Setting temporary environment variables..."
    $env:ANDROID_HOME = $AndroidSdkDir
    $env:ANDROID_SDK_ROOT = $AndroidSdkDir
    $env:FLUTTER_HOME = $FlutterDir
    $env:PATH += ";$FlutterDir\bin;$AndroidSdkDir\platform-tools;$LatestCmdLineToolsDir\bin"

    Write-Host "Running sdkmanager to install required packages..."
    # We pipe 'y' to accept licenses automatically if prompted during install
    # This requires java to be installed. If it fails, we catch it.
    try {
        echo "y" | & "$LatestCmdLineToolsDir\bin\sdkmanager.bat" "platform-tools" "build-tools;35.0.0" "platforms;android-35" "emulator" --sdk_root="$AndroidSdkDir"
        
        Write-Host "Accepting all Android licenses..."
        echo "y" | & "$LatestCmdLineToolsDir\bin\sdkmanager.bat" --licenses --sdk_root="$AndroidSdkDir"
    } catch {
        Write-Host "WARNING: sdkmanager failed. You may need to install Java (JDK 17) manually and run it yourself." -ForegroundColor Yellow
    }

    Write-Host "Running flutter doctor..."
    & "$FlutterDir\bin\flutter.bat" doctor -v
}

Write-Host "Setup script finished."
