from datetime import datetime
from geopy.distance import geodesic
def calculate_distance(user_location,spot_location):
    return round(geodesic(user_location,spot_location).km,2)


current_time = datetime.now().strftime("%H:%M")

def is_open_spot(row):
    opening_time = row["opening_time"]
    closing_time = row["closing_time"]
    if opening_time <= current_time < closing_time:
        return "Open"
    else:
        return "Close"
    