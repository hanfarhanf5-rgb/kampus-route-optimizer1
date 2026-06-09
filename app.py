import os
from flask import Flask, render_template, jsonify, request, send_file
import math
import random
import time
import io
import csv

app = Flask(__name__)

gedung = {
    "Lab Komputer": [-6.3025, 106.8042],
    "Kelas A": [-6.3031, 106.8050],
    "Kelas B": [-6.3040, 106.8060],
    "Perpustakaan": [-6.3012, 106.8072],
    "Kantin": [-6.3008, 106.8035],
    "Rektorat": [-6.3050, 106.8085]
}


def distance(a, b):
    lat1, lon1 = gedung[a]
    lat2, lon2 = gedung[b]
    return math.sqrt((lat1-lat2)**2+(lon1-lon2)**2)


def total_distance(route):
    return round(sum(distance(route[i], route[i+1]) for i in range(len(route)-1))*10000, 2)

# Hill Climbing / SA / GA functions same as before
# ...


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/optimize", methods=["POST"])
def optimize():
    algo = request.json.get("algorithm", "hc")
    # call algorithm function, return steps + time + algo
    return jsonify({"steps": [], "time": 0.0, "algorithm": algo})


@app.route("/export", methods=["POST"])
def export():
    data = request.json.get("steps")
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(["Iterasi", "Route", "Distance"])
    for idx, step in enumerate(data):
        cw.writerow([idx+1, "->".join(step["route"]), step["distance"]])
    mem = io.BytesIO()
    mem.write(si.getvalue().encode("utf-8"))
    mem.seek(0)
    si.close()
    return send_file(mem, mimetype="text/csv", as_attachment=True, download_name="hasil_simulasi.csv")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
