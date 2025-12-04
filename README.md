# CS122A Project – Instructions

This repo contains our CS122A project code:
- ddl.sql        → database schema (HW2)
- test_db.py     → test script for Python ↔ MySQL connection
- project.py     → main project file

Each of us must run the project *locally* using MySQL setup.

---

## 1. Requirements
- MySQL Server + MySQL Workbench
- Python 3
- Install MySQL connector:
  pip3 install mysql-connector-python

---

## 2. Clone the Repo
cd <any folder>
git clone <REPO_URL>
cd cs122a_project

---

## 3. Create the Database (only once)
In MySQL Workbench:

CREATE DATABASE cs122a_project;
USE cs122a_project;

---

## 4. Set Your Own MySQL Password (IMPORTANT)
Each teammate must edit these files *locally*:

### test_db.py
Update this to your own MySQL username + password:

conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="YOUR_PASSWORD",
    database="cs122a_project"
)

### project.py
Update the same values in get_connection():

def get_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="YOUR_PASSWORD",
        database="cs122a_project"
    )

Do NOT commit your password to GitHub.

---

## 5. Test Your Setup
Run:

python3 test_db.py

Expected output:
(1,)

If you don't see this, check your password, MySQL server, and database name.

---

## 6. Running the Project (so far)
We currently support the “import” function.

Place your CSV folder in the repo:

cs122a_project/
    ddl.sql
    test_db.py
    project.py
    test_data/
        User.csv
        AgentClient.csv
        ...

Run the import:

python3 project.py import test_data

This drops tables, recreates them using ddl.sql, and loads all CSVs.

---

## 7. Work Split 
- Member 1: import function + schema
- Member 2: insertAgentClient, addCustomizedModel, deleteBaseModel, listInternetService
- Member 3: countCustomizedModel, topNDurationConfig, listBaseModelKeyWord, NL2SQL

Each person should create their own branch, push changes, then open a Pull Request.

