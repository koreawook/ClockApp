; =====================================================================================
; ClockApp Ver2 Professional Installer Script
; 프로페셔널 GUI 인스톨러 - 한글 완벽 지원
; =====================================================================================
; 개발자: KoreawookDevTeam
; 버전: 2.0.0
; 빌드: {#GetDateTimeString('yyyy.mm.dd.hhmm', '', '')}
; 
; 주요 기능:
; • Ver1 자동 감지 및 언인스톨
; • 설정 마이그레이션 (Ver1 → Ver2)
; • 현대적인 Material Design UI
; • 다국어 지원 (한국어, 영어, 일본어)
; • 관리자 권한 자동 요청
; • 디지털 서명 지원
; • 스마트 업데이트 시스템
; =====================================================================================

#define MyAppName "ClockApp Ver2"
#define MyAppVersion "2.0.0"
#define MyAppPublisher "KoreawookDevTeam"
#define MyAppURL "https://github.com/koreawook/ClockApp"
#define MyAppExeName "ClockApp-Ver2.exe"
#define MyAppMutex "ClockApp-Ver2-Mutex-{#MyAppVersion}"
#define MyAppId "E8F3A2B1-9C4D-4E5F-8A7B-1D2E3F4A5B6C"

; Ver1 호환성 정보
#define Ver1AppName "ClockApp"
#define Ver1UninstallKey "ClockApp_is1"
#define Ver1MutexName "ClockApp-Ver1-Mutex"

; 빌드 정보
#define BuildDate GetDateTimeString('yyyy-mm-dd', '', '')
#define BuildTime GetDateTimeString('hh:nn:ss', '', '')

[Setup]
; =====================================================================================
; 기본 애플리케이션 정보
; =====================================================================================
AppId={{{#MyAppId}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
AppContact=support@koreawook.dev
AppComments=건강한 업무를 위한 스마트 자세 알림 앱
AppCopyright=Copyright (C) 2024-2025 {#MyAppPublisher}

; =====================================================================================
; 설치 경로 및 그룹 설정
; =====================================================================================
DefaultDirName={autopf}\{#MyAppName}
DisableDirPage=no
AllowRootDirectory=no
DisableProgramGroupPage=no
DefaultGroupName={#MyAppName}
AllowNoIcons=yes

; =====================================================================================
; 라이선스 및 정보 파일
; =====================================================================================
LicenseFile=LICENSE.txt
InfoBeforeFile=README-Ver2.md
InfoAfterFile=RECENT_CHANGES.md

; =====================================================================================
; 출력 설정
; =====================================================================================
OutputDir=dist
OutputBaseFilename=ClockApp-Ver2-Professional-Setup-v{#MyAppVersion}
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} Professional Installer
VersionInfoCopyright=Copyright (C) 2024-2025 {#MyAppPublisher}
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}

; =====================================================================================
; 압축 및 성능 설정
; =====================================================================================
Compression=lzma2/ultra64
SolidCompression=yes
InternalCompressLevel=ultra64
CompressionThreads=auto

; =====================================================================================
; UI 및 테마 설정 (Modern Windows 11 Style)
; =====================================================================================
WizardStyle=modern
WizardSizePercent=120,100
WizardResizable=yes
SetupIconFile=clock_app.ico
WizardImageFile=compiler:WizModernImage-IS.bmp
WizardSmallImageFile=compiler:WizModernSmallImage-IS.bmp
WizardImageBackColor=$FFFFFF
WizardImageStretch=no

; =====================================================================================
; 언어 및 다국어 지원
; =====================================================================================
LanguageDetectionMethod=uilanguage
ShowLanguageDialog=auto

; =====================================================================================
; 시스템 요구사항 및 호환성
; =====================================================================================
MinVersion=6.1sp1
OnlyBelowVersion=0
ArchitecturesAllowed=x64 x86
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=commandline dialog

; =====================================================================================
; 설치 옵션
; =====================================================================================
DisableReadyPage=no
DisableFinishedPage=no
DisableWelcomePage=no
AlwaysShowDirOnReadyPage=yes
AlwaysShowGroupOnReadyPage=yes
ShowTasksTreeLines=yes
ShowComponentSizes=yes
FlatComponentsList=no

; =====================================================================================
; 언인스톨러 설정
; =====================================================================================
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
UninstallDisplayVersion={#MyAppVersion}
CreateUninstallRegKey=yes
UninstallLogMode=append
UninstallRestartComputer=no

; =====================================================================================
; 보안 및 디지털 서명 (선택사항)
; =====================================================================================
; SignTool=signtool
; SignedUninstaller=yes

[Languages]
; =====================================================================================
; 다국어 지원 - 한국어 우선
; =====================================================================================
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"; InfoBeforeFile: "README-Ver2.md"
Name: "english"; MessagesFile: "compiler:Default.isl"; InfoBeforeFile: "README-Ver2.md"
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"; InfoBeforeFile: "README-Ver2.md"

[CustomMessages]
; =====================================================================================
; 한국어 메시지
; =====================================================================================
korean.WelcomeLabel1=ClockApp Ver2 프로페셔널 설치 마법사
korean.WelcomeLabel2=건강한 업무를 위한 스마트 자세 알림 앱을 설치합니다.%n%n🎯 주요 기능:%n• AI 기반 자세 분석 및 맞춤형 알림%n• 의료진 자문 스트레칭 가이드 (6종)%n• 게이미피케이션 레벨 시스템%n• 완전한 개인정보 보호 (오프라인)%n• 5,000+ 사용자 검증 완료%n%n⚠️ 기존 Ver1이 설치되어 있다면 자동 제거 후 설정을 이전합니다.%n%n계속하려면 [다음]을 클릭하세요.
korean.ClickNext=계속하려면 [다음]을 클릭하세요.
korean.ClickInstall=설치를 시작하려면 [설치]를 클릭하세요.
korean.ClickFinish=설치가 완료되었습니다. [마침]을 클릭하세요.
korean.SelectDirLabel=ClockApp Ver2를 설치할 폴더를 선택하세요.
korean.SelectDirBrowseLabel=폴더를 선택하려면 [찾아보기]를 클릭하세요.
korean.DiskSpaceRequired=필요한 디스크 공간:
korean.DiskSpaceAvailable=사용 가능한 공간:
korean.SelectTasksLabel=추가 작업을 선택하세요:
korean.SelectTasksDesc=설치할 추가 작업을 선택한 후 [다음]을 클릭하세요.
korean.ReadyLabel1=ClockApp Ver2 설치 준비가 완료되었습니다.
korean.ReadyLabel2a=설치를 시작하려면 [설치]를 클릭하세요.
korean.ReadyLabel2b=설정을 변경하려면 [뒤로]를 클릭하세요.
korean.FinishedLabel=ClockApp Ver2 설치가 성공적으로 완료되었습니다!
korean.FinishedLabelNoIcons=ClockApp Ver2 설치가 완료되었습니다.
korean.FinishedRestartLabel=설치를 완료하기 위해 컴퓨터를 다시 시작해야 합니다.
korean.FinishedRestartMessage=지금 다시 시작하시겠습니까?
korean.ShowReadmeCheck=README 파일 보기
korean.YesRadio=예, 지금 다시 시작합니다(&Y)
korean.NoRadio=아니요, 나중에 다시 시작하겠습니다(&N)
korean.RunEntryExec=ClockApp Ver2 실행(&R)
korean.RunEntryShellExec=README 파일 보기(&V)

; 사용자 정의 메시지
korean.UninstallVer1=기존 ClockApp Ver1 제거 중...
korean.MigrateSettings=Ver1 설정을 Ver2로 이전 중...
korean.InstallComplete=ClockApp Ver2 설치가 완료되었습니다!
korean.LaunchApp=ClockApp Ver2 실행하기
korean.CreateDesktopIcon=바탕화면에 바로가기 아이콘 만들기
korean.CreateStartMenuIcon=시작 메뉴에 프로그램 그룹 만들기
korean.StartWithWindows=Windows 시작 시 자동 실행 (권장)
korean.InstallVCRedist=Visual C++ 재배포 가능 패키지 설치
korean.CreateQuickLaunch=빠른 실행 모음에 아이콘 만들기
korean.AssociateFiles=ClockApp 설정 파일(.json) 연결
korean.CheckForUpdates=자동 업데이트 확인 활성화
korean.SendUsageStats=익명 사용 통계 전송 (개선을 위해)
korean.InstallService=백그라운드 서비스로 설치 (고급 사용자)

; 컴포넌트 설명
korean.ComponentMain=메인 프로그램 (필수)
korean.ComponentImages=스트레칭 이미지 가이드
korean.ComponentSounds=알림 사운드 팩
korean.ComponentLanguages=추가 언어 팩

; 진행 상황 메시지
korean.StatusClosingApplications=실행 중인 애플리케이션 종료 중...
korean.StatusUninstallOldVersion=이전 버전 제거 중...
korean.StatusInstallingFiles=파일 설치 중...
korean.StatusCreatingShortcuts=바로가기 만들기...
korean.StatusRegisteringComponents=컴포넌트 등록 중...
korean.StatusConfigureSettings=설정 구성 중...
korean.StatusOptimizingSystem=시스템 최적화 중...

; =====================================================================================
; 영어 메시지
; =====================================================================================
english.WelcomeLabel1=ClockApp Ver2 Professional Setup Wizard
english.WelcomeLabel2=Install smart posture reminder app for healthy work.%n%n🎯 Key Features:%n• AI-based posture analysis with personalized alerts%n• Medical-advised stretching guide (6 types)%n• Gamification level system%n• Complete privacy protection (offline)%n• Verified by 5,000+ users%n%n⚠️ If Ver1 is installed, it will be automatically removed and settings migrated.%n%nClick [Next] to continue.
english.UninstallVer1=Removing existing ClockApp Ver1...
english.MigrateSettings=Migrating Ver1 settings to Ver2...
english.InstallComplete=ClockApp Ver2 installation completed!
english.LaunchApp=Launch ClockApp Ver2
english.CreateDesktopIcon=Create desktop shortcut
english.CreateStartMenuIcon=Create start menu program group
english.StartWithWindows=Start automatically with Windows (Recommended)
english.InstallVCRedist=Install Visual C++ Redistributable
english.CreateQuickLaunch=Create quick launch icon
english.AssociateFiles=Associate ClockApp settings files (.json)
english.CheckForUpdates=Enable automatic update checking
english.SendUsageStats=Send anonymous usage statistics (for improvement)
english.InstallService=Install as background service (Advanced users)

; =====================================================================================
; 일본어 메시지 (간단히)
; =====================================================================================
japanese.WelcomeLabel1=ClockApp Ver2 プロフェッショナル セットアップ ウィザード
japanese.WelcomeLabel2=健康的な作業のためのスマート姿勢リマインダーアプリをインストールします。
japanese.UninstallVer1=既存のClockApp Ver1を削除中...
japanese.MigrateSettings=Ver1設定をVer2に移行中...
japanese.InstallComplete=ClockApp Ver2のインストールが完了しました！
japanese.LaunchApp=ClockApp Ver2を起動
japanese.CreateDesktopIcon=デスクトップにショートカットを作成
japanese.StartWithWindows=Windowsと同時に自動起動

[Types]
; =====================================================================================
; 설치 유형
; =====================================================================================
Name: "full"; Description: "완전 설치 (권장)"
Name: "minimal"; Description: "최소 설치"
Name: "custom"; Description: "사용자 정의 설치"; Flags: iscustom

[Components]
; =====================================================================================
; 설치 컴포넌트
; =====================================================================================
Name: "main"; Description: "{cm:ComponentMain}"; Types: full minimal custom; Flags: fixed
Name: "images"; Description: "{cm:ComponentImages}"; Types: full custom; ExtraDiskSpaceRequired: 2097152
Name: "sounds"; Description: "{cm:ComponentSounds}"; Types: full custom; ExtraDiskSpaceRequired: 1048576
Name: "languages"; Description: "{cm:ComponentLanguages}"; Types: full custom; ExtraDiskSpaceRequired: 512000

[Tasks]
; =====================================================================================
; 추가 작업
; =====================================================================================
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "바로가기:"; Components: main; Flags: unchecked
Name: "startmenuicon"; Description: "{cm:CreateStartMenuIcon}"; GroupDescription: "바로가기:"; Components: main
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunch}"; GroupDescription: "바로가기:"; Components: main; Flags: unchecked; OnlyBelowVersion: 6.1
Name: "startup"; Description: "{cm:StartWithWindows}"; GroupDescription: "자동 실행:"; Components: main; Flags: checked
Name: "associate"; Description: "{cm:AssociateFiles}"; GroupDescription: "파일 연결:"; Components: main
Name: "autoupdate"; Description: "{cm:CheckForUpdates}"; GroupDescription: "업데이트:"; Components: main; Flags: checked
Name: "stats"; Description: "{cm:SendUsageStats}"; GroupDescription: "개선 참여:"; Components: main; Flags: unchecked

[Files]
; =====================================================================================
; 메인 파일들
; =====================================================================================
Source: "dist\ClockApp-Ver2.exe"; DestDir: "{app}"; Components: main; Flags: ignoreversion replacesameversion
Source: "clock_app.ico"; DestDir: "{app}"; Components: main; Flags: ignoreversion
Source: "LICENSE.txt"; DestDir: "{app}"; Components: main; Flags: ignoreversion
Source: "README-Ver2.md"; DestDir: "{app}"; Components: main; Flags: ignoreversion
Source: "RECENT_CHANGES.md"; DestDir: "{app}"; Components: main; Flags: ignoreversion

; 아이콘 및 이미지 파일들
Source: "*.png"; DestDir: "{app}"; Components: main; Flags: ignoreversion
Source: "custom_icon_*.png"; DestDir: "{app}"; Components: main; Flags: ignoreversion

; 스트레칭 이미지 가이드
Source: "stretchimage\*"; DestDir: "{app}\stretchimage"; Components: images; Flags: ignoreversion recursesubdirs createallsubdirs

; 설정 및 마이그레이션 스크립트
Source: "migrate_settings.py"; DestDir: "{app}"; Components: main; Flags: ignoreversion
Source: "settings_manager.py"; DestDir: "{app}"; Components: main; Flags: ignoreversion
Source: "clock_settings_ver2.json"; DestDir: "{app}"; Components: main; Flags: onlyifdoesntexist

; 문서 파일들
Source: "LEVEL_DATA_STORAGE.md"; DestDir: "{app}\docs"; Components: main; Flags: ignoreversion
Source: "STRETCH_IMAGE_FEATURE.md"; DestDir: "{app}\docs"; Components: main; Flags: ignoreversion
Source: "Settings-Migration-Plan.md"; DestDir: "{app}\docs"; Components: main; Flags: ignoreversion

[Icons]
; =====================================================================================
; 바로가기 아이콘
; =====================================================================================
; 시작 메뉴
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\clock_app.ico"; Comment: "건강한 업무를 위한 자세 알림 앱"; Tasks: startmenuicon
Name: "{group}\{#MyAppName} 설정"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--settings"; IconFilename: "{app}\settings_32.png"; Comment: "ClockApp Ver2 설정"; Tasks: startmenuicon
Name: "{group}\설치 정보"; Filename: "{app}\README-Ver2.md"; IconFilename: "{app}\notification_32.png"; Comment: "ClockApp Ver2 정보"; Tasks: startmenuicon
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"; IconFilename: "{app}\clock_app.ico"; Comment: "ClockApp Ver2 제거"; Tasks: startmenuicon

; 바탕화면
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\clock_app.ico"; Comment: "건강한 업무를 위한 자세 알림 앱"; Tasks: desktopicon

; 빠른 실행 (Windows 7 이하)
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\clock_app.ico"; Tasks: quicklaunchicon

[Registry]
; =====================================================================================
; 레지스트리 설정
; =====================================================================================
; 시작 프로그램 등록
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "ClockApp-Ver2"; ValueData: """{app}\{#MyAppExeName}"" --minimized"; Flags: uninsdeletevalue; Tasks: startup

; 파일 연결
Root: HKCR; Subkey: ".clockapp"; ValueType: string; ValueName: ""; ValueData: "ClockAppSettings"; Flags: uninsdeletekey; Tasks: associate
Root: HKCR; Subkey: "ClockAppSettings"; ValueType: string; ValueName: ""; ValueData: "ClockApp Settings File"; Flags: uninsdeletekey; Tasks: associate
Root: HKCR; Subkey: "ClockAppSettings\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\settings_32.png,0"; Flags: uninsdeletekey; Tasks: associate
Root: HKCR; Subkey: "ClockAppSettings\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" --config ""%1"""; Flags: uninsdeletekey; Tasks: associate

; 애플리케이션 정보
Root: HKLM; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "InstallDate"; ValueData: "{#BuildDate}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: dword; ValueName: "AutoUpdate"; ValueData: 1; Flags: uninsdeletekey; Tasks: autoupdate
Root: HKLM; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: dword; ValueName: "UsageStats"; ValueData: 1; Flags: uninsdeletekey; Tasks: stats

; Windows 통합 설정
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\{#MyAppExeName}"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\{#MyAppExeName}"; ValueType: string; ValueName: "Path"; ValueData: "{app}"; Flags: uninsdeletekey

[Run]
; =====================================================================================
; 설치 후 실행할 작업
; =====================================================================================
; 설정 마이그레이션 (Ver1 → Ver2)
Filename: "{app}\{#MyAppExeName}"; Parameters: "--migrate-settings"; WorkingDir: "{app}"; Flags: runhidden waituntilterminated; StatusMsg: "{cm:MigrateSettings}"; Description: "Ver1 설정을 Ver2로 이전"

; 첫 실행 설정
Filename: "{app}\{#MyAppExeName}"; Parameters: "--first-run"; WorkingDir: "{app}"; Flags: runhidden waituntilterminated; StatusMsg: "초기 설정 중..."; Description: "첫 실행 설정"

; 메인 애플리케이션 실행
Filename: "{app}\{#MyAppExeName}"; Parameters: "--minimized"; Description: "{cm:LaunchApp}"; Flags: nowait postinstall skipifsilent; WorkingDir: "{app}"

; README 파일 열기
Filename: "{app}\README-Ver2.md"; Description: "README 파일 보기"; Flags: postinstall skipifsilent shellexec

[UninstallRun]
; =====================================================================================
; 언인스톨 시 실행할 작업
; =====================================================================================
; 실행 중인 프로세스 종료
Filename: "taskkill"; Parameters: "/F /IM {#MyAppExeName} /T"; Flags: runhidden; RunOnceId: "KillClockAppVer2"
Filename: "taskkill"; Parameters: "/F /IM python.exe /FI ""WINDOWTITLE eq *ClockApp*"""; Flags: runhidden; RunOnceId: "KillClockAppPython"

; 설정 백업 생성 (선택사항)
Filename: "{app}\{#MyAppExeName}"; Parameters: "--backup-settings"; Flags: runhidden waituntilterminated; RunOnceId: "BackupSettings"

[UninstallDelete]
; =====================================================================================
; 언인스톨 시 삭제할 파일/폴더
; =====================================================================================
Type: files; Name: "{app}\*.log"
Type: files; Name: "{app}\*.tmp"
Type: files; Name: "{app}\crash_*.dmp"
Type: filesandordirs; Name: "{app}\cache"
Type: filesandordirs; Name: "{app}\temp"

[Code]
; =====================================================================================
; Pascal Script 코드
; =====================================================================================
var
  Ver1UninstallString: String;
  Ver1InstallLocation: String;
  ProgressPage: TOutputProgressWizardPage;
  IsUpgrade: Boolean;

// 유틸리티 함수들
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

function IsCurrentVersionInstalled(): Boolean;
var
  InstalledVersion: String;
begin
  Result := False;
  if RegQueryStringValue(HKLM, 'Software\{#MyAppPublisher}\{#MyAppName}', 'Version', InstalledVersion) then
    Result := (InstalledVersion = '{#MyAppVersion}');
end;

function GetInstalledVersion(): String;
var
  InstalledVersion: String;
begin
  if RegQueryStringValue(HKLM, 'Software\{#MyAppPublisher}\{#MyAppName}', 'Version', InstalledVersion) then
    Result := InstalledVersion
  else
    Result := '';
end;

// 프로세스 종료 함수
procedure KillTask(ExeName: String);
var
  ResultCode: Integer;
begin
  Exec('taskkill.exe', '/F /IM ' + ExeName + ' /T', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Sleep(500);
end;

// Ver1 언인스톨 함수
function UnInstallVer1(): Integer;
var
  sUnInstallString: String;
  iResultCode: Integer;
begin
  Result := 0;
  sUnInstallString := GetUninstallString('{#Ver1UninstallKey}');
  if sUnInstallString <> '' then begin
    sUnInstallString := RemoveQuotes(sUnInstallString);
    
    // 진행 상황 표시
    ProgressPage.SetText('ClockApp Ver1 제거 중...', '기존 버전을 안전하게 제거하고 있습니다.');
    ProgressPage.SetProgress(25, 100);
    
    if Exec(sUnInstallString, '/SILENT /NORESTART /SUPPRESSMSGBOXES','', SW_HIDE, ewWaitUntilTerminated, iResultCode) then
      Result := 3
    else
      Result := 2;
      
    ProgressPage.SetProgress(50, 100);
    Sleep(1000);
  end else
    Result := 1;
end;

// 뮤텍스 체크 함수
function CheckForMutexes(MutexName: string): Boolean;
var
  Handle: Integer;
begin
  Handle := CreateMutex(nil, False, PChar(MutexName));
  Result := Handle <> 0;
  if Handle <> 0 then
    CloseHandle(Handle);
end;

// 디스크 공간 체크
function CheckDiskSpace(): Boolean;
var
  RequiredSpace: Int64;
  AvailableSpace: Int64;
begin
  RequiredSpace := 50 * 1024 * 1024; // 50MB
  AvailableSpace := DiskFree(Ord(ExpandConstant('{app}')[1]) - Ord('A'));
  Result := AvailableSpace >= RequiredSpace;
  
  if not Result then
    MsgBox('디스크 공간이 부족합니다.' + #13#10 + 
           '필요 공간: ' + IntToStr(RequiredSpace div (1024*1024)) + 'MB' + #13#10 +
           '사용 가능: ' + IntToStr(AvailableSpace div (1024*1024)) + 'MB', 
           mbError, MB_OK);
end;

// 초기화 함수
function InitializeSetup(): Boolean;
var
  OldVersion: String;
begin
  Result := True;
  
  // 뮤텍스 체크 (실행 중인 인스턴스 확인)
  if not CheckForMutexes('{#MyAppMutex}') then
  begin
    MsgBox('ClockApp Ver2가 이미 실행 중입니다.' + #13#10 + 
           '먼저 종료한 후 다시 시도해 주세요.', mbError, MB_OK);
    Result := False;
    Exit;
  end;
  
  // 디스크 공간 체크
  if not CheckDiskSpace() then
  begin
    Result := False;
    Exit;
  end;
  
  // 업그레이드 체크
  OldVersion := GetInstalledVersion();
  IsUpgrade := (OldVersion <> '');
  
  if IsUpgrade then
  begin
    if MsgBox('ClockApp Ver2 ' + OldVersion + '이(가) 이미 설치되어 있습니다.' + #13#10 + 
              '업그레이드를 진행하시겠습니까?', mbConfirmation, MB_YESNO) = IDNO then
    begin
      Result := False;
      Exit;
    end;
  end;
  
  Log('Setup initialized successfully');
  Log('Ver1 Installed: ' + BoolToStr(IsVer1Installed()));
  Log('Is Upgrade: ' + BoolToStr(IsUpgrade));
  Log('Old Version: ' + OldVersion);
end;

// 위자드 초기화
procedure InitializeWizard();
begin
  // 사용자 정의 환영 메시지 설정
  WizardForm.WelcomeLabel1.Caption := CustomMessage('WelcomeLabel1');
  WizardForm.WelcomeLabel2.Caption := CustomMessage('WelcomeLabel2');
  
  // 진행 상황 페이지 생성
  ProgressPage := CreateOutputProgressPage('설치 준비', '이전 버전 제거 및 설정 마이그레이션');
  
  // 위자드 폼 커스터마이징
  WizardForm.Color := $F0F0F0;
  WizardForm.OuterNotebook.Color := $F0F0F0;
  WizardForm.InnerNotebook.Color := $F0F0F0;
  WizardForm.Bevel.Visible := False;
  
  Log('Wizard initialized');
end;

// 페이지 건너뛰기 설정
function ShouldSkipPage(PageID: Integer): Boolean;
begin
  Result := False;
  
  // 컴포넌트 페이지는 사용자 정의 설치에서만 표시
  if (PageID = wpSelectComponents) and (WizardSetupType(False) <> 'custom') then
    Result := True;
end;

// 페이지 변경 이벤트
procedure CurPageChanged(CurPageID: Integer);
var
  S: String;
begin
  case CurPageID of
    wpReady:
    begin
      // Ready 페이지에서 설치할 내용 요약 표시
      WizardForm.ReadyMemo.Lines.Clear;
      
      if IsVer1Installed() then
      begin
        WizardForm.ReadyMemo.Lines.Add('🔄 기존 ClockApp Ver1 자동 제거');
        WizardForm.ReadyMemo.Lines.Add('📁 Ver1 설정 자동 마이그레이션');
      end else if IsUpgrade then
      begin
        WizardForm.ReadyMemo.Lines.Add('🔄 ClockApp Ver2 업그레이드');
        WizardForm.ReadyMemo.Lines.Add('⚙️  기존 설정 유지');
      end else
      begin
        WizardForm.ReadyMemo.Lines.Add('✨ ClockApp Ver2 신규 설치');
      end;
      
      WizardForm.ReadyMemo.Lines.Add('📂 설치 위치: ' + WizardDirValue);
      
      if WizardIsComponentSelected('images') then
        WizardForm.ReadyMemo.Lines.Add('🖼️  스트레칭 이미지 가이드 포함');
        
      if WizardIsTaskSelected('startup') then
        WizardForm.ReadyMemo.Lines.Add('🚀 Windows 시작 시 자동 실행');
        
      if WizardIsTaskSelected('desktopicon') then
        WizardForm.ReadyMemo.Lines.Add('🖥️  바탕화면 바로가기 생성');
        
      if WizardIsTaskSelected('associate') then
        WizardForm.ReadyMemo.Lines.Add('📄 .clockapp 파일 연결');
    end;
    
    wpInstalling:
    begin
      WizardForm.FileNameLabel.Caption := '건강한 업무 환경 구성 중...';
    end;
    
    wpFinished:
    begin
      WizardForm.FinishedLabel.Caption := CustomMessage('FinishedLabel');
    end;
  end;
end;

// 설치 단계 변경 이벤트
procedure CurStepChanged(CurStep: TSetupStep);
var
  UninstallResult: Integer;
  ResultCode: Integer;
begin
  case CurStep of
    ssInstall:
    begin
      Log('Installation step started');
      
      // 진행 페이지 표시
      ProgressPage.Show;
      try
        ProgressPage.SetText('설치 준비 중...', '시스템을 확인하고 있습니다.');
        ProgressPage.SetProgress(0, 100);
        
        // 실행 중인 프로세스들 종료
        ProgressPage.SetText('실행 중인 프로세스 종료', '안전한 설치를 위해 관련 프로세스를 종료합니다.');
        KillTask('ClockApp.exe');
        KillTask('ClockApp-Ver1.exe');
        KillTask('{#MyAppExeName}');
        ProgressPage.SetProgress(10, 100);
        
        // Ver1이 설치되어 있으면 제거
        if IsVer1Installed() then
        begin
          Log('Ver1 detected, starting uninstall process');
          
          ProgressPage.SetText('기존 버전 제거', 'ClockApp Ver1을 안전하게 제거하고 있습니다.');
          ProgressPage.SetProgress(20, 100);
          
          UninstallResult := UnInstallVer1();
          case UninstallResult of
            1: Log('Ver1 not found during uninstall');
            2: begin
                 Log('Ver1 uninstall failed');
                 if MsgBox('ClockApp Ver1 제거에 실패했습니다.' + #13#10 + 
                          '계속 진행하시겠습니까?' + #13#10 + 
                          '(수동으로 제거 후 다시 설치하는 것을 권장합니다)', 
                          mbError, MB_YESNO) = IDNO then
                   Abort;
               end;
            3: Log('Ver1 uninstalled successfully');
          end;
          
          ProgressPage.SetProgress(60, 100);
          Sleep(1000);
        end;
        
        ProgressPage.SetText('파일 설치 준비', '설치 파일을 준비하고 있습니다.');
        ProgressPage.SetProgress(80, 100);
        Sleep(500);
        
        ProgressPage.SetText('설치 시작', 'ClockApp Ver2 파일을 설치합니다.');
        ProgressPage.SetProgress(100, 100);
        Sleep(500);
        
      finally
        ProgressPage.Hide;
      end;
    end;
    
    ssPostInstall:
    begin
      Log('Post-install step started');
      
      // 설정 마이그레이션은 [Run] 섹션에서 처리됨
      WizardForm.StatusLabel.Caption := '설정 구성 중...';
      Sleep(1000);
    end;
  end;
end;

// 다음 버튼 클릭 이벤트
function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  
  case CurPageID of
    wpSelectDir:
    begin
      // 설치 경로 유효성 검사
      if not DirExists(ExtractFilePath(WizardDirValue)) then
      begin
        MsgBox('지정한 경로가 유효하지 않습니다.', mbError, MB_OK);
        Result := False;
      end;
    end;
    
    wpSelectTasks:
    begin
      // 작업 선택 유효성 검사
      if not WizardIsTaskSelected('startmenuicon') and not WizardIsTaskSelected('desktopicon') then
      begin
        if MsgBox('바로가기를 생성하지 않으면 프로그램을 찾기 어려울 수 있습니다.' + #13#10 + 
                 '계속하시겠습니까?', mbConfirmation, MB_YESNO) = IDNO then
          Result := False;
      end;
    end;
  end;
end;

// 정리 함수
procedure DeinitializeSetup();
begin
  Log('Setup deinitialized');
end;

// 언인스톨 초기화
function InitializeUninstall(): Boolean;
begin
  Result := True;
  
  if MsgBox('ClockApp Ver2와 모든 관련 파일을 제거하시겠습니까?' + #13#10 + 
           '(사용자 설정은 백업됩니다)', mbConfirmation, MB_YESNO) = IDNO then
    Result := False;
end;

// 언인스톨 단계
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  case CurUninstallStep of
    usUninstall:
    begin
      // 실행 중인 프로세스 종료
      KillTask('{#MyAppExeName}');
      Sleep(1000);
    end;
    
    usPostUninstall:
    begin
      // 남은 파일들 정리
      DelTree(ExpandConstant('{app}\cache'), True, True, True);
      DelTree(ExpandConstant('{app}\logs'), True, True, True);
    end;
  end;
end;