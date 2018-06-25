import datetime
import logging
import os
import socket

from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
import json

app = Flask(__name__)


def is_ipv6(addr):
    """Checks if a given address is an IPv6 address."""
    try:
        socket.inet_pton(socket.AF_INET6, addr)
        return True
    except socket.error:
        return False


# [START example]
# Environment variables are defined in app.yaml.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    email = db.Column(db.String(50), primary_key = True)
    password = db.Column(db.String(50))

class Details(db.Model):
    first = db.Column(db.String(50))
    last  = db.Column(db.String(50))
    address = db.Column(db.String(200))
    phone = db.Column(db.String(10), primary_key = True)
    desc = db.Column(db.String(500))
    salary = db.Column(db.String(50))
    sign = db.Column(db.LargeBinary())

@app.route('/')
def index():
 error = request.args.get('error')
 message = request.args.get('message')
 return render_template('index.html', error = error, message = message )

@app.route('/register',methods=['POST'])    
def register():
        #username = request.form['name']
        #password = request.form['password']
        #email = request.form['email']
        user = request.get_json()
        username = user["data"]["email"]
        password = user["data"]["password"]
        print(username)
        print(password)
        user = User(password = password, email = username)
        db.session.add(user)
        db.session.commit()
        return  json.dumps({'error':False}), 200, {'ContentType':'application/json'}
        #return render_template('index.html', message = "Succesfully registered. Please login to continue!")

@app.route('/login',methods=['POST'])    
def login():
     # read the posted values from the UI
    user = request.get_json()
    username = user["data"]["email"]
    password = user["data"]["password"]
    print(username)
    print(password)
    user =User.query.filter_by(email = username, password = password).first()
    if user :
      return  json.dumps({'error':False}), 200, {'ContentType':'application/json'}
    else:
       return json.dumps({'error':True}), 500, {'ContentType':'application/json'} 


@app.route('/welcome.html')
def handler():
  message = request.args.get('message')  
  if message:
    return render_template('welcome.html', message = message) 
  else:
    return render_template('welcome.html')


@app.route('/process')
def process():
  submission = request.args.get('submission')
  return render_template('process.html', submission = submission)  
     
@app.route('/desc',methods=['POST'])    
def  userdetails():
     # read the posted values from the UI
    user = request.get_json()
    first = user["data"]["firstName"]
    last  = user["data"]["lastName"]
    phone = user["data"]["phonenumber"]
    salary = user["data"]["salary"]
    desc = user["data"]["description"]
    address = user["data"]["address"]
    sign = user["data"]["signature"]

    details = Details(first = first, last = last, phone = phone, salary = salary, 
                      desc = desc , address = address, sign = bytes(sign,encoding = 'utf-8'))
    db.session.add(details)
    db.session.commit()
    return  json.dumps({'error':False}), 200, {'ContentType':'application/json'}
      
@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
