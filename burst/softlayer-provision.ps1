# ./softlayer-provision.ps1 -api_username "username" -api_key "apikey" -action "CREATE" -config_filename "c:\config.json"
# ./softlayer-provision.ps1 -api_username "username" -api_key "apikey" -action "CANCEL" -config_filename "c:\config.json"


param(
    [string]$api_username,
    [string]$api_key,
    [string]$action,
    [string]$config_file
)


$base_uri = "https://api.softlayer.com/rest/v3.1"           # PUBLIC
#$base_uri = "https://api.service.softlayer.com/rest/v3.1"  # PRIVATE


############################
# Set Base URI Info
############################
$base_64_auth_info = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(("{0}:{1}" -f $api_username,$api_key)))


############################
# Get Config Server Data
############################
$config = Get-Content -Raw -Path $config_filename | ConvertFrom-Json

if (!$config) {
    "Error opening config."
    exit
}


if ($action -eq "CREATE") {
    ############################
    "Provisioning Servers"
    ############################

    $_domain = $config.domain
    $_datacenter = $config.datacenter
    $_cpus = $config.cpus
    $_memory = $config.memory
    $_disk = $config.disk
    $_local_disk = $config.localDisk
    $_private = $config.private
    $_dedicated = $config.dedicated
    $_hourly = $config.hourly
    $_tag = $config.tag
    $_private_vlan = $config.privateVlan
    $_nic_speed = $config.nicSpeed
    $_post_install_url = $config.postInstallUrl
    $_ssh_key = $config.sshKey
    $_os_code = $config.osCode
    $_template_guid = $config.templateGuid


    foreach($h in $config.hosts){

        $hostname = $h.hostname

        $order_data = @{
            parameters=@(
                @{
                    hostname=$hostname
                    domain=$_domain
                    startCpus=$_cpus
                    maxMemory=$_memory
                    localDiskFlag=$_local_disk
                    privateNetworkOnlyFlag=$_private
                    hourlyBillingFlag=$_hourly
                    datacenter=@{
                        name=$_datacenter
                    }
                    tagReferences=@(@{tag=@{name=$_tag}})
                }
            )        
        }

        $order_data.parameters[0].Add("networkComponents",@(@{maxSpeed=$_nic_speed}))

        if ($_os_code -ne "") {
            $order_data.parameters[0].Add("blockDevices",@(@{device=0;diskImage=@{capacity=$_disk}}))
            $order_data.parameters[0].Add("operatingSystemReferenceCode",$_os_code)
        } elseif ($_template_guid -ne "") {
            $order_data.parameters[0].Add("blockDeviceTemplateGroup",@{globalIdentifier=$_template_guid})
        }

        if ($_private_vlan -ne "") {
            $order_data.parameters[0].Add("primaryBackendNetworkComponent",@{networkVlan=@{id=$_private_vlan}})
        }



        $json = $order_data | ConvertTo-Json -Depth 5
        $json


        ##################################
        "Provisioning : {0}" -f $hostname
        ##################################

        $uri = $base_uri + "/SoftLayer_Virtual_Guest"
        $headers = New-Object "System.Collections.Generic.Dictionary[[String],[String]]"
        $headers.Add("Authorization", "Basic {0}" -f $base_64_auth_info)
        $headers.Add("Accept", "application/json")
        $order_response = Invoke-RestMethod $uri -Method Post -Headers $headers -ContentType 'application/json' -Body $json
        $order_response

        $_server_id = $order_response.id
        Sleep -Seconds 1

        $tag_obj = @{parameters=@($_tag)} | ConvertTo-Json -Depth 3
        $uri = $base_uri + "/SoftLayer_Virtual_Guest/{0}/setTags" -f $_server_id
        $tag_response = Invoke-RestMethod $uri -Method Post -Headers $headers -ContentType 'application/json' -Body $tag_obj
        
    }

    exit

} elseif ($action -eq "CANCEL") {
    ############################
    "Cancelling Servers By Tag : {0}" -f $config.tag
    ############################

    if ($config.tag -ne "") {
        $_tag = $config.tag

        $server_list_uri = $base_uri + "/SoftLayer_Account/getVirtualGuests?objectMask=mask[id]&objectFilter={""virtualGuests"":{""tagReferences"":{""tag"":{""name"":{""operation"":""in"", ""options"":[{""name"":""data"",""value"":[""$_tag""]}]}}}}}"
        $server_list_uri
        $servers = Invoke-RestMethod -Uri $server_list_uri -Headers @{Authorization=("Basic {0}" -f $base_64_auth_info)}
        $servers
        foreach($s in $servers){
            "Canceling Server : {0}" -f $s.id
            $cancel_server_uri = $base_uri + "/SoftLayer_Virtual_Guest/{0}" -f $s.id
            $cancel_response = Invoke-RestMethod -Uri $cancel_server_uri -Method DELETE -Headers @{Authorization=("Basic {0}" -f $base_64_auth_info)}
        }
    }

    exit

} else {
    ############################
    "No Valid Action Specified"
    ############################

    exit

}
