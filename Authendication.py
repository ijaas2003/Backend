import jwt

secrete_Key = "QA_Generation";

def GeneratedToken(data):
     print(data);
     Token = jwt.encode(data, secrete_Key, algorithm="HS256");
     return Token;