Dim oShell
Set oShell = CreateObject("WScript.Shell")
oShell.Run "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File ""C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\auto_sync.ps1""", 0, False
Set oShell = Nothing
