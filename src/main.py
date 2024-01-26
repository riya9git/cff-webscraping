from datetime import datetime 

import apm
import rec1
from util import process_city

if __name__ == "__main__":
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    for city in apm.cities:
        process_city(city, apm, timestamp)

    for city in rec1.cities:
        process_city(city, rec1, timestamp)
