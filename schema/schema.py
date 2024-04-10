faculty_schema = {
   "faculty_name": str,
   "faculty_email": str,
   "faculty_dept": str,
   "faculty_taught": str,
   "faculty_pass": str,
   "faculty_confirm_pass": str
}

student_schema = {
   "name": str,
   "email": str,
   "course": str,
   "QueId": str
}

Questions = {
   "Question": str,
   "Answer": str,
   "Distractors": [str]
}