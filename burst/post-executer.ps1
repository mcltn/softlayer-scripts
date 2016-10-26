
############################################################
# Local Machine
# > Set-Item wsman:\localhost\client\trustedhosts *
# > Restart-Service WinRM
# > Enable-WSManCredSSP -Role Client -DelegateComputer *
# > gpedit.msc
#     Computer Configuration > Administrative Templates > System > Credentials Delegation
#     Double Click "Allow delegating fresh credentials with NTLM-only Server Authentication"
#     Enable and add to server list "WSMAN/*"
#
# Remote Machine
# > Enable-WSManCredSSP -Role server
# > Enable-PSRemoting -Force
# > Set-Item wsman:\localhost\client\trustedhosts *
# > Restart-Service WinRM


######################################################################################
# Set Run Variables
# - These can be entered via the command prompt prior to running script
#   if you do not want it in the file
######################################################################################

$api_username = "username"
$api_key = "apikey"
$post_install_script_filename = "powershell-postinstall.ps1"
$config_filename = "config-mex01.json"

$domain_name = "colton.local"
$domain_user = "testaccount"

#[Byte[]] $domain_user_key = (1..16)
$domain_user_key = New-Object Byte[] 16   # You can use 16, 24, or 32 for AES
[Security.Cryptography.RNGCryptoServiceProvider]::Create().GetBytes($domain_user_key)
$domain_user_password = Read-Host -AsSecureString | ConvertFrom-SecureString -Key $domain_user_key

$domain_ou_path = "OU=CloudServers,DC=dev"
$dns_servers = "172.16.0.11" #"172.16.0.11,10.0.80.11,10.0.80.12"
$gateway = "172.16.0.1"

$base_uri = "https://api.softlayer.com/rest/v3.1"

######################################################################################



############################
# BEGIN SCRIPT
############################
############################

$current_path = Split-Path $MyInvocation.MyCommand.Path
$current_path

############################
# Get Config Server Data
############################
$config_path = $current_path + "\" + $config_filename
$config = Get-Content -Raw -Path $config_path | ConvertFrom-Json


############################
# Set Base URI Info
############################
$base_64_auth_info = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(("{0}:{1}" -f $api_username,$api_key)))


############################
# Get List Of Servers By Tag
############################
$server_list_uri = $base_uri + "/SoftLayer_Account/getVirtualGuests"
$servers = Invoke-RestMethod -Uri $server_list_uri -Headers @{Authorization=("Basic {0}" -f $base_64_auth_info)}


############################
# Loop Through Servers
############################
#foreach($s in $servers){
foreach($h in $config.hosts){

    $server_id = $null
    $instance = $null
    $new_ip_address = $null
    $sl_ip_address = $null
    $sl_private_ip_address = $null


    $hostname = $h.hostname
    $s = $servers | where { $_.hostname -eq $hostname }
    $s

    if ($s) {
        "Server ID:{0}" -f $s.id
        "Hostname :{0}" -f $s.hostname

        $server_id = $s.id
        $uri = $base_uri + "/SoftLayer_Virtual_Guest/{0}?objectMask=mask[id,hostname,primaryIpAddress,primaryBackendIpAddress,operatingSystem[passwords[password]]]" -f $server_id
        $uri
        $instance = Invoke-RestMethod -Uri $uri -Headers @{Authorization=("Basic {0}" -f $base_64_auth_info)}
        $instance

        $new_ip_address = $h.privateIPAddress

        #$sl_ip_address = $instance.primaryIpAddress
        #$sl_ip_address
        $sl_private_ip_address = $instance.primaryBackendIpAddress
        $sl_private_ip_address

        $server_password = $instance.operatingSystem.passwords[0].password
        $server_password

        $server_username = "Administrator"
        $secure_password = ConvertTo-SecureString -AsPlainText $server_password -Force
        $cred = New-Object System.Management.Automation.PSCredential -ArgumentList $server_username, $secure_password

        $post_install_script = $current_path + "\" + $post_install_script_filename

        Invoke-Command -FilePath $post_install_script -ComputerName $sl_private_ip_address -Authentication CredSSP -Credential $cred -ArgumentList $domain_name,$domain_user,$domain_user_password,$domain_user_key,$domain_ou_path,$dns_servers,$gateway
    }
    else
    {
        "Couldn't find $hostname"
    }
}

