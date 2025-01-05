import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import aiohttp
import asyncio
import json
import plotly.express as px

def process_func(df, city_name):
    df = df[df['city'] == city_name].copy()
    df['mean_roll_30'] = df.rolling(window=30, on='timestamp', closed='left')['temperature'].mean()
    df['std_roll_30'] = df.rolling(window=30, on='timestamp', closed='left')['temperature'].std()
    df['mean_roll_30'] = df['mean_roll_30'].bfill()
    df['std_roll_30'] = df['std_roll_30'].bfill()
    df['upper_bound'] = df['mean_roll_30'] + 2 * df['std_roll_30']
    df['lower_bound'] = df['mean_roll_30'] - 2 * df['std_roll_30']
    anomalies = df[(df['temperature'] > df['upper_bound']) | (df['temperature'] < df['lower_bound'])]
    seasonal_stats = df.groupby('season')['temperature'].agg(['mean', 'std', 'min', 'max']).reset_index()
    return {"city": city_name, "anomalies": anomalies, "seasonal_stats": seasonal_stats, "processed_data": df}

async def get_current_temperature_async(city, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather"
    params = {'q': city, 'appid': api_key, 'units': 'metric'}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data['main']['temp']
            elif response.status == 401:
                return "Invalid API key. Please see https://openweathermap.org/faq#error401 for more info."
            else:
                return f"Error: {response.status}"

def check_temperature(temp, season, seasonal_stats):
    stats = seasonal_stats[seasonal_stats['season'] == season]
    mean = stats['mean'].iloc[0]
    std = stats['std'].iloc[0]
    lower_bound = mean - 2 * std
    upper_bound = mean + 2 * std
    if lower_bound <= temp <= upper_bound:
        return f"Температура {temp} в градусах Цельсия нормальная для сезона {season}."
    return f"Температура {temp} в градусах Цельсия аномальная для сезона {season}!"

st.title("Приложение для анализа температур")

uploaded_file = st.file_uploader("Загрузите файл с историческими данными в формате csv", type=["csv"])
if uploaded_file:
    data = pd.read_csv(uploaded_file, parse_dates=['timestamp'])
    st.success("Данные успешно загружены!")
    city_name = st.selectbox("Выберите город", data['city'].unique())
    result = process_func(data, city_name)
    anomalies = result["anomalies"]
    seasonal_stats = result["seasonal_stats"]
    processed_data = result["processed_data"]

    st.subheader(f"Описательная статистика для города {city_name}")
    st.dataframe(processed_data['temperature'].describe())

    st.subheader("Временной ряд температур с аномалиями")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(processed_data['timestamp'], processed_data['temperature'], label="Температура", color="blue")
    ax.scatter(anomalies['timestamp'], anomalies['temperature'], color="red", label="Аномалии", zorder=2)
    ax.legend()
    ax.set_title(f"Температуры и аномалии для {city_name}")
    ax.set_xlabel("Дата")
    ax.set_ylabel("Температура в цельсии")
    st.pyplot(fig)

    st.subheader("Сезонный профиль")
    st.dataframe(seasonal_stats)

    st.subheader("Получение текущей температуры через OpenWeatherMap API")
    api_key = st.text_input("Введите ваш API-ключ OpenWeatherMap", type="password")

    if api_key:
        current_season = st.selectbox("Выберите текущий сезон", seasonal_stats['season'].unique())
        if st.button("Получить текущую температуру"):
            with st.spinner("Получение текущей температуры..."):
                temp = asyncio.run(get_current_temperature_async(city_name, api_key))
                if isinstance(temp, str):
                    st.error(temp)
                else:
                    result = check_temperature(temp, current_season, seasonal_stats)
                    st.success(result)
    else:
        st.warning("Введите API-ключ, чтобы получить текущую температуру.")

    st.subheader("Дополнительные возможности")
    st.subheader("Сравнение городов")
    selected_cities = st.multiselect("Выберите города для сравнения", data['city'].unique())
    if selected_cities:
        comparison_stats = []
        for city in selected_cities:
            city_stats = process_func(data, city)['seasonal_stats']
            city_stats['city'] = city
            comparison_stats.append(city_stats)
        comparison_stats = pd.concat(comparison_stats)
        fig = px.line(
            comparison_stats,
            x='season',
            y='mean',
            color='city',
            labels={'season': 'Сезон', 'mean': 'Средняя температура в Цельсиях', 'city': 'Город'},
            title="Сравнение средних температур между городами",
            markers=True
        )
        fig.update_layout(legend_title="Города", template="plotly_white")
        st.plotly_chart(fig)
