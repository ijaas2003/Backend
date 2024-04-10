from flask import Flask, jsonify, make_response, request
from flask_cors import CORS
from pymongo import MongoClient
import logging
import re
import datetime
import errno
from collections import Counter
from schema.schema import faculty_schema, student_schema
from Authendication import GeneratedToken
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
from flask import flash
import random
import numpy as np;
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

if 'faculty' not in db.list_collection_names():
    db.create_collection('faculty')










# ! Routing 
@app.route('/', methods=['GET'])
def example():
    return "Welcome"













@app.route('/StudentLogin', methods=['POST'])
def student_login():
    data = request.json
    username, email, question_id, course = str(data['username']), str(data['email']), str(data['queid']), str(data['Course'])
    data['exp'] = datetime.datetime.now() + datetime.timedelta(days=1)  
    if any([username ==" ",email =="",question_id=="",course==""]) :
        # print("Please Enter All fields")
        return jsonify({"Error":"Please Enter all fields"})
    if all([re.match(Email_Regex, email), re.match(Alpha_Regex, username)]) :
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







from flask import redirect, url_for

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
                    userdata = db['faculty'].find_one({"faculty_email":faculty_email})
                    if userdata is not None:
                        return jsonify({"error": "User already exists"})
                    
                    datas = {
                        "faculty_name":faculty_name,
                        "faculty_email":faculty_email,
                        "faculty_pass":faculty_pass,
                        "faculty_dept":faculty_dept,
                        "faculty_teach":faculty_taught,
                    }
                    res = db['faculty'].insert_one(datas)
                    if res.acknowledged:
                        datas["_id"] = str(datas['_id'])
                        response = make_response({"message": "Success"})
                        response.status_code = 201
                        return response
                        
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
    if any([faculty_email == "", faculty_pass == ""]):
        return jsonify({"error": "Enter all fields"})
    if re.match(Email_Regex, faculty_email):
        userdata = db['faculty'].find_one({"faculty_email": faculty_email})  
        # print(userdata)
        if userdata is not None:
            stored_pass = userdata.get('faculty_pass') 
            print(stored_pass)
            if stored_pass == faculty_pass:
                print("success")
                response = make_response({"message": "Success"})
                response.status_code = 201
                return response
            else:
                return jsonify({"error": "Incorrect password"})
        else:
            response=make_response({"error":"User Not Found "})
            return response
    else:
        return jsonify({"error": "Invalid email format"})








@app.route('/upload', methods=["POST"])
def upload_file():
    uploaded_file = request.files['file']
    File_path = os.path.join(current_dir, 'Pdf', uploaded_file.filename);
    uploaded_file.save(File_path);
    text = StartGenerate(uploaded_file.filename, "Data.txt");
    # print(text)
    if text:
        process = Start(text=text);
        print(process)
        return jsonify({"message": "success"})
    
    
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
    question_tokenizer = T5Tokenizer.from_pretrained('t5-large')
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
    for question, answer in questions:
        print("Question:", question)
        print("Answer:", answer)
        print("\n")
    return "yes"











if __name__ == '__main__':
    app.run()