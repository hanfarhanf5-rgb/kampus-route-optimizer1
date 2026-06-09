import os
from flask import Flask, render_template, jsonify, request, send_file
import math
import random
import io
import csv

app = Flask(__name__)

# Koordinat gedung kampus
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
    return math.sqrt((lat1-lat2)**2 + (lon1-lon2)**2)


def total_distance(route):
    return round(sum(distance(route[i], route[i+1]) for i in range(len(route)-1))*10000, 2)

# Hill Climbing


def hill_climbing():
    route = list(gedung.keys())
    random.shuffle(route)
    best = route[:]
    best_dist = total_distance(best)
    steps = []
    for _ in range(3):  # dummy step untuk animasi
        steps.append(
            {"route": best[:], "distance": best_dist, "local_opt": False})
    improved = True
    while improved:
        improved = False
        for i in range(len(route)-1):
            for j in range(i+1, len(route)):
                neighbor = best[:]
                neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
                d = total_distance(neighbor)
                if d < best_dist:
                    best = neighbor[:]
                    best_dist = d
                    improved = True
                    steps.append(
                        {"route": best[:], "distance": best_dist, "local_opt": False})
        if not improved:
            steps.append(
                {"route": best[:], "distance": best_dist, "local_opt": True})
    return steps

# Simulated Annealing


def simulated_annealing():
    route = list(gedung.keys())
    random.shuffle(route)
    current = route[:]
    current_dist = total_distance(current)
    steps = []
    for _ in range(3):  # dummy step
        steps.append(
            {"route": current[:], "distance": current_dist, "local_opt": False})
    T = 1.0
    T_min = 0.001
    alpha = 0.9
    while T > T_min:
        i, j = random.sample(range(len(route)), 2)
        new_route = current[:]
        new_route[i], new_route[j] = new_route[j], new_route[i]
        d = total_distance(new_route)
        if d < current_dist or random.random() < math.exp(-(d-current_dist)/T):
            current = new_route[:]
            current_dist = d
        steps.append(
            {"route": current[:], "distance": current_dist, "local_opt": False})
        T *= alpha
    steps[-1]["local_opt"] = True
    return steps

# Genetic Algorithm


def genetic_algorithm(pop_size=6, generations=5):
    genes = list(gedung.keys())
    population = [random.sample(genes, len(genes)) for _ in range(pop_size)]
    steps = []
    for g in range(generations):
        population.sort(key=lambda x: total_distance(x))
        best = population[0]
        steps.append(
            {"route": best[:], "distance": total_distance(best), "local_opt": False})
        new_pop = [best[:]]
        while len(new_pop) < pop_size:
            parents = random.sample(population[:3], 2)
            cut = random.randint(1, len(genes)-2)
            child = parents[0][:cut] + \
                [x for x in parents[1] if x not in parents[0][:cut]]
            if random.random() < 0.2:
                a, b = random.sample(range(len(child)), 2)
                child[a], child[b] = child[b], child[a]
            new_pop.append(child)
        population = new_pop
    steps[-1]["local_opt"] = True
    return steps


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/optimize", methods=["POST"])
def optimize():
    algo = request.json.get("algorithm", "hc")
    if algo == "hc":
        steps = hill_climbing()
    elif algo == "sa":
        steps = simulated_annealing()
    else:
        steps = genetic_algorithm()
    return jsonify(steps)


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
    app.run(host="0.0.0.0", port=port, debug=True)
