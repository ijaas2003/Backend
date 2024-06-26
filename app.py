from flask import Flask, jsonify, make_response, request
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from pymongo import MongoClient
import logging
import string
# import json
# import ast
import re
from datetime import datetime,timedelta
import textstat
import errno
from collections import Counter
from schema.schema import faculty_schema, student_schema
from Authendication import GeneratedToken
from Authendication import auth_bp;
from src.Conversion import Conversion as StartGenerate;
import os
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from nltk.corpus import stopwords
from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch
from heapq import nlargest
import random
import numpy as np;
from ChooseQue import RandomQue, ChooseCrtQues;


import gensim.downloader as api

model_path = api.load("glove-wiki-gigaword-300", return_path=True)

if model_path:
    glove_model = api.load("glove-wiki-gigaword-300")
    print("Model loaded from cache")
else:
    glove_model = api.load("glove-wiki-gigaword-300")
    print("Model downloaded")




if not os.path.isdir(os.path.join(nltk.data.find('corpora'), 'stopwords')):
    nltk.download('stopwords')
else:
    stop_words = nltk.corpus.stopwords.words('english')
    stop = list(stop_words)
    st = list(STOP_WORDS)
    for element in st:
        if element not in stop:
            stop.append(element)
    print("Stopwords downloaded");

if not os.path.isfile(os.path.join(nltk.data.find('tokenizers'), 'punkt.zip')):
    nltk.download('punkt')
    
else:
    punctuation_chars = set(punctuation)
    punctuation_chars.remove('-')
# punctuation_chars.add('\n')
    punctuation=list(punctuation_chars)
    print("Punctuations Downloaded")





nlp = spacy.load("en_core_web_lg")


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

# ? Create 'users' collection if it doesn't exist

if 'users' not in db.list_collection_names():
    db.create_collection('users')

if 'tests' not in db.list_collection_names():
    db.create_collection('tests')




# ! JWT Authendication

app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this to a secure key in production
jwt = JWTManager(app)


app.register_blueprint(auth_bp)







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
        Token = GeneratedToken(username)  # Assuming this function is defined correctly
        
    else:
        return jsonify({"error": "Email Error"}), 422









@app.route('/LoginToDash', methods=['POST'])
def LoginToDash():
    data = request.json;
    email, password = data['email'], data['pass']
    print(email, password)
    if not re.match(Email_Regex, email):
        return jsonify({"error": "Invalid Email"});
    userData = db['studentReg'].find_one({"student_email": email});
    print(userData);
    if userData is not None:
        if password == userData['student_pass']:
            return jsonify({"message": "Successfully login", "userId": str(userData['_id'])});
        else:
            return jsonify({"error": "Invalid Password"});
    else:
        return jsonify({"error": "Wrong Email"});













@app.route('/FacultyRegister', methods=["POST"])
def faculty_register():
    data = request.json
    faculty_name, faculty_email, faculty_pass, faculty_confirm_pass, faculty_dept, faculty_taught = (
        str(data['username']), str(data['email']), str(data['pass']), str(data['c_pass']), str(data['dept']), str(data['taught'])
    )
    faculty_name=faculty_name.strip()
    faculty_email=faculty_email.strip()
    if any([faculty_email == "", faculty_confirm_pass == "", faculty_name == "", faculty_pass == "", faculty_taught == "", faculty_dept == ""]):
        return jsonify({"error": "Please Enter all the Fields"})
    if all([re.match(Email_Regex, faculty_email), re.match(Alpha_Regex, faculty_name)]):
        if re.match(Alpha_Regex, faculty_dept):
            if re.match(Alpha_Regex, faculty_taught):
                if faculty_pass == faculty_confirm_pass:
                    userData = db['faculty'].find_one({"faculty_email":faculty_email});
                    if userData == None:
                        datas = {
                            "faculty_name": faculty_name,
                            "faculty_email": faculty_email,
                            "faculty_dept": faculty_dept,
                            "faculty_taught": faculty_taught,
                            "faculty_pass": faculty_pass,
                            "faculty_confirm_pass": faculty_confirm_pass
                        }
                        res = db['faculty'].insert_one(datas);
                        if res.acknowledged:
                            return jsonify({"message": "success"})
                    else: 
                        return jsonify({"error": "User Already Exist"})
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
    data = request.json
    faculty_email, faculty_pass = str(data['email']), str(data['pass'])
    faculty_email=faculty_email.strip()
    faculty_pass=faculty_pass.strip()
    if any([faculty_email == "", faculty_pass == ""]):
        return jsonify({"error": "Enter all fields"})
    
    if re.match(Email_Regex, faculty_email):
        userdata = db['faculty'].find_one({"faculty_email": faculty_email})
        if userdata is not None:
            faculty = userdata.get('_id');
            print(faculty)
            stored_pass = userdata.get('faculty_pass') 
            print(stored_pass)
            if stored_pass == faculty_pass:
                print("success")
                response = make_response({"message": "Successfully Login", "facultyId": str(faculty)})
                response.status_code = 201
                return response
            else:
                return jsonify({"error": "Incorrect password"})
        else:
            return jsonify({"error": "User not found"})
    else:
        return jsonify({"error": "Invalid email format"})







