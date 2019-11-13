# Bug-Hunter-Infrastructure-Deployment

Place the digital_ocean.ini and digital_ocean.py files into /etc/ansible. Be sure to update digital_ocean.ini with your api token. (source: https://github.com/geerlingguy/ansible-for-devops/tree/master/dynamic-inventory/digitalocean)

Be sure to review the plan before building. To plan your Digital Ocean infrastructure, run the following commands:

    terraform plan
 
 Build it:
 
    terraform apply
    
Destroy:

    terraform destroy

To install all of your bug hunting tools, run the following command:
            
    ansible-playbook ./bughunter.yml -i /etc/ansible/digital_ocean.py --private-key /root/.ssh/id_rsa 
    
Currently builds Ubuntu 16.04 x64 or Debian 10 x64 1GB/1VCPU Droplet and installs the following tools. Check out bughunter.yml for full details on what's installed.
* Nmap
* SQLMap
* Dirsearch
* SecLists
* Knockpy
* Wfuzz
* Sublist3r
* Scrapy
* WPScan
* Joomscan

## Lightsail

1) Create an API key with AWS. Run `aws configure` to set the API keys.
2) Create SSH keys with AWS
                
        chmod 400 /path/to/keypair.pem
        
3) Install RVM Ansible Role    
    
        ansible-galaxy install rvm.ruby
  
4) After running `terraform apply`, edit the hosts file to add the IP address terraform outputs. 
5) Install all of the tools with ansible.
            
        ansible-playbook ./debian.yml -i hosts --private-key /path/to/keypair.pem
