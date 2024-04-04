import os
from PyPDF2 import PdfReader
def Conversion(file_name, save_file_name):
	current_directory = os.getcwd();
	parent_dir = os.path.dirname(current_directory);
	file_path = os.path.join(current_directory, 'Pdf', file_name);
	desc_file_path = os.path.join(current_directory, 'Data', save_file_name)
	print(current_directory, file_path, desc_file_path)
	extracted_text = "";
	with open(file_path, "rb") as pdf_file:
		pdf_reader = PdfReader(pdf_file);
		for page in pdf_reader.pages:
			extracted_text += page.extract_text();
	with open(desc_file_path, "w", encoding="utf-8") as text_file:
		text_file.write(extracted_text)
	return "Success" if extracted_text else "Not Success";