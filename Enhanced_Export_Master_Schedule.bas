Attribute VB_Name = "Enhanced_Export_Master_Schedule"
Sub ExportMasterScheduleWithData()
    '
    ' ExportMasterScheduleWithData Macro
    ' Exports the master schedule to PDF and JSON data for Python automation
    '
    
    Dim ws As Worksheet
    Dim exportPath As String
    Dim publicPath As String
    Dim archivePath As String
    Dim jsonPath As String
    Dim fileName As String
    Dim dateStamp As String
    Dim sendTradeEmail As Boolean
    Dim sendCustomerEmail As Boolean
    
    ' Set references
    Set ws = ActiveSheet
    
    ' Get email preferences from checkboxes
    sendTradeEmail = Range("C1").Value
    sendCustomerEmail = Range("D1").Value
    
    ' Create date stamp
    dateStamp = Format(Now(), "yyyy-mm-dd_hhmm")
    
    ' Define paths
    exportPath = "G:\My Drive\Project Dashboard\Schedule System\Temp\Master Schedule.pdf"
    publicPath = "G:\My Drive\Project Dashboard\Public\Master Schedule\Master Schedule.pdf"
    archivePath = "G:\My Drive\Project Dashboard\Schedule System\Master Files\Archive\" & dateStamp & " Master Schedule.pdf"
    jsonPath = "G:\My Drive\Project Dashboard\Schedule System\Temp\schedule_data.json"
    
    ' Create directories if they don't exist
    On Error Resume Next
    MkDir "G:\My Drive\Project Dashboard\Schedule System"
    MkDir "G:\My Drive\Project Dashboard\Schedule System\Temp"
    MkDir "G:\My Drive\Project Dashboard\Public"
    MkDir "G:\My Drive\Project Dashboard\Public\Master Schedule"
    MkDir "G:\My Drive\Project Dashboard\Schedule System\Master Files"
    MkDir "G:\My Drive\Project Dashboard\Schedule System\Master Files\Archive"
    On Error GoTo 0
    
    ' Show progress
    Application.StatusBar = "Exporting Master Schedule..."
    
    ' Export JSON data first
    If Not ExportScheduleDataToJSON(jsonPath) Then
        MsgBox "Failed to export schedule data. Please select the schedule range.", vbExclamation
        Exit Sub
    End If
    
    ' Export PDF (existing code)
    Dim exportRange As Range
    Dim response As VbMsgBoxResult
    Dim hadBorder As Boolean
    Dim originalBorderStyle As Variant
    Dim originalBorderWeight As Variant
    
    If TypeName(Selection) = "Range" And Selection.Cells.Count > 1 Then
        Set exportRange = Selection
        
        ' Add border and export PDF (existing code continues...)
        With exportRange.Borders(xlEdgeBottom)
            hadBorder = .LineStyle <> xlNone
            If hadBorder Then
                originalBorderStyle = .LineStyle
                originalBorderWeight = .Weight
            End If
        End With
        
        With exportRange.Borders(xlEdgeBottom)
            .LineStyle = xlContinuous
            .Weight = xlThick
            .ColorIndex = xlAutomatic
        End With
        
        exportRange.ExportAsFixedFormat Type:=xlTypePDF, _
            fileName:=exportPath, _
            Quality:=xlQualityStandard, _
            IncludeDocProperties:=False, _
            IgnorePrintAreas:=True, _
            OpenAfterPublish:=False
            
        With exportRange.Borders(xlEdgeBottom)
            If hadBorder Then
                .LineStyle = originalBorderStyle
                .Weight = originalBorderWeight
            Else
                .LineStyle = xlNone
            End If
        End With
    Else
        ' Handle no selection case
        response = MsgBox("No range selected. Please select the schedule range first.", vbExclamation)
        Exit Sub
    End If
    
    ' Copy to public folder
    Application.StatusBar = "Copying files..."
    FileCopy exportPath, publicPath
    FileCopy exportPath, archivePath
    
    ' Copy JSON to public folder too
    FileCopy jsonPath, "G:\My Drive\Project Dashboard\Public\Master Schedule\schedule_data.json"
    
    ' Create trigger file for Python script
    Dim triggerFile As String
    triggerFile = "G:\My Drive\Project Dashboard\Schedule System\Temp\trigger.txt"
    
    Open triggerFile For Output As #1
    Print #1, "EXPORT_COMPLETE"
    Print #1, "TRADE_EMAIL:" & sendTradeEmail
    Print #1, "CUSTOMER_EMAIL:" & sendCustomerEmail
    Print #1, "TIMESTAMP:" & Format(Now(), "yyyy-mm-dd hh:mm:ss")
    Print #1, "JSON_DATA:schedule_data.json"
    Close #1
    
    ' Update status
    Application.StatusBar = "Schedule exported successfully!"
    
    MsgBox "Master Schedule exported successfully!" & vbCrLf & vbCrLf & _
           "? PDF saved to public folder" & vbCrLf & _
           "? Schedule data exported as JSON" & vbCrLf & _
           "? Archive copy created" & vbCrLf & _
           "? Automation triggered", _
           vbInformation, "Export Complete"
    
    Application.StatusBar = False
    
