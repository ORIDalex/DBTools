# Ocultar errores y salida visual
$ErrorActionPreference = "SilentlyContinue"

# Ruta del reporte
$reporte = "C:\clf\computerinfo\Computer_Info_$env:COMPUTERNAME-$env:USERNAME.txt"

# Crear carpeta si no existe
New-Item -ItemType Directory -Path "C:\clf\computerinfo" -Force | Out-Null

# Obtener datos del sistema
$os = Get-CimInstance Win32_OperatingSystem
$cs = Get-CimInstance Win32_ComputerSystem
$cpu = Get-CimInstance Win32_Processor
$bios = Get-CimInstance Win32_BIOS
$ramGB = [math]::Round($cs.TotalPhysicalMemory / 1GB, 2)

# Construir contenido
$contenido = @"
==================================================
            INFORMACION GENERAL DEL EQUIPO
==================================================

--- Usuario ---
Usuario        : $env:USERNAME
Equipo         : $env:COMPUTERNAME
Fecha          : $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Ruta Perfil    : $env:USERPROFILE

--- Sistema ---
Sistema Operativo : $($os.Caption)
Version           : $($os.Version)
Fabricante        : $($cs.Manufacturer)
Modelo            : $($cs.Model)
Tipo Sistema      : $($cs.SystemType)

--- Hardware ---
Procesador        : $($cpu.Name)
Nucleos           : $($cpu.NumberOfCores)
Procesadores Log. : $($cpu.NumberOfLogicalProcessors)
RAM Total (GB)    : $ramGB

--- Numero de Serie ---
$($bios.SerialNumber)

--- Red IPv4 ---
$(
    Get-NetIPAddress -AddressFamily IPv4 |
    Where-Object {$_.IPAddress -notlike "169.*"} |
    Select-Object InterfaceAlias, IPAddress |
    Format-Table -HideTableHeaders | Out-String
)

--- MAC ---
$(
    Get-NetAdapter |
    Where-Object {$_.Status -eq "Up"} |
    Select-Object Name, MacAddress |
    Format-Table -HideTableHeaders | Out-String
)

--- Discos ---
$(
    Get-CimInstance Win32_DiskDrive |
    Select-Object Model,
        @{Name="Size(GB)";Expression={[math]::Round($_.Size/1GB,2)}},
        MediaType |
    Format-Table -HideTableHeaders | Out-String
)
"@

# Guardar archivo en UTF8 limpio
Set-Content -Path $reporte -Value $contenido -Encoding utf8