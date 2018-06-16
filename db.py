#!/usr/bin/python3
import hashlib
import configparser
import sqlite3

class list_database:

    def __init__(self,config):
        try:
            Config = configparser.ConfigParser()
            Config.read(config)
            self.db = Config['Main']['Database']
        except:
            print("Config Error!")
            exit()
        self.connect()
        tables = self.execute("SELECT name FROM sqlite_master WHERE type='table';")
         

        if(('categories',) not in tables): 
            self.execute('''CREATE TABLE categories
                            (name TEXT PRIMARY KEY,
                            num INTEGER NOT NULL);''')

        if(('notes',) not in tables): 
            self.execute('''CREATE TABLE notes
                            (content TEXT NOT NULL,
                            created_date DATE NOT NULL,
                            completed_date DATE,
                            hidden_date DATE,
                            completed BOOLEAN CHECK(completed IN("True","False")),
                            hidden BOOLEAN CHECK(hidden IN("True","False")),
                            category TEXT NOT NULL,
                            importance INTEGER NOT NULL);''')

        if(('accounts',) not in tables):
            self.execute('''CREATE TABLE accounts
                            (username TEXT PRIMARY KEY,
                            password TEXT NOT NULL);''')

            print("Create a master user.")
            username = input("Username: ")
            password = input("Password: ")
            password = hashlib.sha256(str(password).encode()).hexdigest()
            self.executevar("INSERT INTO accounts VALUES(?, ?)",(username, password))


    def close(self):
        self.conn.close()

    def connect(self):
        self.conn = sqlite3.connect(self.db)
        self.cur = self.conn.cursor()

    def execute(self,command):
        self.connect()
        self.cur.execute(command)
        self.conn.commit()
        text_return = self.cur.fetchall()
        self.close()
        return text_return

    def executevar(self,command,operands):
        self.connect()
        self.cur.execute(command,operands)
        self.conn.commit()
        text_return = self.cur.fetchall()
        self.close()
        return text_return


    def new_user(self,username,password):
        self.executevar("INSERT INTO accounts VALUES(?, ?)",(username, hashlib.sha256(str(password).encode()).hexdigest()))

    def del_user(self,username):
        self.executevar("DELETE FROM accounts WHERE username=?",(username,))