End Sub

Function ExportScheduleDataToJSON(jsonPath As String) As Boolean
    '
    ' Exports the selected schedule data to JSON format
    '
    
    On Error GoTo ErrorHandler
    
    Dim rng As Range
    Dim cell As Range
    Dim row As Long, col As Long
    Dim startRow As Long, startCol As Long
    Dim jsonData As String
    Dim projectData As String
    Dim scheduleData As String
    Dim firstDataRow As Long
    
    ' Use selection or active range
    If TypeName(Selection) = "Range" And Selection.Cells.Count > 1 Then
        Set rng = Selection
    Else
        ExportScheduleDataToJSON = False
        Exit Function
    End If
    
    ' Find the starting row and column
    startRow = rng.row
    startCol = rng.Column
    
    ' Initialize JSON
    jsonData = "{" & vbCrLf
    jsonData = jsonData & "  ""export_date"": """ & Format(Now(), "yyyy-mm-dd hh:mm:ss") & """," & vbCrLf
    jsonData = jsonData & "  ""projects"": [" & vbCrLf
    
    ' Identify header rows (assuming first 6 rows are headers)
    ' Row 1: Community names
    ' Row 2: Community names continued or "Estates/Landing"
    ' Row 3: Addresses (346/354, etc.)
    ' Row 4: Streets
    ' Row 5: Lots
    ' Row 6: Square footage
    ' Row 7: Features
    ' Row 8+: Schedule data
    
    firstDataRow = startRow + 7 ' Adjust based on your structure
    
    ' Process each column (project)
    Dim projectCount As Long
    projectCount = 0
    
    For col = startCol + 1 To startCol + rng.Columns.Count - 1
        ' Check if column is hidden
        If Not Columns(col).Hidden Then
            ' Get project info from header rows
            Dim community As String, address As String, street As String
            Dim lots As String, sqft As String, features As String
            
            ' Read header data (with error handling for merged cells)
            On Error Resume Next
            community = Trim(CStr(Cells(startRow, col).Value & " " & Cells(startRow + 1, col).Value))
            address = CStr(Cells(startRow + 2, col).Value)
            street = CStr(Cells(startRow + 3, col).Value)
            lots = CStr(Cells(startRow + 4, col).Value)
            sqft = CStr(Cells(startRow + 5, col).Value)
            features = CStr(Cells(startRow + 6, col).Value)
            On Error GoTo ErrorHandler
            
            ' Only process if we have an address
            If address <> "" And address <> "0" Then
                ' Handle duplex addresses
                Dim addresses() As String
                If InStr(address, "/") > 0 Then
                    addresses = Split(address, "/")
                Else
                    ReDim addresses(0)
                    addresses(0) = address
                End If
                
                ' Process each unit in duplex
                Dim unitIndex As Long
                For unitIndex = 0 To UBound(addresses)
                    If projectCount > 0 Then
                        jsonData = jsonData & "," & vbCrLf
                    End If
                    
                    ' Extract lot number for this unit
                    Dim unitLot As String
                    unitLot = ExtractLotNumber(lots, unitIndex)
                    
                    ' Start project object
                    projectData = "    {" & vbCrLf
                    projectData = projectData & "      ""project_id"": """ & Trim(addresses(unitIndex)) & """," & vbCrLf
                    projectData = projectData & "      ""address"": """ & Trim(addresses(unitIndex)) & " " & Trim(street) & """," & vbCrLf
                    projectData = projectData & "      ""community"": """ & Replace(Trim(community), """", "\""") & """," & vbCrLf
                    projectData = projectData & "      ""lots"": """ & unitLot & """," & vbCrLf
                    projectData = projectData & "      ""sqft"": """ & ExtractSquareFootage(sqft) & """," & vbCrLf
                    projectData = projectData & "      ""features"": """ & Replace(Trim(features), """", "\""") & """," & vbCrLf
                    projectData = projectData & "      ""column_index"": " & (col - startCol - 1) & "," & vbCrLf
                    projectData = projectData & "      ""schedule"": [" & vbCrLf
                    
                    ' Extract schedule data
                    scheduleData = ""
                    Dim scheduleCount As Long
                    scheduleCount = 0
                    
                    For row = firstDataRow To startRow + rng.Rows.Count - 1
                        ' Check if row is hidden
                        If Not Rows(row).Hidden Then
                            Dim dateValue As String, taskValue As String
                            
                            ' Get date from column D (the actual date column)
                            dateValue = CStr(Cells(row, 4).Value)  ' Column D = 4
                            
                            ' Get task from project column
                            taskValue = CStr(Cells(row, col).Value)
                            
                            ' Process if we have both date and task
                            If dateValue <> "" And taskValue <> "" And taskValue <> "0" Then
                                If scheduleCount > 0 Then
                                    scheduleData = scheduleData & "," & vbCrLf
                                End If
                                
                                ' Format date
                                Dim formattedDate As String
                                formattedDate = FormatScheduleDate(dateValue)
                                
                                scheduleData = scheduleData & "        {" & vbCrLf
                                scheduleData = scheduleData & "          ""date"": """ & formattedDate & """," & vbCrLf
                                scheduleData = scheduleData & "          ""task"": """ & Replace(Trim(taskValue), """", "\""") & """," & vbCrLf
                                scheduleData = scheduleData & "          ""phase"": """ & CategorizeTask(taskValue) & """" & vbCrLf
                                scheduleData = scheduleData & "        }"
                                
                                scheduleCount = scheduleCount + 1
                            End If
                        End If
                    Next row
                    
                    ' Close schedule array and project object
                    projectData = projectData & scheduleData & vbCrLf
                    projectData = projectData & "      ]" & vbCrLf
                    projectData = projectData & "    }"
                    
                    ' Add project to JSON
                    jsonData = jsonData & projectData
                    projectCount = projectCount + 1
                    
                Next unitIndex
            End If
        End If
    Next col
    
    ' Close JSON
    jsonData = jsonData & vbCrLf & "  ]" & vbCrLf & "}"
    
    ' Write to file
    Dim fileNum As Integer
    fileNum = FreeFile
    
    Open jsonPath For Output As #fileNum
    Print #fileNum, jsonData
    Close #fileNum
    
    ExportScheduleDataToJSON = True
    Exit Function
    
ErrorHandler:
    MsgBox "Error exporting schedule data: " & Err.Description, vbExclamation
    ExportScheduleDataToJSON = False
    
End Function
Function ExtractLotNumber(lotString As String, unitIndex As Long) As String
    ' Extract lot number from strings like "Lots 81/82"
    Dim result As String
    result = lotString
    
    ' Remove "Lots" prefix
    result = Replace(result, "Lots", "")
    result = Trim(result)
    
    ' Handle split lots
    If InStr(result, "/") > 0 Then
        Dim parts() As String
        parts = Split(result, "/")
        If unitIndex <= UBound(parts) Then
            result = Trim(parts(unitIndex))
        Else
            result = Trim(parts(0))
        End If
    End If
    
    ExtractLotNumber = result
End Function

Function ExtractSquareFootage(sqftString As String) As String
    ' Extract just the numeric square footage
    Dim matches As Object
    Dim regex As Object
    Set regex = CreateObject("VBScript.RegExp")
    
    regex.Pattern = "\d{4}"
    regex.Global = True
    
    Set matches = regex.Execute(sqftString)
    
    If matches.Count > 0 Then
        ExtractSquareFootage = matches(0).Value
    Else
        ExtractSquareFootage = sqftString
    End If
End Function

Function FormatScheduleDate(dateString As String) As String
    ' Convert Excel date to YYYY-MM-DD format
    On Error Resume Next
    
    Dim dateValue As Date
    
    ' Try to parse the date
    If IsDate(dateString) Then
        dateValue = CDate(dateString)
        FormatScheduleDate = Format(dateValue, "yyyy-mm-dd")
    Else
        ' Handle special formats like "M 9-Jun"
        Dim cleanDate As String
        cleanDate = dateString
        
        ' Remove day abbreviations
        cleanDate = Replace(cleanDate, "M ", "")
        cleanDate = Replace(cleanDate, "T ", "")
        cleanDate = Replace(cleanDate, "W ", "")
        cleanDate = Replace(cleanDate, "Th ", "")
        cleanDate = Replace(cleanDate, "F ", "")
        
        ' Add year if not present
        If InStr(cleanDate, "-") > 0 And Len(cleanDate) < 10 Then
            cleanDate = cleanDate & "-2024"
        End If
        
        If IsDate(cleanDate) Then
            dateValue = CDate(cleanDate)
            FormatScheduleDate = Format(dateValue, "yyyy-mm-dd")
        Else
            FormatScheduleDate = dateString ' Return original if can't parse
        End If
    End If
    
    On Error GoTo 0
End Function

Function CategorizeTask(task As String) As String
    ' Categorize construction task
    Dim taskLower As String
    taskLower = LCase(task)
    
    Select Case True
        Case InStr(taskLower, "foundation") > 0 Or InStr(taskLower, "slab") > 0 Or InStr(taskLower, "concrete") > 0
            CategorizeTask = "foundation"
        Case InStr(taskLower, "fram") > 0
            CategorizeTask = "framing"
        Case InStr(taskLower, "roof") > 0
            CategorizeTask = "roofing"
        Case InStr(taskLower, "elec") > 0
            CategorizeTask = "electrical"
        Case InStr(taskLower, "plumb") > 0
            CategorizeTask = "plumbing"
        Case InStr(taskLower, "hvac") > 0
            CategorizeTask = "hvac"
        Case InStr(taskLower, "insulat") > 0
            CategorizeTask = "insulation"
        Case InStr(taskLower, "drywall") > 0 Or InStr(taskLower, "tape") > 0 Or InStr(taskLower, "texture") > 0
            CategorizeTask = "drywall"
        Case InStr(taskLower, "paint") > 0 Or InStr(taskLower, "pva") > 0
            CategorizeTask = "painting"
        Case InStr(taskLower, "floor") > 0 Or InStr(taskLower, "carpet") > 0 Or InStr(taskLower, "lvp") > 0
            CategorizeTask = "flooring"
        Case InStr(taskLower, "cabinet") > 0 Or InStr(taskLower, "c-tops") > 0
            CategorizeTask = "cabinets"
        Case InStr(taskLower, "clean") > 0 Or InStr(taskLower, "move") > 0
            CategorizeTask = "move"
        Case InStr(taskLower, "inspect") > 0
            CategorizeTask = "inspection"
        Case InStr(taskLower, "detail") > 0 Or InStr(taskLower, "finish") > 0 Or InStr(taskLower, "trim") > 0
            CategorizeTask = "finishing"
        Case Else
            CategorizeTask = "other"
    End Select
End Function

