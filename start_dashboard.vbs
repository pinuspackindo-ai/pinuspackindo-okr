Dim oShell
Set oShell = CreateObject("WScript.Shell")
oShell.CurrentDirectory = "C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1"
oShell.Run """C:\Users\audit\AppData\Local\Python\pythoncore-3.14-64\pythonw.exe"" app.py", 0, False
Set oShell = Nothing