@app.route('/studentReg', methods=['POST'])
def studentReg():
    data = request.json;
    stud_name, stud_pass, stud_repass, stud_course, stud_email = data['username'], data['password'], data['rePassword'], data['Dept'], data['email'];
    
    if any([stud_course == "", stud_email == "", stud_name == "", stud_pass == "", stud_repass == ""]):
        return jsonify({"error": "Please Fill all the Fields"})
    if all([re.match(Email_Regex, stud_email), re.match(Alpha_Regex, stud_name), re.match(Alpha_Regex, stud_course)]):
        if stud_pass == stud_repass:
            check = db['studentReg'].find_one({"student_email": stud_email});
            print(check)
            if check is None:
                student_details = {
                    "student_name": stud_name,
                    "student_email": stud_email,
                    "student_dept": stud_course,
                    "student_pass": stud_pass,
                    "student_repass": stud_repass
                }
                res = db['studentReg'].insert_one(student_details);
                return jsonify({"message": "Successfull Registered"});
            else:
                return jsonify({"error": "user Already Available"})
        else:
            return jsonify({"error": "Password Does not match"})
    else:
        return jsonify({"error": "Check name, email and course"})








@app.route('/upload', methods=["POST"])
def upload_file():
    global FacId;
    systime=datetime.now()
    systime=systime + timedelta(minutes=30)
    # print(systime)
    # print(type(systime))
    uploaded_file = request.files['file']
    startingTime = request.form['startingTime']
    endingTime = request.form['endingTime']
    FacId = request.form['facultyId']
    QueCount=request.form['que_count']
    duration = request.form['duration']
    input_format = '%Y-%m-%dT%H:%M'
    input_format1 = '%H:%M'
    startingTime_convert = datetime.strptime(startingTime, input_format)
    endingTime_convert = datetime.strptime(endingTime,input_format)
    duration_convert=datetime.strptime(duration,input_format1)
    duration_time = duration_convert.time()
    duration_minutes = duration_time.hour * 60 + duration_time.minute
    dur=endingTime_convert - startingTime_convert
    dur_minutes = dur.total_seconds() / 60
    hour,min=map(int,duration.split(':'))
    TimeRem=hour*3600 + min *60
    if type(dur_minutes) == float:
        dur_minutes=int(dur_minutes)
    if startingTime_convert >= systime:
        if endingTime_convert > startingTime_convert:
            if duration_minutes < dur_minutes:
                print("yes")
            else:
                return jsonify({"error": "Provide Correct Duration"})
        else:
            return jsonify({"error": "Provide  correct ending time"})
    else:
        return jsonify({"error": " provide correct starting time"}) 

    File_path = os.path.join(current_dir, 'Pdf', uploaded_file.filename);
    uploaded_file.save(File_path);
    text = StartGenerate(uploaded_file.filename, "Data.txt");
    if text:
        def GenerateId(lens):
            total = string.ascii_uppercase + string.digits;
            Id = ''.join(random.choice(total) for _ in range(lens))
            return Id
        global QuestionId;
        QuestionId = GenerateId(lens=8);
        process = Start(text=text);
        print(process)
        que_count=len(process)
        # print(len(process))
        if int(QueCount) > que_count:
            return jsonify({"error":"Que count Not match "});
        data = {
            "QuestionId": QuestionId,
            "StartingTime": startingTime,
            "EndingTime": endingTime,
            "Duration": TimeRem,
            "quecount":QueCount,
            "FacultyId": FacId
        }
        res = db['questions'].insert_many(process)
        que_res = db['questionstiming'].insert_one(data)
        if all([res.acknowledged, que_res.acknowledged]):
            return jsonify({"message": "Questions Stores"});
        else:
            return jsonify({"error": "Error occur while Generating"})
    else:
        return jsonify({"error": "There is no data in the given pdf"})
    
    
    
    
    
    
