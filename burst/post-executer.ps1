# ./post-executer.ps1 -api_username "username" -api_key "apikey" -config_filename "c:\config.json"

############################################################
# Local Machine
# > Set-ExecutionPolicy Unrestricted
# > Set-Item wsman:\localhost\client\trustedhosts *
# > Restart-Service WinRM
#
# Remote Machine
# > Enable-WSManCredSSP -Role server
# > Enable-PSRemoting -Force
# > Set-Item wsman:\localhost\client\trustedhosts *
# > Restart-Service WinRM

param(
    [string]$api_username,
    [string]$api_key,
    [string]$config_file
)


######################################################################################
######################################################################################

$domain_name = "colton.local"
$domain_user = "testaccount"
$domain_ou_path = "OU=CloudServers,DC=dev"
$dns_servers = "172.16.0.11" #"172.16.0.11,10.0.80.11,10.0.80.12"
$gateway = "172.16.0.1"


$domain_user_key = New-Object Byte[] 16   # You can use 16, 24, or 32 for AES
[Security.Cryptography.RNGCryptoServiceProvider]::Create().GetBytes($domain_user_key)
$domain_user_password = Read-Host "Domain User Password:" -AsSecureString | ConvertFrom-SecureString -Key $domain_user_key


######################################################################################

#$base_uri = "https://api.softlayer.com/rest/v3.1"        # PUBLIC
$base_uri = "https://api.service.softlayer.com/rest/v3.1" # PRIVATE

######################################################################################



############################
# BEGIN SCRIPT
############################
############################

############################
# Get Config Server Data
############################
$config = Get-Content -Raw -Path $config_filename | ConvertFrom-Json


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
        #$server_password

        $server_username = "Administrator"
        $secure_password = ConvertTo-SecureString -AsPlainText $server_password -Force
        $cred = New-Object System.Management.Automation.PSCredential -ArgumentList $server_username, $secure_password

        $post_install_script = $current_path + "\" + $post_install_script_filename

        $sl_session_option = New-PSSessionOption -MaxConnectionRetryCount 1
        $sl_session = New-PSSession -ComputerName $sl_private_ip_address -Authentication Negotiate -Credential $cred -SessionOption $sl_session_option
        Invoke-Command -Session $sl_session -ScriptBlock {
            
            param(
                [string]$new_ip_address,
                [string]$dns_servers,
                [string]$gateway
            )

            $private_nic = Get-NetAdapter -Name "PrivateNetwork-A"
            #$sl_ip = ($private_nic | Get-NetIPAddress -AddressFamily IPv4).IPAddress
            $private_nic | New-NetIPAddress -AddressFamily IPv4 -IPAddress $new_ip_address -PrefixLength 24 -Type Unicast #-DefaultGateway $gateway
            if (!$?)
            {
                " Error saving IP Address "
            }

            Disable-NetAdapterBinding -Name "PrivateNetwork-A" -ComponentID ms_tcpip6

            ###############################
            " Update DNS Servers "
            ###############################
            $private_nic | Set-DnsClientServerAddress -ServerAddresses ($dns_servers)

            
        
        } -ArgumentList $($new_ip_address,$dns_servers,$gateway)

        "Pausing 10 Seconds to Before Switching Sessions"
        Sleep -Seconds 10

        $hig_session = New-PSSession -ComputerName $new_ip_address -Authentication Negotiate -Credential $cred
        Invoke-Command -Session $hig_session -ScriptBlock {

            param(
                [byte[]]$domain_user_key,
                [string]$domain_user,
                [string]$domain_user_password,
                [string]$domain_name,
                [string]$domain_ou_path,
                [string]$sl_private_ip_address
            )

            ###############################
            #" Remove SoftLayer IP Address "
            ###############################
            $private_nic = Get-NetAdapter -Name "PrivateNetwork-A"
            $private_nic | Remove-NetIPAddress -IPAddress $sl_private_ip_address -Confirm:$False

            Sleep -Seconds 5

            ######################################################
            # Credentials
            ######################################################
            $secure_password = $domain_user_password | ConvertTo-SecureString -Key $domain_user_key
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
        } -ArgumentList $($domain_user_key,$domain_user,$domain_user_password,$domain_name,$domain_ou_path,$sl_private_ip_address)

    }
    else
    {
        "Couldn't find $hostname"
    }
}

