#Set-ExecutionPolicy Unrestricted
#[Byte[]] $key = (1..16)
#Invoke-Command -FilePath 'c:\prov\join-domain.ps1' -ComputerName 'localhost' -ArgumentList 'domain','username','password',$key,'OU=CloudServers,DC=dev'

param([string]$domainName, [string]$username, [string]$password, [byte[]]$key, [string]$OUPath)

$domainName
$username
#$password
$OUPath
#$key

######################################################
# Credentials
######################################################
$securepassword = $password | ConvertTo-SecureString -Key $key
$cred = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $username, $securepassword

############################
" Add to Domain "
############################
try {
    Add-Computer -DomainName $domainName -Credential $cred -OUPath $OUPath 2>&1
} catch {
    "Error adding to domain"
}

############################
" Reboot Server "
############################
Sleep -Seconds 5
#Restart-Computer -Force


