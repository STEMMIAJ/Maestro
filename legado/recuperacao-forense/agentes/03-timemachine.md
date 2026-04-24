# AGENTE 3 — TIME MACHINE
## Status Time Machine
Backup session status:
{
    ClientID = "com.apple.backupd";
    Percent = "-1";
    Running = 0;
}

## Destinos de backup
tmutil: No destinations configured.

## Snapshots locais (APFS)
Snapshots for disk /:

## Último backup
Failed to mount backup destination, error: Error Domain=com.apple.backupd.ErrorDomain Code=17 "Failed to mount destination." UserInfo={NSLocalizedDescription=Failed to mount destination.}

## Máquinas de backup disponíveis
No machine directory found for host.
POSIXError(_nsError: Error Domain=NSPOSIXErrorDomain Code=1 "Operation not permitted")

## INSTRUÇÃO DE RECUPERAÇÃO MANUAL
Se snapshots existem: tmutil restore [snap-path] [destino]
Ou abrir Time Machine pela UI.
