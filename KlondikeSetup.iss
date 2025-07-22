[Setup]
AppId={{1B2F5C8D-9E3A-4B7C-8F1D-6A5E9B2C4D7F}
AppName=Klondike Archiver
AppVersion=1.0.0
AppVerName=Klondike Archiver 1.0.0
AppPublisher=Klondike Software
DefaultDirName={autopf}\Klondike Archiver
DefaultGroupName=Klondike Archiver
AllowNoIcons=yes
LicenseFile=LICENSE.txt
InfoBeforeFile=README.txt
OutputDir=dist
OutputBaseFilename=KlondikeArchiverSetup
SetupIconFile=klondike_icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
UninstallDisplayIcon={app}\KCrinkle.exe

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode
Name: "fileassoc"; Description: "Associate .kc files with Klondike Archiver"; GroupDescription: "File Associations"; Flags: checkedonce

[Files]
Source: "dist\KCrinkle.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "klondike_icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "kc_file_icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion isreadme
Source: "README.txt"; DestDir: "{app}"; Flags: ignoreversion isreadme

[Icons]
Name: "{group}\Klondike Archiver"; Filename: "{app}\KCrinkle.exe"; IconFilename: "{app}\klondike_icon.ico"
Name: "{group}\{cm:UninstallProgram,Klondike Archiver}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Klondike Archiver"; Filename: "{app}\KCrinkle.exe"; IconFilename: "{app}\klondike_icon.ico"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\Klondike Archiver"; Filename: "{app}\KCrinkle.exe"; IconFilename: "{app}\klondike_icon.ico"; Tasks: quicklaunchicon

[Registry]
; File association for .kc files
Root: HKCR; Subkey: ".kc"; ValueType: string; ValueName: ""; ValueData: "KlondikeArchive"; Flags: uninsdeletevalue; Tasks: fileassoc
Root: HKCR; Subkey: "KlondikeArchive"; ValueType: string; ValueName: ""; ValueData: "Klondike Crinkle Archive"; Flags: uninsdeletekey; Tasks: fileassoc
Root: HKCR; Subkey: "KlondikeArchive\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\kc_file_icon.ico"; Tasks: fileassoc
Root: HKCR; Subkey: "KlondikeArchive\shell"; ValueType: string; ValueName: ""; ValueData: "open"; Tasks: fileassoc
Root: HKCR; Subkey: "KlondikeArchive\shell\open"; ValueType: string; ValueName: ""; ValueData: "&Open with Klondike Archiver"; Tasks: fileassoc
Root: HKCR; Subkey: "KlondikeArchive\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\KCrinkle.exe"" ""%1"""; Tasks: fileassoc

; Context menu for .kc files
Root: HKCR; Subkey: "KlondikeArchive\shell\uncrinkle"; ValueType: string; ValueName: ""; ValueData: "Uncrinkle with KC"; Tasks: fileassoc
Root: HKCR; Subkey: "KlondikeArchive\shell\uncrinkle\command"; ValueType: string; ValueName: ""; ValueData: """{app}\KCrinkle.exe"" ""%1"""; Tasks: fileassoc

; Add to "Open with" menu
Root: HKCR; Subkey: "Applications\KCrinkle.exe\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\KCrinkle.exe"" ""%1"""; Tasks: fileassoc
Root: HKCR; Subkey: "Applications\KCrinkle.exe"; ValueType: string; ValueName: "FriendlyAppName"; ValueData: "Klondike Archiver"; Tasks: fileassoc

[Run]
Filename: "{app}\KCrinkle.exe"; Description: "{cm:LaunchProgram,Klondike Archiver}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: files; Name: "{app}\*.log"

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Refresh shell to update file associations
    if IsTaskSelected('fileassoc') then
    begin
      RegWriteStringValue(HKEY_CURRENT_USER, 'Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.kc', 'Progid', 'KlondikeArchive');
    end;
  end;
end;

// Custom messages
[CustomMessages]
LaunchProgram=Launch %1
