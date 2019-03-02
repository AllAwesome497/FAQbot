from flask import Flask
from threading import Thread
import random

app = Flask('')

@app.route('/')
def home():
    return "I'm alive"

def run():
  app.run(host='0.0.0.0',port=random.randint(2000,9000))

def keep_alive():
    #print('>keep_alive')
    t = Thread(target=run)
    t.start()