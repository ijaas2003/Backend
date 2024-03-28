from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def Example():
    
    return "Welcome";





@app.route('/Login', methods=['POST'])
def Show():
    data = request.json;
    Username, Email, QuestionID = data['username'], data['email'], data['queid'];
    print(Username, Email, QuestionID)
    return jsonify({"message":"success"})






if __name__ == '__main__':
    app.run()
