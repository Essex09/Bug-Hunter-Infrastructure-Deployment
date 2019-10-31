# Bug-Hunter-Infrastructure-Deployment

Place the digital_ocean.ini and digital_ocean.py files into /etc/ansible. Be sure to update digital_ocean.ini with your api token.

To build your Digital Ocean infrastructure, run the following commands:
* Be sure to review the plan before building.

      terraform plan
 
 Build it:
 
    terraform apply
    
Destroy:

    terraform destroy

To install all of your bug hunting tools, run the following command:
            
    ansible-playbook ./bughunter.yml -i /etc/ansible/digital_ocean.py --private-key /root/.ssh/id_rsa 
