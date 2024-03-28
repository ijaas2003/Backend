from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

def WordTokenize(text):
     words = word_tokenize(text)
     stop_words = set(stopwords.words('english'))
     filtered_words = [word for word in words if word.lower() not in stop_words]
     cleaned_text = ' '.join(filtered_words);
     return cleaned_text, words;
