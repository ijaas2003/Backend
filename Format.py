def Format(question, answer, que_diff, distractors, similarity, difficulty, QuestionId):
     json_format = {
		"Id": f"{question}",
          "Question": f"{question}",
          "Answer": f"{answer}",
          "Que_Difficulty": f"{que_diff}",
          "Distractors": [f"{distractors[0]}", f"{distractors[1]}", f"{distractors[2]}", f"{distractors[3]}"],
          "Similarity": similarity,
          "Difficulty": difficulty,
          "QuestionID": f"{QuestionId}"
	}
     return json_format;
     