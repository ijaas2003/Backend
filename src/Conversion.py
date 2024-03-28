import os
from PyPDF2 import PdfReader
def Conversion(file_name, save_file_name):
	current_directory = os.getcwd();
	parent_dir = os.path.dirname(current_directory);
	file_path = os.path.join(parent_dir, 'Pdf', file_name);
	desc_file_path = os.path.join(parent_dir, 'Data', save_file_name)
	extracted_text = "";
	with open(file_path, "rb") as pdf_file:
		pdf_reader = PdfReader(pdf_file);
		x = 1;
		for page in pdf_reader.pages:
			extracted_text += page.extract_text();
			x += 1
	with open(desc_file_path, "w", encoding="utf-8") as text_file:
		text_file.write(extracted_text)
	return extracted_text;