' Jalankan auto_sync.ps1 yang ada di folder yang sama dengan file ini,
' jadi tetap jalan walau nama folder proyek diganti.
Dim oShell, oFS, sDir
Set oFS = CreateObject("Scripting.FileSystemObject")
Set oShell = CreateObject("WScript.Shell")
sDir = oFS.GetParentFolderName(WScript.ScriptFullName)
oShell.Run "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File """ & sDir & "\auto_sync.ps1""", 0, False
Set oShell = Nothing
Set oFS = Nothing
