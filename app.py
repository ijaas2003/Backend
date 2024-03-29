from flask import Flask, jsonify, make_response, request
from flask_cors import CORS
from pymongo import MongoClient
import logging
import re
import errno

app = Flask(__name__)
CORS(app)

# !Initialize logging
logging.basicConfig(filename='User_Log.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# !Define Regex patterns
Email_Regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
Alpha_Regex = r'^[a-zA-Z]+$'


# !MongoDB Connection
try:
    client = MongoClient('mongodb://localhost:27017', maxPoolSize=50, minPoolSize=10)
    db = client['QA_Generation']
    collection = db['Faculty']    
    print("Connected to MongoDB")
except OSError as e:
    if e.errno:
        print("Socket error: An operation was attempted on something that is not a socket.")
    else:
        print("OSError:", e)
except Exception as e:
    print("Error:", e)



# Routes
@app.route('/', methods=['GET'])
def example():
    return "Welcome"


@app.route('/Login', methods=['POST'])
def student_login():
    data = request.json
    username, email, question_id = str(data['username']), str(data['email']), str(data['queid'])
    if re.match(Email_Regex, email):
        print(username, email, question_id)
        return jsonify({"message": "success"})
    else:
        return jsonify({"error": "Email Error"})


@app.route('/FacultyRegister', methods=["POST"])
def faculty_register():
    data = request.json
    faculty_name, faculty_email, faculty_pass, faculty_confirm_pass, faculty_dept, faculty_taught = (
        str(data['username']), str(data['email']), str(data['pass']), str(data['c_pass']), str(data['dept']), str(data['taught'])
    )
    print(data)
    if any([faculty_email == "", faculty_confirm_pass == "", faculty_name == "", faculty_pass == "", faculty_taught == "", faculty_dept == ""]):
        return jsonify({"error": "Please Enter all the Fields"})
    if all([re.match(Email_Regex, faculty_email), re.match(Alpha_Regex, faculty_name)]):
        if re.match(Alpha_Regex, faculty_dept):
            if re.match(Alpha_Regex, faculty_taught):
                if faculty_pass == faculty_confirm_pass:
                    return jsonify({"message": "success"})
                else:
                    return jsonify({"error": "Password Does Not Match"})
            else:
                return jsonify({"error": "Enter Valid subject name"});
        else:
            return jsonify({"error": "Enter valid Department"})
    else:
        return jsonify({"error": "Enter valid Email or Name"})


@app.route('/FacultyLogin', methods=['POST'])
def faculty_login():
    response = make_response({"message": "Success"})
    response.status_code = 201
    return response


if __name__ == '__main__':
    app.run()
