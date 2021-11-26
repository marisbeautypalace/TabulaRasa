# TabulaRasa
interd. Project HS Osnabrueck

## Mockup
![mockup](https://user-images.githubusercontent.com/37381176/142486864-53c861e0-ae5c-41d5-bc00-815e4279702b.png)

Creating a rasa chatbot to answer FAQs and manage event registration for Kompetenzzentrum 4.0 Lingen

## Setup Rasa X server (Docker)

1. Download the install script for Rasa X either for a specific version 
```
curl -sSL -o install.sh https://storage.googleapis.com/rasa-x-releases/0.42.6/install.sh
```
or edge version
```
curl -sSL -o install.sh https://storage.googleapis.com/rasa-x-releases/latest/install.sh
```

2. Install Rasa X
```
sudo bash ./install.sh
```

3. Start up Rasa X in the Backround
```
cd /etc/rasa
sudo docker-compose up -d
```

4. Set up your password
```
cd /etc/rasa
sudo python3 rasa_x_commands.py create --update admin me <PASSWORD>
```

For more Information also see:
(https://rasa.com/docs/rasa-x/installation-and-setup/install/docker-compose/)

## Connect Rasa X with your Git Reposetory

1. Start Rasa X within your webbrowser and navigate to the "Connect to a reposetory" option

2. Clone your Git Repos URL with SSH and paste it in the "SSH for repository" field in Rasa X

3. For the filed "Target branch" choose "master"

4. Copy the SSH deply key from Rasa X and paste ist into your Git Repos Settings/Deploy keys. Title the key and give write accsess

5. Press "Veryfy connection" Button

## Set up Docker

1. 

## Rasa installation (local)

1. Create a virtual enviroment with python version 3.7
```
conda create --name tabalurasa python==3.7
```

2. Activate the virtual enviroment
```
conda activate tabularasa
```

3. Use an older version of pip due to backtracking runtime issue
(https://stackoverflow.com/questions/65122957/resolving-new-pip-backtracking-runtime-issue)
```
python -m pip install --upgrade pip==20.2
```

4. Install rasa
```
pip install rasa
```

5. Copy this repository 
https://support.atlassian.com/bitbucket-cloud/docs/clone-a-git-repository/

6. Open the project in your favourite IDE

7. Create a settings.json in the project directory (root) with the following content:
```
{
    "python.pythonPath": "C:\\XXXXX\\XXXXX\\XXXXX\\XXXXX\\python.exe",
    "terminal.integrated.shell.windows":"C:\\Windows\\System32\\cmd.exe",
    "terminal.integrated.shellArgs.windows": ["/K", "C:\\XXXXX\\XXXXX\\XXXXX\\activate.bat C:\\XXXXX\\XXXXX\\XXXXX\\tabularasa"]
}
```

8. Adjust the path to the corresponding files e.g.: 
```
{
    "python.pythonPath": "C:\\DEV\\miniconda3\\envs\\tabularasa\\python.exe",
    "terminal.integrated.shell.windows":"C:\\Windows\\System32\\cmd.exe",
    "terminal.integrated.shellArgs.windows": ["/K", "C:\\DEV\\miniconda3\\Scripts\\activate.bat C:\\DEV\\miniconda3\\envs\\tabularasa"]
}
```

9. Install spacy for advanced natural language processing
```
pip install spacy
```

10. Check your rasa version
```
rasa --version
```
This is my output: 
```
This is my output:
Rasa Version      :         2.8.12
Minimum Compatible Version: 2.8.9
Rasa SDK Version  :         2.8.2
Rasa X Version    :         0.42.4
Python Version    :         3.7.11
Operating System  :         Windows-10-10.0.19041-SP0
Python Path       :         c:\dev\miniconda3\envs\tabularasa\python.exe
```

11. Train the rasa model
```
rasa train
```

12. Interact with the bot via terminal
```
rasa shell
```

For more information see the official rasa documentation:
https://rasa.com/docs/rasa/

## Access Rasa X server
1. Use the network of the hs osnabrück (e. g. via eduVPN)

2. Open 131.173.65.71/login in your favourite browser and login with credentials



