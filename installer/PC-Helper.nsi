Unicode true
Name "PC Helper"
Caption "PC Helper"
OutFile "PC-Helper-Setup.exe"
InstallDir "$PROGRAMFILES64\PC Helper"
InstallDirRegKey HKLM "Software\PC Helper" "InstallDir"
RequestExecutionLevel admin
Icon "assets\pc-helper.ico"

VIProductVersion "1.1.0.0"
VIAddVersionKey "ProductName" "PC Helper"
VIAddVersionKey "CompanyName" "Kiyoske"
VIAddVersionKey "FileDescription" "Local Windows control center"
VIAddVersionKey "FileVersion" "1.1.0"
VIAddVersionKey "ProductVersion" "1.1.0"

Page directory
Page instfiles

Section "PC Helper" SecMain
  SectionIn RO
  SetOutPath "$INSTDIR"
  File "dist\PC-Helper.exe"
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  WriteRegStr HKLM "Software\PC Helper" "InstallDir" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\PC Helper" "DisplayName" "PC Helper"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\PC Helper" "UninstallString" '"$INSTDIR\Uninstall.exe"'
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\PC Helper" "DisplayVersion" "1.1.0"
  CreateShortcut "$DESKTOP\PC Helper.lnk" "$INSTDIR\PC-Helper.exe"
  CreateDirectory "$SMPROGRAMS\PC Helper"
  CreateShortcut "$SMPROGRAMS\PC Helper\PC Helper.lnk" "$INSTDIR\PC-Helper.exe"
  CreateShortcut "$SMPROGRAMS\PC Helper\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
SectionEnd

Section "Uninstall"
  Delete "$DESKTOP\PC Helper.lnk"
  Delete "$SMPROGRAMS\PC Helper\PC Helper.lnk"
  Delete "$SMPROGRAMS\PC Helper\Uninstall.lnk"
  RMDir "$SMPROGRAMS\PC Helper"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\PC Helper"
  DeleteRegKey HKLM "Software\PC Helper"
  Delete "$INSTDIR\PC-Helper.exe"
  Delete "$INSTDIR\Uninstall.exe"
  RMDir "$INSTDIR"
SectionEnd
