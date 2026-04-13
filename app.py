from flask import Flask, request, jsonify, render_template
import time, os, smtplib, random

app = Flask(__name__)

attempts = {}

# 👉 УПРОЩЕННЫЕ “РЕАЛЬНЫЕ” БИЛЕТЫ (аналог экзамена)
QUESTIONS_BANK = {
    "ab": [
        {"q":"Перекрёсток без знаков — кто главный?", "img":"/static/1.png",
         "a":["слева","справа","главная дорога","пешеход"], "correct":1},

        {"q":"Можно ли обгон на пешеходном переходе?", "img":"/static/2.png",
         "a":["да","нет"], "correct":1},

        {"q":"Максимальная скорость в городе?", "img":"/static/3.png",
         "a":["60","80","90"], "correct":0}
    ],

    "cd": [
        {"q":"Грузовик на перекрёстке — кто уступает?", "img":"/static/4.png",
         "a":["легковые","грузовик","пешеход"], "correct":0},

        {"q":"Остановка на мосту разрешена?", "img":"/static/5.png",
         "a":["да","нет"], "correct":1}
    ]
}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/start", methods=["POST"])
def start():
    ip = request.remote_addr
    data = request.json
    cat = data["category"]

    if ip in attempts and time.time() - attempts[ip] < 3*60*60:
        return jsonify({"error":"Повтор через 3 часа"}), 403

    attempts[ip] = time.time()

    questions = random.sample(QUESTIONS_BANK[cat], len(QUESTIONS_BANK[cat]))

    return jsonify({"questions": questions})

@app.route("/finish", methods=["POST"])
def finish():
    data = request.json
    fio = data["fio"]
    cat = data["category"]
    answers = data["answers"]

    qs = QUESTIONS_BANK[cat]
    errors = 0
    details = []

    for i,q in enumerate(qs):
        ok = answers[i] == q["correct"]
        if not ok:
            errors += 1
        details.append(ok)

    result = "СДАЛ" if errors <= 2 else "НЕ СДАЛ"

    send_email(fio, cat, result, errors)

    return jsonify({"result":result, "details":details})

def send_email(fio,cat,result,errors):
    msg=f"""
ФИО:{fio}
Категория:{cat}
Результат:{result}
Ошибки:{errors}
"""

    server=smtplib.SMTP("smtp.gmail.com",587)
    server.starttls()
    server.login(os.getenv("EMAIL"),os.getenv("PASSWORD"))
    server.sendmail(os.getenv("EMAIL"),"Timkaxd@mail.ru",msg)
    server.quit()

if __name__=="__main__":
    app.run()
