import random
from bson.objectid import ObjectId
def RandomQue(Questions):
     return random.choice(Questions);


def ChooseCrtQues(db, easy, medium, hard, duration, id, answer):
     ids = ObjectId(id)
     print(ids)
     current_que = db['questions'].find_one({"_id": ids})
     print(current_que)
     correct_ans = str(current_que['Answer'])
     currentDiffvalue = current_que['QuestionDiff']
     currentDiff = current_que['Que_Difficulty']
     if correct_ans.lower() == answer:
          if currentDiff == "easy":
               getQues = random.choice(medium)
               print(getQues, currentDiff)
               return getQues
          elif currentDiff == "medium":
               getQues = random.choice(hard)
               print(getQues)
               return getQues
          elif currentDiff == "hard":
               #QueGen = random.choice(hard);
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