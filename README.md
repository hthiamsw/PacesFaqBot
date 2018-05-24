# Chatbot-Verification

Project for Chatbot-Verification done by Liu Zhemin (zliu023@e.ntu.edu.sg)

## Getting Started Guide

### Getting Started for macOS and Unix-like

To run the server for this project, we will do the following:

1. Install `pip`
2. Install `virtualenv` and activate it
3. Install all python dependecies for this project
4. Run the server

First, we will install pip by following installation guide at 
https://pip.pypa.io/en/stable/installing/

```shell
$ curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
$ python get-pip.py
```

Next, we will install `virtualenv` using `pip`, create a virtual environment, and activate the 
environment. 

```shell
$ sudo python -m pip install virtualenv
$ virtualenv venv_CV
$ source venv_CV/bin/activate
```

Next, we will install all requirements/dependencies for this project using `pip`.

```
$ pip install -r requirements.txt
```

Finally, we start the server using the followin command:

```shell
# Make sure you are in <root> folder before running the server

# Run the server.
# The website can be accessed at http://localhost:5000
$ python server.py
```

# Invoke the training of text classifier.
The script is in <root>/data/train_clf.py

```shell
# Make sure you are in <root> folder before running the script
$ python data/train_clf.py
```

At the end of our development, we call `deactivate` in command line to deactivate `virtualenv`.

We don't install these dependecies everytime when we want to develop for this project. A normal 
workflow would be:

```shell
# In <root>
$ source venv_CV/bin/activate

$ python server.py

# When you are done
$ deactivate
```
