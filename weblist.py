#!/usr/bin/python3
import hashlib
from datetime import datetime
from db import *
from flask import Flask, render_template, request, Response
from functools import wraps

app = Flask(__name__)      
web_db = list_database('weblist.conf')

def check_auth(username, password):

    password = hashlib.sha256(str(password).encode()).hexdigest()
    db_pass = web_db.executevar("SELECT password FROM accounts WHERE username=?",(username,))
    if db_pass !=None:
        return password == db_pass[0][0]
    else:
        return False

def getcats():
    return web_db.execute("SELECT name FROM categories;")

def getcatdata():
    return web_db.execute("SELECT name,num FROM categories;")

def createcat(name):
    web_db.executevar("INSERT INTO categories VALUES(?,0)",(name,))

def delcat(name):
    web_db.executevar("DELETE FROM categories WHERE name=?",(name,))
    web_db.executevar("DELETE FROM notes WHERE category=?",(name,))

def delnote(rowid):
    if (web_db.executevar("SELECT completed FROM notes WHERE rowid=?",(rowid,))[0][0]) == 'False':
        web_db.executevar("UPDATE categories SET num = num - 1 WHERE name IN(SELECT category FROM notes WHERE rowid=?)",(rowid,))#HERE
    web_db.executevar("DELETE FROM notes WHERE rowid=?",(rowid,))


def completenote(rowid):
    if (web_db.executevar("SELECT completed FROM notes WHERE rowid=?",(rowid,))[0][0]) == 'False':
        web_db.executevar("UPDATE categories SET num = num - 1 WHERE name IN(SELECT category FROM notes WHERE rowid=? and completed='False')",(rowid,))
    web_db.executevar("UPDATE notes SET completed=?,completed_date=strftime('%Y-%m-%d','now','localtime') WHERE rowid=?",("True",rowid))

def changecontent(content,rowid):
    print('Content: ' + content)
    print('Rowid: ' + str(rowid))
    web_db.executevar("UPDATE notes SET content=? WHERE rowid=?",(content,rowid))


def changeimportance(importance,rowid):
    print('Importance: ' + str(importance))
    print('Rowid: ' + str(rowid))
    web_db.executevar("UPDATE notes SET importance=? WHERE rowid=?",(importance,rowid))


def getnotes(cat):
    unhidenotes()
    if cat == 'All':
        return web_db.execute("SELECT content,importance,rowid FROM notes WHERE completed='False' AND hidden='False' ORDER BY importance DESC")
    elif cat == 'Hidden':
        return web_db.execute("SELECT content,importance,rowid FROM notes WHERE hidden='True' and completed='False' ORDER BY importance DESC")
    elif cat == 'Completed':
        return web_db.execute("SELECT content,importance,rowid FROM notes WHERE completed='True' ORDER BY importance DESC")
    else:
        return web_db.executevar("SELECT content,importance,rowid FROM notes WHERE hidden='False' and category=? and completed='False' ORDER BY importance DESC",(cat,))


def unhidenotes():
    web_db.execute("UPDATE notes SET hidden='False' WHERE hidden='True' and strftime('%Y-%m-%d','now','localtime') >= hidden_date")

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

@app.route('/weblist',methods=["POST","GET"])
@requires_auth
def main():
    if request.method == "POST":
        ln = list(request.form.keys())
        print(ln)
        print(request.form['action'])
        if('Delete' in ln):
            delnote(request.form['Delete'])
        if('content' in ln):
            changecontent(request.form['content'],request.form['rowid'])
        if('importance' in ln):
            changeimportance(request.form['importance'],request.form['rowid'])
        elif('Complete' in ln):
            completenote(request.form['Complete'])
        print(request.form['action'])
        return render_template('main.html',dats=getnotes(request.form['action']),names=getcats(),ip ='/weblist',selected=request.form['action'])
                            
    return render_template('main.html',dats=getnotes('All'),names=getcats(),selected='All',ip='/weblist')

@app.route('/weblist/catadd',methods=["POST","GET"])
@requires_auth
def catadd():
    if request.method == "POST":
        ln = list(request.form.keys())
        print(ln)
        if('name' in ln):
            createcat(request.form['name'])
        elif('delete' in ln):
            delcat(request.form['delete'])


    return render_template('catadd.html',dats=getcatdata(),ip='/weblist/catadd')
                            
@app.route('/weblist/noteadd',methods=["POST","GET"])
@requires_auth
def noteadd():
    if request.method == "POST":
        ln = list(request.form.keys())
        if 'hidden' in ln:
            web_db.executevar("INSERT INTO notes VALUES(?,?,NULL,?,'False','True',?,?)",(request.form['content'],datetime.now().strftime('%Y-%m-%d'),request.form['date'],request.form['category'],request.form['importance']))
        else:
            web_db.executevar("INSERT INTO notes VALUES(?,?,NULL,NULL,'False','False',?,?)",(request.form['content'],datetime.now().strftime('%Y-%m-%d'),request.form['category'],request.form['importance']))
        web_db.executevar("UPDATE categories SET num = num + 1 WHERE name=?",(request.form['category'],))
    return render_template('noteadd.html',names=getcats(),ip='/weblist/noteadd')
                            
if __name__ == '__main__':
        app.run(host='0.0.0.0', port=5000)
