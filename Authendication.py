from flask import Blueprint, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity

auth_bp = Blueprint('Authendication', __name__)
secrete_Key = "QA_Generation";

def GeneratedToken(username):
     print(username);
     Token = create_access_token(identity=username);
     return Token;



