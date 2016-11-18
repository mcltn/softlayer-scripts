
##################################
##################################

param(
    [string]$domain_name,
    [string]$domain_user,
    [string]$domain_password,
    [byte[]]$domain_key,
    [string]$domain_ou_path,
    [string]$dns_servers,
    [string]$gateway
)


##################################
##################################


###################
" Get Server Name "
###################
$pwd = (Get-Location)
$server_name = $env:computername
$server_name
""


###################
# Get Disk info
###################
$mdd = Get-WmiObject -Class Win32_Volume | 
        Select DriveLetter,
            @{Label="FreeSpace (In GB)";Expression={$_.Freespace/1gb}},
            @{Label="Capacity (In GB)";Expression={$_.Capacity/1gb}},
            DeviceID,Label

####################################
" Checking locally for UserData... "
####################################
$dl = ""
foreach ($md in $mdd) {
    if ($md.Label -match "METADATA") {
        $dl = $md.DriveLetter
        $meta = $dl + "\meta.js"
        $userdata = Get-Content -Raw -Path $meta
        $userdata = $userdata.replace('["','')
        $userdata = $userdata.replace('"]','')
        $userdata = $userdata.replace('\','')
        $userdata = $userdata | ConvertFrom-Json
        $hn = $userdata.hostname
        $ip = $userdata.privateIPAddress
    }
}

if ($dl -eq "") {
    ##################################################
    " Getting Userdata from SoftLayer API Service... "
    ##################################################
    $uri = "https://api.service.softlayer.com/rest/v3/SoftLayer_Resource_Metadata/getUserMetadata.json"
    $userdata = Invoke-RestMethod -Uri $uri | ConvertFrom-Json
    $userdata
    $hn = $userdata.hostname
    $ip = $userdata.privateIPAddress
}

Write-Host " Hostname   : $hn"
Write-Host " IP Address : $ip"


###############################
" Updating Private NIC Address "
###############################
$private_nic = Get-NetAdapter -Name "PrivateNetwork-A"
$sl_ip = ($private_nic | Get-NetIPAddress -AddressFamily IPv4).IPAddress
$private_nic | New-NetIPAddress -AddressFamily IPv4 -IPAddress $ip -PrefixLength 24 -Type Unicast #-DefaultGateway $gateway
if (!$?)
{
    " Error saving IP Address "
}

###############################
" Update DNS Servers "
###############################
$private_nic | Set-DnsClientServerAddress -ServerAddresses ($dns_servers)


###############################
" Remove SoftLayer IP Address "
###############################
#$private_nic | Remove-NetIPAddress -IPAddress $sl_ip -Confirm:$False
#Remove-NetRoute -NextHop x.x.x.x -Confirm:$False


Sleep -Seconds 10

#Test-Connection 172.16.0.11

######################################################
# Credentials
######################################################
$secure_password = $domain_password | ConvertTo-SecureString -Key $domain_key
$cred = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $domain_user, $secure_password

############################
" Add to Domain "
############################
try {
    Add-Computer -DomainName $domain_name -Credential $cred #-OUPath $domain_ou_path 2>&1
} catch {
    "Error adding to domain"
}

############################
" Reboot Server "
############################
Sleep -Seconds 5
Restart-Computer -Force

exit
