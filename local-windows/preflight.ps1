# Read-only Windows build environment inventory. No installation or PATH changes.
$ErrorActionPreference = 'Continue'
'=== Windows / CPU / memory ==='
Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, OSArchitecture
Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors
Get-CimInstance Win32_ComputerSystem | Select-Object @{Name='RAM_GB';Expression={[math]::Round($_.TotalPhysicalMemory / 1GB)}}
'=== Commands currently on PATH ==='
foreach ($name in @('git','cmake','ninja','gcc','g++','qmake','qmake6','cl','python','docker','ssh')) {
  Get-Command $name -All -ErrorAction SilentlyContinue | Select-Object Name, Source
}
'=== MSYS2 roots ==='
foreach ($base in @('C:\msys64','C:\scopy-msys64','C:\ScopyToolchain')) {
  if (Test-Path $base) {
    Get-Item $base | Select-Object FullName
    foreach ($kind in @('mingw64','ucrt64')) {
      $bin=Join-Path $base "$kind\bin"
      foreach ($tool in @('gcc.exe','cmake.exe','qmake.exe','qmake-qt5.exe')) {
        $candidate=Join-Path $bin $tool
        if (Test-Path $candidate) { $candidate }
      }
    }
  }
}
'=== Existing Qt installations ==='
Get-ChildItem 'C:\Qt','D:\Qt' -Directory -ErrorAction SilentlyContinue | Select-Object FullName
'=== Free disk space ==='
Get-PSDrive -PSProvider FileSystem | Select-Object Name, @{Name='Free_GB';Expression={[math]::Round($_.Free / 1GB)}}
'Inventory complete. No system settings were changed.'
