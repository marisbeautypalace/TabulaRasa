# TabulaRasa
interdisciplinary Project HS Osnabrueck

## UI
![MicrosoftTeams-image](https://user-images.githubusercontent.com/37381176/155945700-2f5ed1e2-1265-4db7-af8b-85cb3ac1611b.png)
![MicrosoftTeams-image (1)](https://user-images.githubusercontent.com/37381176/155945816-9f39cf33-5f5a-46b2-b38e-ced2335db478.png)


Creating a rasa chatbot to answer FAQs and manage event registration for Kompetenzzentrum 4.0 Lingen

## Setup Rasa X server (Docker)

1. Download the install script for Rasa X either for a specific version 
```
curl -sSL -o install.sh https://storage.googleapis.com/rasa-x-releases/1.0.1/install.sh
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

5. Press "Verify connection" Button

## Set up Docker Compose for the Docker Image with Spacy & Action Server

1. Download the Rasa X Docker-compose.yml (in this case for Version == 1.0.1)
```
wget -qO docker-compose.yml https://storage.googleapis.com/rasa-x-releases/1.0.1/docker-compose.ce.yml
```

2. Create a directory for the Rasa-Sevice Dockerfile (e. g. "rasa-service")
```
sudo mkdir rasa-service
```

3. Within the directrory create a Dockerfile
```
sudo nano Dockerfile
```

4. Paste this code to extend the Dockerimage with Spacy
```
ARG RASA_IMAGE
FROM ${RASA_IMAGE}

USER root

RUN pip install -U pip setuptools wheel
RUN pip install -U spacy

RUN python -m spacy download de_core_news_lg

USER 1001
```
5. Create a directory for the Rasa-Action Dockerfile (e. g. "rasa-action")
```
sudo mkdir rasa-action
```

6. Within the directrory create a Dockerfile
```
sudo nano Dockerfile
```

7. Paste this code to extend the Dockerimage for the Action Server
```
# Extend the offical Rasa SDK image
FROM rasa/rasa-sdk:2.8.2

# Use Subdirectory as working directory
WORKDIR /app

# Copy any additional custom requirements, if necesarry (uncomment next line)
# COPY actions/requirements.txt ./

# Change User
USER root

# Install extra reqirements for actions, if necesarry (uncoment next line)
# RUN pip install -r requirements.txt

# Copy actions folder to working directory
COPY ./actions /app/actions

# Change User
USER 1001
```

8. Within the rasa-action folder create a subfolder 'actions' for all custom actions files and the requirements.txt file. Paste the Pythone code into the files and the required libraries into the .txt file
```
cd etc/rasa/rasa-actions
sudo mkdir actions
sudo nano actions/actions.py
sudo nano actions/__init__.py
sudo nano actions/requirements.txt
```

9. Change permissions for rasa-service and rasa-action respectively
```
sudo chmod 775 -R rasa-service
sudo chmod 775 -R rasa-action
```

10. In the docker-compose.yml file, adapt the x-rasa-services: &default-rasa-service section
```
x-rasa-services: &default-rasa-service
  build:
    context: ./rasa-service
    args:
      RASA_IMAGE: "rasa/rasa:${RASA_VERSION}-full"
  restart: always
  volumes:
      - ./.config:/.config
.....
```

11. In the docker-compose.yml file, adapt the app section
```
  app:
    build:
      context: ./rasa-action
    restart: always
    expose:
      - "5055"
    depends_on:
      - rasa-production
```
12. Rebuild the Docker image
```
sudo docker-compose down
sudo docker-compose build
sudo docker-compose up -d
```

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
Rasa Version      :         2.8.16
Minimum Compatible Version: 2.8.9
Rasa SDK Version  :         2.8.2
Rasa X Version    :         1.0.1
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

## UI maintenance
The UI is build with rasa webchat. A chat widget to deploy virtual assistants made with rasa or botfront on any website. 

For more information see the rasa webchat project:
https://github.com/botfront/rasa-webchat

The script which contains the body, the parameters and other features you will find here:
```
index.html
```


