import os;



def StartGenerates(file_name):
    from Conversion import Conversion;
    print("This is Main Function");
    Des_file_name = "Data.txt";
    Text = Conversion(file_name, Des_file_name);
    if Text:
        return "Success"
    else:
        return "Not Success"


StartGenerates("Tamil Nadu1.pdf")

    # if(Text):
    #     print("Converted to Text File... Completed");
    #     Extracted_text, Token = WordTokenize(Text);
    #     ForReadAndWrite(Des_file_name, "CleanedText.txt", Extracted_text);
    #     print("Data extracted and copied in Cleaned file");
    # else:
    #     print("Not Completed File Name is Wrong");

