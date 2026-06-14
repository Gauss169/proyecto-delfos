import os
from dotenv import load_dotenv

load_dotenv()

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET = os.getenv("BINANCE_SECRET")

TRADING_CONFIG = {
    'symbol': 'SOLUSDC',
    'target_time': '19:28',
    'check_interval': 2,
    'stop_loss_threshold': 0.9,
    'take_profit_threshold': 1.02,
    'fee_margin': 0.995,
    'timeout': 15
}

MODEL_CONFIG = {
    'model_path': 'models/gb_low_model.pkl',
    'columns_path': 'models/gb_low_columns.pkl',
    'threshold_path': 'models/umbral_gb_low_columns.pkl',
    'prediction_period': 370,
    'prediction_hour': 10
}

RACHAS = [1, 3, 7, 14, 30, 90, 180, 360]
