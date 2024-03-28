import os;
current_Dir = os.getcwd();
def ForReadAndWrite(source_file, destination_file, Write_Content):
     current_directory = os.getcwd();
     parent_dir = os.path.dirname(current_directory);
     Read  = os.path.join(parent_dir, 'Data', source_file);
     Write = os.path.join(parent_dir, 'Data', destination_file);
     #print(Read, Write);
     with open(Write, "w", encoding="utf-8") as file:
          file.write(Write_Content);
     return "Finished";
     