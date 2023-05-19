import requests as re
import spacy
from spacy.language import Language
from spacy_langdetect import LanguageDetector
import pandas as pd


langs = pd.read_csv("lang_codes.csv")
three_char_codes = langs["alpha3-b"]
two_char_codes = langs["alpha2"]

def get_lang_detector(nlp, name):
    return LanguageDetector()

nlp = spacy.load("en_core_web_sm")
Language.factory("language_detector", func=get_lang_detector)
nlp.add_pipe('language_detector', last=True)

punctuation = list(",./!@#$%^&*()-+[]'")

# cleans request from MARC
def is_not_punctuation(char):
    return char not in punctuation

# Replace with tool once Data API key arrives
def get_title(record_num):
    r = re.get("https://catalog.hathitrust.org/api/volumes/full/recordnumber/{}.json".format(record_num))
    bib = r.json()
    title = list(bib["records"][record_num]["titles"][0])
    return ''.join(list(filter(is_not_punctuation, title)))
    
# From toy project
# returns 3 char
def get_language(record_num):
    r = re.get("https://quod.lib.umich.edu/cgi/o/oai/oai?verb=GetRecord&metadataPrefix=oai_dc&identifier=oai:quod.lib.umich.edu:MIU01-{}".format(record_num))
    return r.text.split("<dc:language>")[1].partition('<')[0]

# returns 2 char
def get_language_prediction(record_num):
    title = get_title(record_num)
    doc = nlp(title)
    return doc._.language

def get_other_code(lang_code):
    code_size = len(lang_code)
    if code_size == 2:
        return three_char_codes.iloc[(two_char_codes == lang_code).idxmax()]
    else:
        return two_char_codes.iloc[(three_char_codes == lang_code).idxmax()]

# returns true if the predicted language is different from the bibliography
def compare_langs(record_num : str) -> bool:
    return get_language(record_num) == get_other_code(get_language_prediction(record_num))



from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)

@app.route('/',methods=('GET', 'POST'))
def index():
    return render_template('create.html')

@app.route('/create',methods = ['POST', 'GET'])
def login():
   if request.method == 'POST':
      id = request.form['hathitrust-id']
      return redirect(url_for('success',name = id))
   else:
      user = request.args.get('nm')
      return redirect(url_for('success',name = id))


@app.route('/success/<name>')
def success(name):
   return get_language(id)

