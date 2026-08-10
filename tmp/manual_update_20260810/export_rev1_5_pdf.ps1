$inputPptx = 'C:\Users\deepu\OneDrive\Desktop\Rane\dms_portal_copy\output\pptx\DMS_Portal_User_Manual_Updated_Rev1.5.pptx'
$outputPdf = 'C:\Users\deepu\OneDrive\Desktop\Rane\dms_portal_copy\output\pdf\DMS_Portal_User_Manual_Updated_Rev1.5.pdf'

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $outputPdf) | Out-Null
$powerPoint = $null
$presentation = $null
try {
    $powerPoint = New-Object -ComObject PowerPoint.Application
    $presentation = $powerPoint.Presentations.Open($inputPptx, $true, $false, $false)
    $presentation.SaveAs($outputPdf, 32)
}
finally {
    if ($null -ne $presentation) { $presentation.Close() }
    if ($null -ne $powerPoint) { $powerPoint.Quit() }
    if ($null -ne $presentation) { [void][Runtime.InteropServices.Marshal]::ReleaseComObject($presentation) }
    if ($null -ne $powerPoint) { [void][Runtime.InteropServices.Marshal]::ReleaseComObject($powerPoint) }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}

Get-Item $outputPdf | Select-Object FullName, Length, LastWriteTime
