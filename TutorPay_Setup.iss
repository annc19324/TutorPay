[Setup]
AppName=TutorPay
AppVersion=1.0
DefaultDirName={autopf}\TutorPay
DefaultGroupName=TutorPay
OutputDir=dist
OutputBaseFilename=TutorPay_Setup
Compression=lzma
SolidCompression=yes
SetupIconFile=annc19324.ico
UninstallDisplayIcon={app}\main.exe
WizardStyle=modern

[Files]
Source: "dist\main.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "annc19324.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "annc19324.jpg"; DestDir: "{app}"; Flags: ignoreversion
Source: "DejaVuSans.ttf"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\TutorPay"; Filename: "{app}\main.exe"; IconFilename: "{app}\annc19324.ico"
Name: "{autodesktop}\TutorPay"; Filename: "{app}\main.exe"; IconFilename: "{app}\annc19324.ico"