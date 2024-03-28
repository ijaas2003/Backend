from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient;
import re
app = Flask(__name__)
CORS(app)


# ! Regex
Email_Regex = r'^[a-zA-Z]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# ! Routes
@app.route('/', methods=['GET'])
def Example():
    return "Welcome";


@app.route('/Login', methods=['POST'])
def Show():
    data = request.json;
    Username, Email, QuestionID = str(data['username'], data['email'], data['queid']);
    if re.match(Email_Regex, Email):
        print(Username, Email, QuestionID)
        return jsonify({"message":"success"})
    else:
        return jsonify({"error":"Email Error"})






if __name__ == '__main__':
    app.run()
