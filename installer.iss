[Setup]
AppName=JARVIS Mark II
AppVersion=2.0.0
AppPublisher=Stark Industries
DefaultDirName={autopf}\JARVIS Mark II
DefaultGroupName=JARVIS Mark II
UninstallDisplayIcon={app}\Jarvis.exe
Compression=lzma2
SolidCompression=yes
OutputDir=dist
OutputBaseFilename=JarvisSetup

[Files]
Source: "dist\Jarvis.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\JARVIS Mark II"; Filename: "{app}\Jarvis.exe"
Name: "{autodesktop}\JARVIS Mark II"; Filename: "{app}\Jarvis.exe"

[Run]
Filename: "{app}\Jarvis.exe"; Description: "Launch JARVIS Mark II"; Flags: postinstall nowait skipifsilent
