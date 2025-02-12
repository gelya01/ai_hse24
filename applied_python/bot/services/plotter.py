import matplotlib.pyplot as plt
import io


def generate_weekly_progress_plot(
    dates, water_data, calorie_data, burned_calories_data
):
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))

    formatted_dates = [d[-2:] + "." + d[5:7] for d in dates]
    # график воды
    ax[0].plot(
        formatted_dates,
        water_data,
        marker="o",
        linestyle="-",
        color="blue",
        label="Выпито (мл)",
    )
    ax[0].set_title("Прогресс по воде за неделю")
    ax[0].set_xlabel("Дата")
    ax[0].set_ylabel("Мл")
    ax[0].legend()
    ax[0].grid()

    # график калорий
    ax[1].plot(
        formatted_dates,
        calorie_data,
        marker="o",
        linestyle="-",
        color="green",
        label="Потреблено (ккал)",
    )
    ax[1].plot(
        formatted_dates,
        burned_calories_data,
        marker="s",
        linestyle="--",
        color="red",
        label="Сожжено (ккал)",
    )
    ax[1].set_title("Прогресс по калориям за неделю")
    ax[1].set_xlabel("Дата")
    ax[1].set_ylabel("ккал")
    ax[1].legend()
    ax[1].grid()

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()

    return buf
