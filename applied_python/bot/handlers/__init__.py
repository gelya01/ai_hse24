from .start import router as start_router
from .profile import router as profile_router
from .food import router as food_router
from .water import router as water_router

# from .exercise import router as exercise_router
# from .stats import router as stats_router
# from .progress import router as progress_router
# from .photo import router as photo_router
# from .recommend import router as recommend_router

all_routers = [
    start_router,
    profile_router,
    # food_router,
    # exercise_router,
    # stats_router,
    # progress_router,
    # photo_router,
    # recommend_router,
]
