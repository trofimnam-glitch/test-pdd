from flask import Flask, request, jsonify
import time
import smtplib
import os

app = Flask(__name__)
@app.route("/")
def home():
    return """
    <h1>Тест ПДД</h1>
    <p>Система работает</p>
    """
attempts = {}

QUESTIONS = {
    "ab": [
        {"q": "Кто имеет приоритет?", "a": ["A", "B"], "correct": 0},
        {"q": "Можно ли обгонять?", "a": ["Да", "Нет"], "correct": 1}
    ],
    "cd": [
        {"q": "Разрешена ли остановка?", "a": ["Да", "Нет"], "correct": 0}
    ]
}

@app.route("/start", methods=["POST"])
def start():
    data = request.json
    fio = data["fio"]
    category = data["category"]

    ip = request.remote_addr
    now = time.time()

    if ip in attempts and now - attempts[ip] < 3 * 60 * 60:
        return jsonify({"error": "Повтор через 3 часа"}), 403

    attempts[ip] = now

    return jsonify({"questions": QUESTIONS[category]})


@app.route("/finish", methods=["POST"])
def finish():
    data = request.json

    fio = data["fio"]
    category = data["category"]
    answers = data["answers"]

    questions = QUESTIONS[category]

    errors = 0

    for i, q in enumerate(questions):
        if answers[i] != q["correct"]:
            errors += 1

    result = "СДАЛ" if errors <= 2 else "НЕ СДАЛ"

    send_email(fio, category, result, errors)

    return jsonify({"result": result, "errors": errors})


def send_email(fio, category, result, errors):
    message = f"""
ФИО: {fio}
Категория: {category}
Результат: {result}
Ошибки: {errors}
"""

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(os.getenv("EMAIL"), os.getenv("PASSWORD"))
    server.sendmail(os.getenv("EMAIL"), "Timkaxd@mail.ru", message)
    server.quit()


app.run(host="0.0.0.0", port=10000)
