' Jalankan app.py dari folder yang sama dengan file ini (tahan rename folder).
' Interpreter: pakai pythoncore 3.14 kalau ada, kalau tidak jatuh ke pythonw di PATH.
Dim oShell, oFS, sDir, sPy
Set oFS = CreateObject("Scripting.FileSystemObject")
Set oShell = CreateObject("WScript.Shell")
sDir = oFS.GetParentFolderName(WScript.ScriptFullName)
sPy = oShell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\Python\pythoncore-3.14-64\pythonw.exe"
If Not oFS.FileExists(sPy) Then sPy = "pythonw.exe"
oShell.CurrentDirectory = sDir
oShell.Run """" & sPy & """ app.py", 0, False
Set oShell = Nothing
Set oFS = Nothing
