from flask import Flask, current_app, request

app = Flask(__name__)

def validate_data(data: dict):
    if isinstance(data, dict) and all([isinstance(v, str) for v in data.values()]) and "from" in data and "message" in data:
        return data, 200

    return {"error": True, "message": "Invalid message content"}, 403


@app.route("/messages", methods=["POST"])
def vote_story():
    data = request.json

    data, status_code = validate_data(data)

    if status_code == 200:
        #print update and display message board
        print(data)

    return data, 200

if __name__ == "__main__":
    app.config['TESTING'] = True
    app.config['DEBUG'] = True
    app.run(debug=True, host="0.0.0.0", port=5000)