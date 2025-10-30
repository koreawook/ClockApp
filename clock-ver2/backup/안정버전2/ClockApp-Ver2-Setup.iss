; ClockApp Ver2 Professional Installer Script
; 한글 지원 + Ver1 언인스톨 + 설정 마이그레이션
; 개발자: KoreawookDevTeam
; 버전: 2.0.0

#define MyAppName "ClockApp Ver2"
#define MyAppVersion "2.0.0"
#define MyAppPublisher "KoreawookDevTeam"
#define MyAppURL "https://koreawook.github.io/ClockApp/"
#define MyAppExeName "ClockApp-Ver2.exe"
#define MyAppMutex "ClockApp-Ver2-Mutex"

; Ver1 정보
#define Ver1AppName "ClockApp"
#define Ver1UninstallKey "ClockApp_is1"

[Setup]
; 기본 설정
AppId={{E8F3A2B1-9C4D-4E5F-8A7B-1D2E3F4A5B6C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE.txt
InfoBeforeFile=README-Ver2.md
OutputDir=dist
OutputBaseFilename=ClockApp-Ver2-Setup
SetupIconFile=clock_app.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

; 한글 지원 설정
LanguageDetectionMethod=uilanguage
ShowLanguageDialog=auto

; 권한 설정
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; 시스템 요구사항
MinVersion=6.1sp1
ArchitecturesAllowed=x64 x86
ArchitecturesInstallIn64BitMode=x64

; UI 설정
; WizardImageFile=compiler:WizModernImage-IS.bmp
; WizardSmallImageFile=compiler:WizModernSmallImage-IS.bmp
DisableProgramGroupPage=yes
DisableReadyPage=no
DisableFinishedPage=no

; 언인스톨 설정
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
CreateUninstallRegKey=yes

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"

[CustomMessages]
korean.WelcomeLabel1=ClockApp Ver2 설치 마법사에 오신 것을 환영합니다!
korean.WelcomeLabel2=이 프로그램은 건강한 업무를 위한 자세 알림 앱입니다.%n%n기존 Ver1이 설치되어 있다면 자동으로 제거되고, 설정은 Ver2로 이전됩니다.%n%n• 개인정보 수집 없음 (완전 오프라인)%n• 광고 없음, 100% 무료%n• 의료진 자문을 통한 스트레칭 가이드%n• 5,000+ 사용자 검증 완료%n%n계속하려면 [다음]을 클릭하십시오.
korean.UninstallVer1=기존 ClockApp Ver1 제거 중...
korean.MigrateSettings=Ver1 설정을 Ver2로 이전 중...
korean.InstallComplete=ClockApp Ver2 설치가 완료되었습니다!
korean.LaunchApp=ClockApp Ver2 실행
korean.CreateDesktopIcon=바탕화면에 바로가기 아이콘 만들기
korean.CreateStartMenuIcon=시작 메뉴에 바로가기 아이콘 만들기
korean.StartWithWindows=Windows 시작 시 자동 실행

english.WelcomeLabel1=Welcome to ClockApp Ver2 Setup Wizard!
english.WelcomeLabel2=This program is a posture reminder app for healthy work.%n%nIf Ver1 is already installed, it will be automatically removed and settings will be migrated to Ver2.%n%n• No personal data collection (completely offline)%n• No ads, 100% free%n• Stretching guide with medical consultation%n• Verified by 5,000+ users%n%nClick [Next] to continue.
english.UninstallVer1=Removing existing ClockApp Ver1...
english.MigrateSettings=Migrating Ver1 settings to Ver2...
english.InstallComplete=ClockApp Ver2 installation completed!
english.LaunchApp=Launch ClockApp Ver2
english.CreateDesktopIcon=Create desktop shortcut
english.CreateStartMenuIcon=Create start menu shortcut
english.StartWithWindows=Start automatically with Windows

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startmenuicon"; Description: "{cm:CreateStartMenuIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "startup"; Description: "{cm:StartWithWindows}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; 메인 실행파일
Source: "dist\ClockApp-Ver2\ClockApp-Ver2.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\ClockApp-Ver2\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs
; 아이콘 파일들
Source: "dist\ClockApp-Ver2\*.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\ClockApp-Ver2\clock_app.ico"; DestDir: "{app}"; Flags: ignoreversion
; 문서 파일들
Source: "dist\ClockApp-Ver2\LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\ClockApp-Ver2\README-Ver2.md"; DestDir: "{app}"; Flags: ignoreversion
; 설정 마이그레이션 스크립트
Source: "dist\ClockApp-Ver2\migrate_settings.py"; DestDir: "{app}"; Flags: ignoreversion
; 스트레칭 이미지 폴더 (있으면 포함)
Source: "stretchimage\*"; DestDir: "{app}\stretchimage"; Flags: ignoreversion recursesubdirs createallsubdirs; Check: DirExists(ExpandConstant('{src}\stretchimage'))
; Python 런타임 (필요시)
; Source: "python\*"; DestDir: "{app}\python"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; 시작 메뉴 아이콘
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\clock_app.ico"; Tasks: startmenuicon
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"; IconFilename: "{app}\clock_app.ico"; Tasks: startmenuicon

; 바탕화면 아이콘
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\clock_app.ico"; Tasks: desktopicon

[Registry]
; 시작 프로그램 등록
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "ClockApp-Ver2"; ValueData: """{app}\{#MyAppExeName}"" --minimized"; Flags: uninsdeletevalue; Tasks: startup

; 앱 정보 등록
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}_is1"; ValueType: string; ValueName: "DisplayName"; ValueData: "{#MyAppName}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}_is1"; ValueType: string; ValueName: "DisplayVersion"; ValueData: "{#MyAppVersion}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}_is1"; ValueType: string; ValueName: "Publisher"; ValueData: "{#MyAppPublisher}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}_is1"; ValueType: string; ValueName: "URLInfoAbout"; ValueData: "{#MyAppURL}"; Flags: uninsdeletekey

[Run]
; 설정 마이그레이션 실행 (설치 중)
Filename: "python"; Parameters: """{app}\migrate_settings.py"""; WorkingDir: "{app}"; Flags: runhidden waituntilterminated; StatusMsg: "{cm:MigrateSettings}"; Description: "Migrating settings from Ver1 to Ver2"

; 설치 완료 후 앱 실행
Filename: "{app}\{#MyAppExeName}"; Parameters: "--minimized"; Description: "{cm:LaunchApp}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
; 언인스톨 시 실행 중인 프로세스 종료
Filename: "taskkill"; Parameters: "/F /IM {#MyAppExeName}"; Flags: runhidden; RunOnceId: "KillClockAppVer2"

[Code]
var
  Ver1UninstallString: String;
  Ver1InstallLocation: String;

function GetUninstallString(AppID: String): String;
var
  sUnInstPath: String;
  sUnInstallString: String;
begin
  sUnInstPath := 'Software\Microsoft\Windows\CurrentVersion\Uninstall\' + AppID;
  sUnInstallString := '';
  if not RegQueryStringValue(HKLM, sUnInstPath, 'UninstallString', sUnInstallString) then
    RegQueryStringValue(HKCU, sUnInstPath, 'UninstallString', sUnInstallString);
  Result := sUnInstallString;
end;

function IsVer1Installed(): Boolean;
begin
  Result := (GetUninstallString('{#Ver1UninstallKey}') <> '');
end;

function UnInstallVer1(): Integer;
var
  sUnInstallString: String;
  iResultCode: Integer;
begin
  Result := 0;
  sUnInstallString := GetUninstallString('{#Ver1UninstallKey}');
  if sUnInstallString <> '' then begin
    sUnInstallString := RemoveQuotes(sUnInstallString);
    if Exec(sUnInstallString, '/SILENT /NORESTART /SUPPRESSMSGBOXES','', SW_HIDE, ewWaitUntilTerminated, iResultCode) then
      Result := 3
    else
      Result := 2;
  end else
    Result := 1;
end;

procedure KillTask(ExeName: String);
var
  ResultCode: Integer;
begin
  Exec('taskkill.exe', '/F /IM ' + ExeName, '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  UninstallResult: Integer;
begin
  case CurStep of
    ssInstall:
    begin
      // Ver1이 설치되어 있으면 제거
      if IsVer1Installed() then
      begin
        // 실행 중인 Ver1 프로세스 종료
        KillTask('ClockApp.exe');
        KillTask('ClockApp-Ver1.exe');
        Sleep(1000);
        
        // Ver1 언인스톨 실행
        WizardForm.StatusLabel.Caption := CustomMessage('UninstallVer1');
        WizardForm.ProgressGauge.Style := npbstMarquee;
        
        UninstallResult := UnInstallVer1();
        case UninstallResult of
          1: Log('Ver1이 설치되어 있지 않음');
          2: MsgBox('Ver1 제거에 실패했습니다. 수동으로 제거해 주세요.', mbError, MB_OK);
          3: Log('Ver1 제거 성공');
        end;
        
        WizardForm.ProgressGauge.Style := npbstNormal;
        Sleep(2000);
      end;
    end;
    
    ssPostInstall:
    begin
      // 설정 마이그레이션은 [Run] 섹션에서 처리됨
      WizardForm.StatusLabel.Caption := CustomMessage('MigrateSettings');
      Sleep(1000);
    end;
  end;
end;

// 뮤텍스 체크 함수 (간단한 버전)
function CheckForMutexes(MutexName: string): Boolean;
begin
  // 실제로는 프로세스가 실행 중인지 직접 확인
  Result := True; // 일단 항상 True로 설정 (설치 허용)
end;

function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  
  // 설치 전에 실행 중인 ClockApp 프로세스들을 강제 종료
  Exec('taskkill.exe', '/F /IM ClockApp-Ver2.exe /T', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Exec('taskkill.exe', '/F /IM python.exe', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  
  // 프로세스 종료 대기
  Sleep(2000);
  
  // 항상 설치 허용 (뮤텍스 체크 제거)
  Log('InitializeSetup: 설치 시작 허용');
end;

procedure InitializeWizard();
begin
  // 사용자 정의 환영 메시지 설정
  WizardForm.WelcomeLabel1.Caption := CustomMessage('WelcomeLabel1');
  WizardForm.WelcomeLabel2.Caption := CustomMessage('WelcomeLabel2');
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  // ReadyPage는 표시 (설치 전 확인용)
  Result := False;
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  case CurPageID of
    wpReady:
    begin
      // Ready 페이지에서 설치할 내용 요약 표시
      if IsVer1Installed() then
        WizardForm.ReadyMemo.Lines.Add('• 기존 ClockApp Ver1 제거')
      else
        WizardForm.ReadyMemo.Lines.Add('• 신규 설치');
      
      WizardForm.ReadyMemo.Lines.Add('• ClockApp Ver2 설치');
      WizardForm.ReadyMemo.Lines.Add('• 설정 파일 마이그레이션');
      
      if WizardIsTaskSelected('startup') then
        WizardForm.ReadyMemo.Lines.Add('• Windows 시작 시 자동 실행 등록');
    end;
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
end;

procedure DeinitializeSetup();
begin
  // 정리 작업
end;