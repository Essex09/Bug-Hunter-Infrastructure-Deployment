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
