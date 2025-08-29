import os 

folder_path = "Pipleline 1/Bug Tests"
entries = os.scandir(folder_path)
for entry in entries:
    in_entries = os.scandir(folder_path + "/" + entry.name)
    for in_entry in in_entries:
        print(in_entry.name)