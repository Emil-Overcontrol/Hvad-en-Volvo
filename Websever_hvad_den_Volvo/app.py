from flask import Flask, jsonify, render_template

if __package__:
    from .car_data import VOLVO_MODELS
    from .database import get_car_models, initialize_database
else:
    from car_data import VOLVO_MODELS
    from database import get_car_models, initialize_database


app = Flask(__name__, static_folder="Static")
initialize_database()


@app.route("/")
def index():
    return render_template("Index.html")


@app.route("/wiki")
def wiki():
    return render_template("Wiki.html", models=get_car_models())

@app.route("/game")
def game():
    return render_template("Game.html", models=get_car_models())

@app.route("/api/data", methods=["GET"])
def get_data():
    return jsonify({"cars": get_car_models()})


@app.route("/api/cars", methods=["GET"])
def get_cars():
    return jsonify({"cars": get_car_models()})


@app.route("/api/cars/<model_name>", methods=["GET"])
def get_car(model_name):
    cars = get_car_models(model_name)
    if not cars:
        return jsonify({"error": "Car model not found"}), 404
    return jsonify(cars[0])


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