def Start(text):
    def remove_page(text):
        pattern = r'\bPage\s+N\d{2}\b'
        c_text=re.sub(pattern,'',text)
        c_text=c_text.replace('\n','')
        return c_text
    c_text=remove_page(text=text)
    text=c_text
    word_token = word_tokenize(text)
    doc=nlp(text)
    sentence_tokens = [sent for sent in doc.sents]
    para=""
    count=0;
    para_list=[]
    for x in sentence_tokens:
        if count>30:
            para_list.append(para)
            para=""
            count=0
        else:
            para=para+str(x)
            count=count+1;
    if para!="":
        para_list.append(para)

    text_list=[[paragraph] for paragraph in para_list]
    capitalized_paragraphs = []
    for paragraph in text_list:
        paragraph_text = paragraph[0]
        doc = nlp(paragraph_text)
        capitalized_text = '. '.join([sent.capitalize() for sent in paragraph_text.split('.')])
        capitalized_paragraphs.append([capitalized_text])
    text_list = capitalized_paragraphs;
    word_freq_list = []

    for text in text_list:
        word_freq = Counter()
        for sentence in text:
            words = sentence.split()
            words = [word.lower() for word in words if word.lower() not in stop and word.lower() not in punctuation]
            word_freq.update(words)
        word_freq_list.append(word_freq)
    max_frequencies = []
    for word_freq in word_freq_list:
        max_frequency = max(word_freq.values(), default=0)
        max_frequencies.append(max_frequency)
    for idx, word_freq in enumerate(word_freq_list, 1):
        max_frequency = max(word_freq.values(), default=1)
        for word in word_freq.keys():
            word_freq[word] /= max_frequencies[idx - 1]
    def tokenize_sentences_regex(text_list):
        pattern = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s'
        long_sentences = []
        for paragraph in text_list:
            tot_sentence = []
            sentences = re.split(pattern, paragraph[0])
            for sentence in sentences:
                if len(sentence) > 10:
                    tot_sentence.append(sentence)
            long_sentences.append(tot_sentence)
        return long_sentences
    long_sentences = tokenize_sentences_regex(text_list)
    sentence_scores = []
    for sublist, word_freq in zip(long_sentences, word_freq_list):
        nested_dict = {}
        for sentence in sublist:
            score = sum(word_freq.get(word.lower(), 0) for word in sentence.split())
            nested_dict[sentence] = score
        sentence_scores.append(nested_dict)
    def generate_summary(sentence_scores):
        summary = nlargest(3, sentence_scores, key=lambda x: sentence_scores[x])
        summary_sentences = [sentence for sentence in summary]
        return summary_sentences
    summaries = []
    for sentence_scores in sentence_scores:
        summary = generate_summary(sentence_scores)
        summaries.append(summary)
    text_doc = []
    for i in text_list:
        para = []
        for j in i:
            para.append(nlp(str(j)))
        text_doc.append(para)
    summary_doc = []
    for i in summaries:
        summary = []
        for j in i:
            summary.append(nlp(str(j)))
        summary_doc.append(summary)
    keys = []
    for doc in text_doc:
        k1 = []
        for sentence in doc:
            doc_sentence = nlp(str(sentence))
            for word in doc_sentence.noun_chunks:
                if word.text.lower() not in stop:
                    k1.append(word.text)
        keys.append(k1)
    keywords = []

    for doc in summary_doc:
        k1 = []
        for sentence in doc:
            doc_sentence = nlp(str(sentence))  # Convert the sentence to a spaCy Doc object
            for word in doc_sentence.noun_chunks:
                if word.text.lower() not in stop:
                    k1.append(word.text)
        keywords.append(k1)

    common_keywords = []
    for keys_list, keywords_list in zip(keys, keywords):
        keys_set = set(keys_list)
        keywords_set = set(keywords_list)
        common = keys_set.intersection(keywords_set)
        common_keywords.append(list(common))
    question_tokenizer = T5Tokenizer.from_pretrained('t5-large',legacy=False)
    question_model = T5ForConditionalGeneration.from_pretrained('Parth/result')
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    question_model = question_model.to(device)
    def get_question(context, answer, model, tokenizer):
        text = "context: {} answer: {}".format(context, answer)
        encoding = tokenizer.encode_plus(text, max_length=384, pad_to_max_length=False, truncation=True, return_tensors="pt").to(device)
        input_ids, attention_mask = encoding["input_ids"], encoding["attention_mask"]
        outs = model.generate(input_ids=input_ids,
                                attention_mask=attention_mask,
                                early_stopping=True,
                                num_beams=5,
                                num_return_sequences=1,
                                no_repeat_ngram_size=2,
                                max_length=72 )
        dec = [tokenizer.decode(ids, skip_special_tokens=True) for ids in outs]
        Question = dec[0].replace("question:", "")
        Question = Question.strip()
        return Question


    def generate_questions(summaries, keywords, model, tokenizer):
        que_pair = []
        for i, summary in enumerate(summaries):
            keys = keywords[i]
            for answer in keys:
                ques = get_question(summary, answer, model, tokenizer)
                que_pair.append((ques, answer.capitalize()))
        return que_pair

    questions = generate_questions(summaries, common_keywords, question_model, question_tokenizer)
    
    def remove_words(input_string, words_to_remove):
        Removed_n = input_string.replace("\n", "");
        words = input_string.split()
        cleaned_words = [word for word in words if word.lower() not in words_to_remove]
        return ' '.join(cleaned_words)


    def generate_distractors(target_word, num_distractors=5, glove_model=None):
        target_words = target_word.split()

        try:
            target_vectors = [glove_model.get_vector(word) for word in target_words]
            target_vector = np.mean(target_vectors, axis=0)
            # Calculate cosine similarity between the target word and all other words in the vocabulary
            similarity_scores = np.dot(glove_model.vectors, target_vector) / (
                np.linalg.norm(glove_model.vectors, axis=1) * np.linalg.norm(target_vector)
            )
            # Sort the words based on their similarity scores
            most_similar_indices = np.argsort(-similarity_scores)
            # Extract top similar words as distractors (excluding the target word itself)
            distractors = [glove_model.index_to_key[idx] for idx in most_similar_indices if glove_model.index_to_key[idx] not in target_words]
            return distractors[:num_distractors]  # Return the specified number of distractors


        except Exception as e:
            print("Error occurred:", e)
            return []


    current_Answer_list = []
    Proper_QA = [];
    RemoveWords = ["its", "a", "the", "this", "page n01", "n01"];
    i = 1;
    for index, (question, answer) in enumerate(questions, start = 1):
        similarity = []
        difficulty = []
        que_diff = ""
        ans = remove_words(answer, RemoveWords);
        target_word = ans.lower()
        ansnlp = nlp(target_word);
        distractors = generate_distractors(target_word, glove_model=glove_model)
        if distractors == []:
            continue;
        else:
            current_Answer_list = random.sample(distractors, min(3, len(distractors)))
            if current_Answer_list != []:
                current_Answer_list.append(target_word)
                random.shuffle(current_Answer_list)
            for similaritys in current_Answer_list:
                doc = nlp(similaritys);
                val = ansnlp.similarity(doc);
                similarity.append(val);
            for value in similarity:
                if value == 1.0:
                    difficulty.append(10)
                elif 0.7 <= value < 1.0:
                    difficulty.append(7)
                elif 0.4 <= value < 0.7:
                    difficulty.append(4)
                else:
                    difficulty.append(0)
            var = textstat.automated_readability_index(question)
            if var < 6 :
                que_diff = "easy"
            elif 6 <= var < 9:
                que_diff = "medium"
            else :
                que_diff = "hard"
            from Format import Format
            question_dict = Format(question, ans, que_diff, current_Answer_list, similarity, difficulty, QuestionId, FacId, var)
        Proper_QA.append(question_dict)
        i+=1;
    return Proper_QA




