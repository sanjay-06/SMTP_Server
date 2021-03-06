# A Flask application to receive incoming mails
# The SendGrid Inbound Parse Webhook is used to receive incoming emails

from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request
import os

from modules.db.dbConnection import MongoConnect
from modules.mail.parseRecvMail import extractDetails
from modules.auth.encrypt import encryptAES

app = Flask(__name__)

# Receive POST Requests at the /email endpoint
@app.route('/email', methods=['POST'])

def receive_email():
    """Receives an incoming email, encrypts the contents, and stores the encrypted in email in a MongoDB database"""
    print("Received mail")
    username, fromMailId, subject, body = extractDetails(request)

    client = MongoConnect.getConnection()
    dbName = os.environ.get("DBNAME")
    userCollectionName = os.environ.get("USERCOLLNAME")
    UserCollection = client[dbName][userCollectionName]

    user = UserCollection.find_one({"username":username})

    if user:
        encryptText = fromMailId + '+' + subject + '+' + body
        ciphertext, tag, nonce = encryptAES(username, encryptText)
       
        mailCollectionName = os.environ.get("MAILCOLLNAME")
        InMailCollection = client[dbName][mailCollectionName]
    
        dataDocDict = {'username': username, 'ciphertext': ciphertext, 'tag': tag, 'nonce': nonce}
        print(dataDocDict)
        InMailCollection.insert_one(dataDocDict)
    else:
        print("Received email for user that does not exist")

    return ''

def startReceiveMails():
    """Starts the flask application"""
    app.run(host= '0.0.0.0')
    