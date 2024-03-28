import os;
from Conversion import Conversion;
from Generate import WordTokenize;
from ForWrite import ForReadAndWrite;


print("This is Main Function");
file_name = "Tamil Nadu.pdf";
Des_file_name = "Data.txt";
Text = Conversion(file_name, Des_file_name);


if(Text):
    print("Converted to Text File... Completed");
    Extracted_text, Token = WordTokenize(Text);
    ForReadAndWrite(Des_file_name, "CleanedText.txt", Extracted_text);
    print("Data extracted and copied in Cleaned file");
else:
    print("Not Completed File Name is Wrong");

