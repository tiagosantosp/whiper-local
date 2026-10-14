Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c cd /d C:\DEV\whiper-local && .venv\Scripts\pythonw.exe main.py", 0, False
Set WshShell = Nothing
