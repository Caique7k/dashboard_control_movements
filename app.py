from flask import Flask, render_template
import psycopg2
from config import DB_CONFIG, SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

@app.route('/')
def home():
    return "Sistema de Controle de Movimentações da Fazenda 🚜"

if __name__ == '__main__':
    app.run(debug=True)