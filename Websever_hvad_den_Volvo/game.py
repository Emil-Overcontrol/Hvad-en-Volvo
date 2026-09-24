if __package__:
    from .car_data import VOLVO_MODELS
    from .database import get_car_models, initialize_database
else:
    from car_data import VOLVO_MODELS
    from database import get_car_models, initialize_database


