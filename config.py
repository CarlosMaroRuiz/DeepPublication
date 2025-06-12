from dotenv import load_dotenv
import os #comunte estos pasos se realizan para crear la importaciones de variables entorno

load_dotenv()
class Config:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY") 


#Para realizar la importacion
config = Config()