' SDP thin client for registering a device. Windows version.
' 2012-09-09 mjraatik

' This goes through all network adapters in the local computer since I could not find
' a means to get only a bluetooth
strComputer = "." 
Set objWMIService = GetObject("winmgmts:\\" & strComputer & "\root\cimv2")
Set colItems = objWMIService.ExecQuery("Select * from Win32_NetworkAdapter")

For Each objItem in colItems
    If (InStr(objItem.Caption, "Bluetooth") And objItem.MACAddress <> "")  Then
		' For some reason, two BT:s was found but the other did not have a MAC
		' Assigns MAC to a string that is to be executed. The URL is hardcoded here and needs to be corrected
		URLexecutable = "iexplore.exe http://kurre.soberit.hut.fi:8080/registration/" & objItem.MACAddress
    End If
Next

If URLexecutable <> "" Then
	Set WshShell = WScript.CreateObject("WScript.Shell")
	Return = WshShell.Run(URLexecutable, 1)
Else
	Wscript.Echo "No bluetooth address found!"
End if
