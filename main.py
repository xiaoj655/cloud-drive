import uvicorn
from dotenv import load_dotenv
import os

if __name__ == '__main__':
    load_dotenv()
    uvicorn.run('src:app', reload=True)