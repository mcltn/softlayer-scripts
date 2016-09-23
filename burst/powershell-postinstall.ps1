#Powershell -executionPolicy ByPass c:\postinstall.ps1


###################
" Get Server Name "
###################
$pwd = (Get-Location)
$serverName = $env:computername
$serverName
""

$domainName = "domain.local"
$dnsServers = ("172.16.0.11")
$gateway = "172.16.0.1"
$OUPath = "OU=CloudServers,DC=dev"

######################################################
# Credentials
# This needs to be hardcoded or pulled from a resource
######################################################
#$cred = Get-Credential
#read-host -AsSecureString | ConvertFrom-SecureString | out-file c:\users\developer\securestring.txt

$username = "testaccount"
$password = cat c:\users\developer\securestring.txt | ConvertTo-SecureString
$cred = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $username, $password


$pauseTime = 5  #Seconds
$sleepTime = 60 #Seconds


####################
# Functions
####################
function myPause() {
    Sleep -Seconds $pauseTime
}

##################################
##################################


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
$privateNic = Get-NetAdapter -Name "PrivateNetwork-A"
$slIP = $privateNic.IPv4Address.IPAddress
$privateNic | New-NetIPAddress -AddressFamily IPv4 -IPAddress $ip -PrefixLength 24 -Type Unicast #-DefaultGateway $gateway
if (!$?)
{
    " Error saving IP Address "
}

###############################
" Update DNS Servers "
###############################
$privateNic | Set-DnsClientServerAddress -ServerAddresses $dnsServers


###############################
" Remove SoftLayer IP Address "
###############################
#$privateNic | Remove-NetIPAddress -IPAddress $slIP -Confirm:$False
#Remove-NetRoute -NextHop x.x.x.x -Confirm:$False


Sleep -Seconds $pauseTime

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

Sleep -Seconds $pauseTime
#Restart-Computer -Force

exit
