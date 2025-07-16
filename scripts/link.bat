rem link-name python icon-pth file.py run app

@echo off
Cls
set SCRIPT="%TEMP%\%RANDOM%-%RANDOM%-%RANDOM%-%RANDOM%.vbs"

echo Set oWS = WScript.CreateObject("WScript.Shell") >> %SCRIPT%
echo sLinkFile = "%USERPROFILE%\Desktop\%1.lnk" >> %SCRIPT%

echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%
echo oLink.TargetPath = "%2" >> %SCRIPT%
echo oLink.IconLocation = "%3" >> %SCRIPT%
echo oLink.Arguments = "%4 %5" >> %SCRIPT%
echo oLink.Save >> %SCRIPT%

cscript /nologo %SCRIPT%
del %SCRIPT%
pause