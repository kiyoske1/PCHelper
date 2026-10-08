Unicode true
Name "PC Helper"
OutFile "PC-Helper-Setup.exe"
InstallDir "$PROGRAMFILES64\\PC Helper"
RequestExecutionLevel admin
Icon "assets\\pc-helper.ico"

Page directory
Page instfiles

Section "PC Helper"
  SetOutPath "$INSTDIR"
  File "dist\\PC-Helper.exe"
  CreateShortcut "$DESKTOP\\PC Helper.lnk" "$INSTDIR\\PC-Helper.exe"
  CreateShortcut "$SMPROGRAMS\\PC Helper.lnk" "$INSTDIR\\PC-Helper.exe"
SectionEnd

Section "Uninstall"
  Delete "$DESKTOP\\PC Helper.lnk"
  Delete "$SMPROGRAMS\\PC Helper.lnk"
  Delete "$INSTDIR\\PC-Helper.exe"
  RMDir "$INSTDIR"
SectionEnd
