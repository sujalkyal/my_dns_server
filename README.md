#Steps to deploy on an AWS EC2 instance

1. Launch an AWS EC2 Instance
    * Instance type: Ubuntu
    * Security groups: 
        * SSH->TCP - PORT 22 - 0.0.0.0
        * UDP(ALL) - PORT ALL - 0.0.0.0

2. Connect to the EC2 Instance in AWS and run the following commands
    * `sudo apt update`
    * `sudo apt upgrade -y`
    * `sudo apt install python3 python3-pip -y`
    * `sudo apt install git -y`

3. Clone Your Project from GitHub
    * `git clone https://github.com/sujalkyal/my_dns_server.git`
    * `cd my_dns_server`

4. Create and Activate a Python Virtual Environment and Install required dependencies
    * `sudo apt install python3-venv -y`
    * `python3 -m venv myenv`
    * `source myenv/bin/activate`
    * `pip install dnspython`

5. Run All Python Files in the Background
    * run `nohup python3 DNS_Server.py & nohup python3 COM_Server.py & nohup python3 EDU_Server.py & nohup python3 GOV_Server.py & nohup python3 IN_Server.py &`
    * verify the processes are running - `ps aux | grep python3`
    * to kill a process - kill -9 <PID>

#To test the server 

- run the Client.py file provided in your local machine and simply enter the domain