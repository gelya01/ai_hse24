from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from sklearn.linear_model import LinearRegression
import uvicorn
from fastapi.responses import RedirectResponse
import time

app = FastAPI()

# хранилище моделей
models = {}


# все необходимы классы
class ModelConfig(BaseModel):
    id: str
    ml_model_type: str
    hyperparameters: Dict[str, Optional[bool]]


class FitRequest(BaseModel):
    X: List[List[float]]
    y: List[float]
    config: ModelConfig


class FitResponse(BaseModel):
    message: str


class LoadRequest(BaseModel):
    id: str


class LoadResponse(BaseModel):
    message: str


class PredictRequest(BaseModel):
    id: str
    X: List[List[float]]


class PredictionResponse(BaseModel):
    id: str
    predictions: List[float]


class ModelListResponse(BaseModel):
    models: List[Dict[str, str]]


class RemoveResponse(BaseModel):
    message: str


# ручки по тз
@app.post("/fit", response_model=FitResponse)
def fit_model(request: FitRequest):
    X = request.X
    y = request.y
    config = request.config

    # проверяем, есть ли модель с таким id
    if config.id in models:
        raise HTTPException(
            status_code=400, detail=f"Model with ID '{config.id}' already exists"
        )

    # преобразуем строки в числа (если возможно)
    try:
        X = [[float(value) for value in row] for row in X]
        y = [float(value) for value in y]
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="X and y must contain only numbers or numeric strings",
        )

    # проверяем соответствие длины X и y
    if len(X) != len(y):
        raise HTTPException(status_code=400, detail="Длины X и y не совпадают!")

    # проверяем тип модели
    if config.ml_model_type != "linear":
        raise HTTPException(
            status_code=400, detail="Поддерживается только 'linear' для обучения"
        )

    # обучаем модель
    model = LinearRegression(**config.hyperparameters)
    model.fit(X, y)
    time.sleep(60)  # на всякий случай, т.к. такое тз

    models[config.id] = model

    return {"message": f"Model '{config.id}' trained and saved"}


@app.post("/load", response_model=LoadResponse)
def load_model(request: LoadRequest):
    model_id = request.id
    if model_id not in models:
        raise HTTPException(
            status_code=404, detail=f"Model with ID '{model_id}' not found"
        )

    return {"message": f"Model '{model_id}' loaded"}


@app.post("/predict", response_model=PredictionResponse)
def predict_model(request: PredictRequest):
    model_id = request.id
    X = request.X

    if model_id not in models:
        raise HTTPException(
            status_code=404, detail=f"Model with ID '{model_id}' not found"
        )

    try:
        X = [[float(value) for value in row] for row in X]
    except ValueError:
        raise HTTPException(
            status_code=400, detail="X must contain only numbers or numeric strings"
        )

    model = models[model_id]
    predictions = model.predict(X).tolist()

    return {"id": model_id, "predictions": predictions}


@app.get("/list_models", response_model=ModelListResponse)
def list_models():
    return {"models": [{"id": model_id} for model_id in models.keys()]}


@app.delete("/remove_all", response_model=RemoveResponse)
def remove_all_models():
    models.clear()
    return {"message": "All models have been removed"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
