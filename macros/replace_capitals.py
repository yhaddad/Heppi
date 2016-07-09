import glob, os

for filename in os.listdir("."):
    if 'Resolved' in filename:
        os.rename(filename, filename.replace('Resolved', 'LaMerde'))
