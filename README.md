# TabulaRasa
interd. Project HS Osnabrueck

## Mockup
![mockup](https://user-images.githubusercontent.com/37381176/142486864-53c861e0-ae5c-41d5-bc00-815e4279702b.png)

Creating a rasa chatbot to answer FAQs and manage event registration for Kompetenzzentrum 4.0 Lingen

# Rasa installation (local)

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
