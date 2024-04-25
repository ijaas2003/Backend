import random
from bson.objectid import ObjectId
def RandomQue(medium):
     return random.choice(medium);


def ChooseCrtQues(user, db, easy, medium, hard, duration, id, answer, score):
     MarkEasy, MarkMedium, MarkHard = 4, 7, 10;
     print(user)
     ids = ObjectId(id)
     # print(ids)
     current_que = db['questions'].find_one({"_id": ids})
     print(current_que)
     correct_ans = str(current_que['Answer'])
     currentDiffvalue = current_que['QuestionDiff']
     currentDiff = current_que['Que_Difficulty']
     if currentDiff == "easy":
          updateScore = db['studentattended'].find_one_and_update({"_id": user['_id']},{"$inc": {"Easy": 1}}, return_document=True)
     if currentDiff == "medium":
          updateScore = db['studentattended'].find_one_and_update({"_id": user['_id']},{"$inc": {"Medium": 1}}, return_document=True)
     if currentDiff == "hard":
          updateScore = db['studentattended'].find_one_and_update({"_id": user['_id']},{"$inc": {"Hard": 1}}, return_document=True)
     if correct_ans.lower() == answer:
          if currentDiff == "easy":
               getQues = random.choice(medium)
               updateScore = db['studentattended'].find_one_and_update({"_id": user['_id']},{"$inc": {"score": MarkEasy}}, return_document=True)
               print(updateScore)
               print(getQues, currentDiff)
               return getQues
          elif currentDiff == "medium":
               getQues = random.choice(hard)
               updateScore = db['studentattended'].find_one_and_update({"_id": user['_id']},{"$inc": {"score": MarkMedium}}, return_document=True)
               print(updateScore)
               print(getQues)
               return getQues
          elif currentDiff == "hard":
               #QueGen = random.choice(hard);
               updateScore = db['studentattended'].find_one_and_update({"_id": user['_id']},{"$inc": {"score": MarkHard}}, return_document=True)
               print(updateScore)
               for que in hard:
                    if que['QuestionDiff'] > currentDiffvalue:
                         print(que['_id'], que['QuestionDiff']);
                         return que
               return random.choice(hard);
     elif currentDiff == "easy":
          filtered_easy = [ques for ques in easy if ques['QuestionDiff'] < currentDiffvalue]
          if filtered_easy:
               random_question = random.choice(filtered_easy)
               print("Random Question:", random_question)
               return random_question
          else:
               QueGen = random.choice(easy)
               print(QueGen)
               return QueGen
     elif currentDiff == "medium":
          QueGen = random.choice(easy)
          return QueGen
     elif currentDiff == "hard":
          QueGen = random.choice(medium)
          return QueGen