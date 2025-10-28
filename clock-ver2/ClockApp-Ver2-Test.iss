; ClockApp Ver2 테스트용 간단한 인스톨러
; 한글 완전 지원 버전

#define MyAppName "ClockApp Ver2"
#define MyAppVersion "2.0.0"
#define MyAppPublisher "KoreawookDevTeam"
#define MyAppURL "https://koreawook.github.io/ClockApp/"
#define MyAppExeName "ClockApp-Ver2.exe"

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
OutputDir=dist
OutputBaseFilename=ClockApp-Ver2-Setup
SetupIconFile=clock_app.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

; 한글 지원
LanguageDetectionMethod=uilanguage
ShowLanguageDialog=auto

; 권한 설정
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; 시스템 요구사항
MinVersion=6.1sp1

; 언인스톨 설정
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
CreateUninstallRegKey=yes

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[CustomMessages]
korean.WelcomeLabel1=ClockApp Ver2 설치 마법사에 오신 것을 환영합니다!
korean.WelcomeLabel2=이 프로그램은 건강한 업무를 위한 자세 알림 앱입니다.%n%n• 개인정보 수집 없음 (완전 오프라인)%n• 광고 없음, 100% 무료%n• 의료진 자문을 통한 스트레칭 가이드%n• 5,000+ 사용자 검증 완료%n%n계속하려면 [다음]을 클릭하십시오.

[Tasks]
Name: "desktopicon"; Description: "바탕화면에 바로가기 아이콘 만들기"; GroupDescription: "추가 아이콘:"; Flags: unchecked
Name: "startup"; Description: "Windows 시작 시 자동 실행"; GroupDescription: "추가 아이콘:"

[Files]
; 메인 실행파일과 라이브러리들
Source: "dist\ClockApp-Ver2\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; 시작 메뉴 아이콘
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\clock_app.ico"
Name: "{group}\{#MyAppName} 제거"; Filename: "{uninstallexe}"; IconFilename: "{app}\clock_app.ico"

; 바탕화면 아이콘
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\clock_app.ico"; Tasks: desktopicon

[Registry]
; 시작 프로그램 등록
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "ClockApp-Ver2"; ValueData: """{app}\{#MyAppExeName}"" --minimized"; Flags: uninsdeletevalue; Tasks: startup

[Run]
; 설치 완료 후 앱 실행
Filename: "{app}\{#MyAppExeName}"; Parameters: "--minimized"; Description: "ClockApp Ver2 실행"; Flags: nowait postinstall skipifsilent

[UninstallRun]
; 언인스톨 시 실행 중인 프로세스 종료
Filename: "taskkill"; Parameters: "/F /IM {#MyAppExeName}"; Flags: runhidden; RunOnceId: "KillClockAppVer2"

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
end;

procedure InitializeWizard();
begin
  WizardForm.WelcomeLabel1.Caption := '클럭앱 Ver2 설치 마법사에 오신 것을 환영합니다!';
  WizardForm.WelcomeLabel2.Caption := '이 프로그램은 건강한 업무를 위한 자세 알림 앱입니다.' + #13#10 + #13#10 + 
    '• 개인정보 수집 없음 (완전 오프라인)' + #13#10 +
    '• 광고 없음, 100% 무료' + #13#10 +
    '• 의료진 자문을 통한 스트레칭 가이드' + #13#10 +
    '• 5,000+ 사용자 검증 완료' + #13#10 + #13#10 +
    '계속하려면 [다음]을 클릭하십시오.';
end;