from bson.objectid import ObjectId
@app.route('/GetUserData/<Type>/<id>')
def GetData(Type,id):
    print(Type, id)
    if Type == "faculty":
        ids = ObjectId(id)
        FacultyData = db['faculty'].find_one({"_id": ids}, {"_id":0});
        Questions = list(db['questionstiming'].find({"FacultyId":id}, {"_id":0}));
        print(FacultyData, Questions)
        if FacultyData is not None:
            return jsonify({"message": "Retrieved Successful", "FacultyData": FacultyData, "questionsData": Questions});
        else:
            return jsonify({"error": "Not available"})
    elif Type == "studentexamdata":
        Studentexam = list(db['studentattended'].find({"QueId": id}, {"_id": 0}));
        for s in range(0, len(Studentexam)):
            ch = db['studentReg'].find_one({"student_email": Studentexam[s]['email']})
            Studentexam[s]['name'] = ch['student_name'];
            Studentexam[s]['dept'] = ch['student_dept'];
        print(Studentexam)
        return jsonify({ "Studentexam": Studentexam })
    else:
        ids = ObjectId(id)
        Userinfo=db['studentReg'].find_one({"_id":ids},{"_id":0});
        Attended = list(db['studentattended'].find({ "email": Userinfo['student_email'] }, { "_id": 0}))
        
        print(Userinfo)
        if Userinfo is not None:
            return jsonify({
                "message": "Retrieved Successful",
                "Userinfo": Userinfo,
                "Attended": Attended if Attended else "No Data"
            })
        else:
            return jsonify({"error": "Not Available "})








