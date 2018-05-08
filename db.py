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
        tables = self.queryall("SELECT name FROM sqlite_master WHERE type='table';")
         

        if(('categories',) not in tables): 
            self.execute('''CREATE TABLE categories
                            (name TEXT,
                            num INTEGER);''')

        if(('notes',) not in tables): 
            self.execute('''CREATE TABLE notes
                            (id INTEGER,
                            content TEXT,
                            created_date TEXT,
                            completed_date TEXT,
                            hidden_date TEXT,
                            completed TEXT,
                            hidden TEXT,
                            category TEXT,
                            importance INTEGER);''')

        if(('accounts',) not in tables):
            self.execute('''CREATE TABLE accounts
                            (username TEXT,
                            password TEXT);''')

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
    
    def queryall(self,command):
        try:
            self.cur.execute(command)
            return self.cur.fetchall()
        except:
            print("Database Error!")
    
    def queryone(self,command):
        try:
            self.cur.execute(command)
            return self.cur.fetchone()
        except:
            print("Database Error!")

    def execute(self,command):
        try:
            self.cur.execute(command)
            self.conn.commit()
        except:
            print("Database Error!")

    def executevar(self,command,operands):
        try:
            self.cur.execute(command,operands)
            self.conn.commit()
        except:
            print("Database Error!")

    def new_user(self,username,password):
        self.cur.execute("INSERT INTO accounts VALUES(?, ?)",(username, hashlib.sha256(str(password).encode()).hexdigest()))
        self.conn.commit()

    def del_user(self,username):
        self.cur.execute("DELETE FROM accounts WHERE username=?",(username,))
        self.conn.commit()