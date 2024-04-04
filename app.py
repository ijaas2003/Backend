from flask import Flask, jsonify, make_response, request
from flask_cors import CORS
from pymongo import MongoClient
import logging
import re
import datetime
import errno
from schema.schema import faculty_schema, student_schema
from Authendication import GeneratedToken
from src.Conversion import Conversion as StartGenerate;
import os









app = Flask(__name__)
CORS(app)





# ! Working Directory
current_dir = os.getcwd();
print(current_dir)







# ! Logging
logging.basicConfig(filename='User_Log.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')









# ! Regex 
Email_Regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
Alpha_Regex = r'^[a-zA-Z]+$'







#! DB Connectivity 
try:
    client = MongoClient('mongodb://localhost:27017', maxPoolSize=50, minPoolSize=10)
    db = client['QA_Generation']
    print("Connected to MongoDB")
except OSError as e:
    if e.errno:
        print("Socket error: An operation was attempted on something that is not a socket.")
    else:
        print("OSError:", e)
except Exception as e:
    print("Error:", e)

# Create 'users' collection if it doesn't exist
if 'users' not in db.list_collection_names():
    db.create_collection('users')













# ! Routing 
@app.route('/', methods=['GET'])
def example():
    return "Welcome"













@app.route('/StudentLogin', methods=['POST'])
def student_login():
    data = request.json
    username, email, question_id, course = str(data['username']), str(data['email']), str(data['queid']), str(data['Course'])
    data['exp'] = datetime.datetime.now() + datetime.timedelta(days=1)
    if re.match(Email_Regex, email):
        print(username, email, course, question_id)
        Token = GeneratedToken(data)  # Assuming this function is defined correctly
        userData = db['users'].find_one({ "email":email, "QueId": question_id });
        if userData == None:
            datas = {
                "name": username,
                "email": email,
                "course": course,
                "QueId": question_id
            }
            res = db['users'].insert_one(datas);
            if res.acknowledged:
                datas["_id"] = str(datas['_id'])
                return jsonify({"message": "success", "Token": f"{Token}", "userData": datas}), 200;
        else:
            return jsonify({"message": "Continue Exam"}), 200
    else:
        return jsonify({"error": "Email Error"}), 422






@app.route('/LoginToDash', methods=['POST'])
def LoginToDash():
    data = request.json;
    print(data);
    
    return jsonify({ "message": "success" })












@app.route('/FacultyRegister', methods=["POST"])
def faculty_register():
    data = request.json
    faculty_name, faculty_email, faculty_pass, faculty_confirm_pass, faculty_dept, faculty_taught = (
        str(data['username']), str(data['email']), str(data['pass']), str(data['c_pass']), str(data['dept']), str(data['taught'])
    )
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
                return jsonify({"error": "Enter Valid subject name"})
        else:
            return jsonify({"error": "Enter valid Department"})
    else:
        return jsonify({"error": "Enter valid Email or Name"})













@app.route('/FacultyLogin', methods=['POST'])
def faculty_login():
    response = make_response({"message": "Success"})
    response.status_code = 201
    return response














@app.route('/upload', methods=["POST"])
def upload_file():
    uploaded_file = request.files['file']
    File_path = os.path.join(current_dir, 'Pdf', uploaded_file.filename);
    uploaded_file.save(File_path);
    print(StartGenerate(uploaded_file.filename, "Data.txt"));
    return 'File uploaded successfully';






if __name__ == '__main__':
    app.run()
