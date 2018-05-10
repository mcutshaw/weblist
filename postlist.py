#!/usr/bin/python3
import hashlib
import configparser
import sqlite3
import datetime
from db import *
from flask import Flask, render_template, request, Response
from functools import wraps

app = Flask(__name__)      

conn,cur = dbconnect()
dbclose(conn)
def check_auth(username, password):
    conn,cur = dbconnect()
    password = hashlib.sha256(str(password).encode()).hexdigest()
    cur.execute("SELECT password FROM accounts WHERE username=?",(username,))
    db_pass = cur.fetchone()
    dbclose(conn)
    if db_pass !=None:
        return password == db_pass[0]
    else:
        return False
def check_role(username,password,role):
    if not check_auth(username,password):
        return false
    else:
        conn,cur = dbconnect()
        cur.execute("SELECT role FROM accounts WHERE username=?",(username,))
        roles_list = cur.fetchone()
        dbclose(conn)
        return (roles_list[0] == role or roles_list[0] == 'all')
def get_logs(username):
    conn,cur = dbconnect()
    cur.execute("SELECT logs FROM accounts WHERE username=?;",(username,))
    logs = cur.fetchone()
    logs = logs[0]
    dbclose(conn)
    return logs

def check_logs(username,password,logs):
    if not check_auth(username,password):
        return false
    else:
        conn,cur = dbconnect()
        cur.execute("SELECT logs FROM accounts WHERE username=?",(username,))
        log_list = cur.fetchone()
        dbclose(conn)
        return (log_list[0] == logs or log_list[0] == 'all')


def authenticate():
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/postlist',methods=["POST","GET"])
@requires_auth
def home():
    auth = request.authorization
    if (check_role(auth.username, auth.password, 'reader')):
        name_list = load_namelist(get_logs(auth.username))
        if request.method == "POST":
            ln = list(request.form.keys())
            for item in ln:
                print(item)
                if item == 'action':
                    data = []
                    if(check_logs(auth.username, auth.password,request.form[item])):
                        conn,cur = dbconnect()
                        cur.execute("SELECT contents,date,rowid FROM logs WHERE header=? ORDER BY date DESC;",(request.form[item],))
                        for log in cur.fetchall():
                            data.append(log)
                        dbclose(conn)
                    return render_template('home.html',names=name_list,ip="/postlist",dats=data,selected=request.form['action'])
                            
        return render_template('home.html',names=name_list,ip="/postlist",dats=[],selected=None)
    return authenticate()

@app.route('/postlist/manager',methods=["POST","GET"])
@requires_auth
def manager():
    auth = request.authorization
    if(check_role(auth.username,auth.password,'manager')):
        user_list = load_userlist()
        if request.method == "POST":
            ln = list(request.form.keys())
            if('username' in ln):
                username = request.form['username']
                password = request.form['password']
                role = request.form['role']
                logs = request.form['logs']
                new_user(username,password,role,logs)
            elif('delete' in ln):
                del_user(request.form['delete'])

            user_list = load_userlist()
            return render_template('manager.html',ip="/postlist/manager",dats=user_list)
                        
        return render_template('manager.html',ip="/postlist/manager",dats=user_list)
    return authenticate()

@app.route('/postlist/data',methods=["POST"])
@requires_auth
def data():
    auth = request.authorization
    if(check_role(auth.username,auth.password,'writer')):

        name_list = load_namelist()
        ln = request.form.keys()
        conn,cur = dbconnect()
        for item in ln:
            if(check_logs(auth.username,auth.password,item)):
                cur.execute("INSERT INTO logs VALUES(?,?,?);",(item,request.form[item],datetime.datetime.now()))
        conn.commit()
        dbclose(conn)
        return render_template('blank.html')
    return authenticate()


if __name__ == '__main__':
        app.run(host='0.0.0.0', port=5000)
