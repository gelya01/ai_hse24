from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import List
import pickle
import pandas as pd
from io import StringIO
from fastapi.responses import RedirectResponse

app = FastAPI()

with open("model.pkl", "rb") as file:
    data = pickle.load(file)
    model = data["model"]
    preprocessor = data["preprocessor"]


class Item(BaseModel):
    name: str
    year: int
    km_driven: int
    fuel: str
    seller_type: str
    transmission: str
    owner: str
    mileage: float
    engine: int
    max_power: float
    torque: float
    seats: str


class Items(BaseModel):
    objects: List[Item]


@app.get("/", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse("/docs")


@app.post("/predict_item")
def predict_item(item: Item) -> float:
    """
    Получение предсказания для одного объекта
    """
    df = pd.DataFrame([item.dict()])
    preprocessed_data = preprocessor.transform(df)
    return model.predict(preprocessed_data)


@app.post("/predict_items")
def predict_items(items: List[Item]) -> List[float]:
    """
    Получение предсказаний для списка объектов
    """
    df = pd.DataFrame([item.dict() for item in items])
    preprocessed_data = preprocessor.transform(df)
    return model.predict(preprocessed_data)


@app.post("/predict_csv")
def predict_csv(file: UploadFile = File(...)):
    """
    Получение предсказаний для объектов из csv
    """
    contents = file.file.read().decode("utf-8")
    df = pd.read_csv(StringIO(contents))
    predictions = []
    # обработка csv
    for _, row in df.iterrows():
        item = Item(
            name=row["name"],
            year=int(row["year"]),
            km_driven=int(row["km_driven"]),
            fuel=row["fuel"],
            seller_type=row["seller_type"],
            transmission=row["transmission"],
            owner=row["owner"],
            mileage=float(row["mileage"]),
            engine=int(row["engine"]),
            max_power=float(row["max_power"]),
            torque=float(row["torque"]),
            seats=str(row["seats"]),
        )
        # Предобработка и предсказание
        preprocessed_data = preprocessor.transform(pd.DataFrame([item.dict()]))
        prediction = model.predict(preprocessed_data)[0]
        predictions.append(prediction)
    # Добавляем предсказания в DataFrame
    df["predicted_price"] = predictions
    # Сохраняем результат в CSV
    output = StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return {"filename": "predictions.csv", "file": output.getvalue()}
