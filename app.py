from flask import Flask, jsonify, make_response, request
from flask_cors import CORS
from pymongo import MongoClient;
import logging;
import re
import jwt;
import datetime





app = Flask(__name__)
CORS(app)


# TODO This is a logging data of an user 
logging.basicConfig(filename='User_Log.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")


# ! Regex
Email_Regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
Name_Regex  = r'^[a-zA-Z]+$';




# ! Routes
@app.route('/', methods=['GET'])
def Example():
    return "Welcome";








@app.route('/Login', methods=['POST'])
def StudentLogin():
    data = request.json;
    Username, Email, QuestionID = str(data['username']), str(data['email']), str(data['queid']);
    if re.match(Email_Regex, Email):
        print(Username, Email, QuestionID)
        
        return jsonify({"message":"success"})
    else:
        return jsonify({"error":"Email Error"})







@app.route('/FacultyRegister', methods=["POST"])
def FacultyReg():
    data = request.json;
    FacultyName, FacultyEmail, FacultyPass, FacultyConF_Pass = str(data['username']), str(data['email']), str(data['pass']), str(data['c_pass']);
    print(FacultyEmail, FacultyName, FacultyConF_Pass, FacultyPass)
    if any([FacultyEmail == "", FacultyConF_Pass == "", FacultyName == "", FacultyPass == ""]):
        return jsonify({"error": "Please Enter all the Fields"})
    if all([re.match(Email_Regex, FacultyEmail), re.match(Name_Regex, FacultyName)]):
        if FacultyPass == FacultyConF_Pass:
            return jsonify({"message":"success"});
        else:
            return jsonify({"error":"Password Does Not Match"})
    else:
        return jsonify({"error": "Enter valid Email or Name"})






@app.route('/FacultyLogin', methods=['POST'])
def FacultyRegister():
    response = make_response({"message": "Success"})
    response.status_code = 201;
    return response;




if __name__ == '__main__':
    app.run()
