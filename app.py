from fastapi import FastAPI
from fastapi.responses import FileResponse

from main import Model, RandomGame

model = Model()
game = RandomGame()
app = FastAPI()


@app.get("/")
async def get_ui():
    return FileResponse("index.html")


@app.get("/styles.css")
async def get_styles():
    return FileResponse("styles.css")


@app.get("/script.js")
async def get_script():
    return FileResponse("script.js")


@app.get("/play")
async def play():
    return game.play()


@app.get("/evaluate")
async def evaluate(player, program):
    return game.evaluate(player, program)


@app.post("/reset")
async def reset():
    model.reset()


@app.post("/add_datum")
async def add_datum(datum):
    model.add_datum(datum)


@app.post("/train_model")
async def train_model(epochs=500, learning_rate=0.005):
    model.train_model(epochs, learning_rate)


@app.get("/predict_move")
async def predict_move(last_player_move, last_program_move, last_result):
    return model.predict_move(last_player_move, last_program_move, last_result)
