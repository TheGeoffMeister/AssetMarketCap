from glob import glob
import random
import pickle

file_extension = "png"

search_pickle = glob("*")
files = glob("*"+file_extension)

if "saved_films.pkl" not in search_pickle:
    with open('saved_films.pkl', 'wb') as f:
        pickle.dump(files, f)

else:
    with open('saved_films.pkl', 'rb') as f:
        files = pickle.load(f)

random_index = random.randrange(len(files))
random_file = "Random film is" + str(files[random_index])

print(random_file)

del files[random_index]

with open('saved_films.pkl', 'wb') as f:
    pickle.dump(files, f)
    
    
if len(files) == 0:
    files = glob("*"+file_extension)
    with open('saved_films.pkl', 'wb') as f:
        pickle.dump(files, f)
    


    