easy = [];
medium = []
hard = []
@app.route('/getquestion', methods=['POST'])
def GenerateNQ():
    global Userdata;
    data = request.json
    testToken = str(data['testToken'])
    if testToken == "":
        email,password, Id,  queid, course = (
            str(data['email']),
            str(data['pass']),
            str(data['Id']),
            str(data['queid']),
            str(data['Dept'])
        )
        e = db['studentReg'].find_one({'student_email': email})
        realUser = db['studentReg'].find_one({"_id": ObjectId(Id)});
        if e is not None:
            if str(e['student_email']) != str(realUser['student_email']):
                return jsonify({"error": "It not exact user Email"});
            # print(password ,e['student_pass'])
            if password != e['student_pass']:
                return jsonify({"error": "Password incorrect"})
            quesid = db['questionstiming'].find_one({"QuestionId": queid})
            Questions = list(db['questions'].find({}, {"Id": 0}))
            for que in Questions:
                print(que['Que_Difficulty'])
                if que['Que_Difficulty'] == "easy":
                    easy.append(que)
                elif que['Que_Difficulty'] == "medium":
                    medium.append(que)
                elif que['Que_Difficulty'] == "hard":
                    hard.append(que)
            
            if quesid is not None:
                Token = GeneratedToken(email)
                userData = db['studentattended'].find_one({"email": email, "QueId": queid})
                #print(userData)# this data I will need 
                Userdata = userData;
                if userData is None:
                    datas = {
                        "email": email,
                        "course": course,
                        "QueId": queid,
                        "Easy": 0,
                        "Medium": 0,
                        "Hard": 0,
                        "score": 0,
                        "percent": 0,
                        "Questionsattented": 0
                    }
                    res = db['studentattended'].insert_one(datas)
                    # print(res[1]);
                checkQue = db['questionstiming'].find_one({"QuestionId":userData['QueId']}, {"quecount":1})
                print(int(userData['Questionsattented']) == int(checkQue['quecount']));
                if int(userData['Questionsattented']) == int(checkQue['quecount']):
                    return jsonify({"error": "Already Attended the Test"});
                QueGen = RandomQue(medium)
                questionStructure = {
                    "Questionobjid": str(QueGen['_id']),
                    "Question": QueGen['Question'],
                    "Distractors": QueGen['Distractors'], 
                }
                return jsonify({"message": "Let's Start the Test",  "startTest": Token, "questionStructure": questionStructure, "duration": quesid['Duration']}), 200
            else:
                return jsonify({"error": "Invalid Question Id"})
        else:
            return jsonify({"error": "Invalid email"})
    else:
        print(Userdata);
        duration, queobjid, answer = ( 
            str(data['duration']),
            str(data['queobjid']),
            str(data['answer']) 
        )
        if answer == "":
            return jsonify({"error": "Enter any answer"})
        
        checkQue = db['questionstiming'].find_one({"QuestionId":Userdata['QueId']}, {"quecount":1})
        UpdateduserData = db['studentattended'].find_one_and_update(
                {"_id": Userdata["_id"]},
                {"$inc": 
                    {"Questionsattented": 1}
                },return_document=True
            )
        QueGen = ChooseCrtQues(
                user=UpdateduserData,
                db=db,
                easy=easy,
                medium=medium,
                hard=hard,
                duration=duration,
                answer=answer.lower(), 
                id=queobjid,
                score=UpdateduserData['score']
            )
        if int(checkQue['quecount']) == (UpdateduserData['Questionsattented']):
            users = db['studentattended'].find_one({"_id": Userdata["_id"]})
            easyattent, mediumattent, hardattent = users['Easy'] * 4, users['Medium'] * 7, users['Hard'] * 10
            per = f"{(users['score'] / (easyattent + mediumattent + hardattent)) * 100 :.2f}"
            print(per)
            up = db['studentattended'].find_one_and_update({"_id": Userdata['_id']}, {"$set": {"percent": per}}, return_document=True)
            return jsonify({"message": "Completed"});
        questionStructure = {
            "Questionobjid": str(QueGen['_id']),
            "Question": QueGen['Question'],
            "Distractors": QueGen['Distractors'],
        }
        return jsonify({"questionStructure": questionStructure})






if __name__ == '__main__':
    app.run()