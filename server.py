from flask import Flask, request, jsonify, render_template_string
import random
import string

app = Flask(__name__)
rooms = {}

PAGE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>تحدي الأصدقاء</title>
<style>
body {
    background: #101827;
    color: white;
    font-family: Arial;
    text-align: center;
    padding: 20px;
}
.box {
    background: #1e293b;
    padding: 20px;
    margin: 20px auto;
    border-radius: 15px;
    max-width: 420px;
}
input, button {
    padding: 12px;
    margin: 7px;
    border-radius: 8px;
    border: none;
    font-size: 16px;
}
button {
    background: #16a34a;
    color: white;
    cursor: pointer;
}
input { max-width: 85%; }
#game { display: none; }
</style>
</head>
<body>
<h1>🎮 تحدي الأصدقاء</h1>
<p>أنشئ غرفة والعب مع صديقك!</p>

<div class="box" id="home">
    <h3>إنشاء غرفة جديدة</h3>
    <input id="creator" placeholder="اكتب اسمك">
    <br>
    <button onclick="createRoom()">إنشاء غرفة</button>

    <hr>
    <h3>الانضمام إلى غرفة</h3>
    <input id="joinname" placeholder="اكتب اسمك">
    <br>
    <input id="roomcode" placeholder="رمز الغرفة">
    <br>
    <button onclick="joinRoom()">دخول الغرفة</button>
    <p id="message"></p>
</div>

<div class="box" id="game">
    <h2>رمز الغرفة: <span id="code"></span></h2>
    <p>أرسل الرمز لصديقك حتى ينضم إليك.</p>
    <h3>اللاعبون</h3>
    <p id="players"></p>
    <hr>
    <h3>🎯 خمن الرقم من 1 إلى 10</h3>
    <p>لديك 5 محاولات.</p>
    <input id="guess" type="number" min="1" max="10" placeholder="اكتب رقمًا">
    <br>
    <button onclick="makeGuess()">تخمين</button>
    <p id="result"></p>
    <button onclick="resetGame()">لعب من جديد</button>
</div>

<script>
let myRoom = "";
let myName = "";

async function send(url, data) {
    const r = await fetch(url, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
    });
    return await r.json();
}

async function createRoom() {
    myName = document.getElementById("creator").value.trim();
    if (!myName) {
        alert("اكتب اسمك أولاً");
        return;
    }
    const d = await send("/create", {name: myName});
    if (!d.ok) {
        alert(d.message);
        return;
    }
    enterGame(d.code);
}

async function joinRoom() {
    myName = document.getElementById("joinname").value.trim();
    myRoom = document.getElementById("roomcode").value.trim().toUpperCase();

    if (!myName || !myRoom) {
        alert("اكتب اسمك ورمز الغرفة");
        return;
    }

    const d = await send("/join", {
        name: myName,
        code: myRoom
    });

    if (!d.ok) {
        alert(d.message);
        return;
    }
    enterGame(myRoom);
}

function enterGame(code) {
    myRoom = code;
    document.getElementById("home").style.display = "none";
    document.getElementById("game").style.display = "block";
    document.getElementById("code").textContent = code;
    refresh();
}

async function refresh() {
    if (!myRoom) return;
    const r = await fetch("/status?code=" +
