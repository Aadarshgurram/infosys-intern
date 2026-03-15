import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("RAPID_API_KEY")
headers = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "irctc1.p.rapidapi.com"
}

def get_train_status(train_no):
    url = "https://irctc1.p.rapidapi.com/api/v1/liveTrainStatus"
    params = {"trainNo": train_no}
    response = requests.get(url, headers=headers, params=params)
    print("STATUS CODE:", response.status_code)
    data = response.json()
    if response.status_code == 200 and data.get("status"):
        train = data["data"]
        result = {
            "train_name": train["train_name"],
            "current_station": train["current_station"],
            "delay": train["delay"],
            "next_station": train["next_stoppage_info"]["next_stoppage"],
            "eta": train["eta"]
        }
        return result
    return None

def get_pnr_status(pnr):
    url = "https://irctc1.p.rapidapi.com/api/v3/getPNRStatus"
    params = {"pnrNumber": pnr}
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    if response.status_code == 200 and "data" in data:
        pnr_data = data["data"]
        result = {
            "train_name": pnr_data["train_name"],
            "train_number": pnr_data["train_number"],
            "from": pnr_data["boarding_point"],
            "to": pnr_data["destination"],
            "status": pnr_data["passengersList"][0]["currentStatus"]
        }
        return result
    return None

def get_train_schedule(train_no):
    url = "https://irctc1.p.rapidapi.com/api/v1/getTrainSchedule"
    params = {"trainNo": train_no}
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    if response.status_code == 200 and "data" in data:
        schedule = data["data"]
        result = {
            "train_name": schedule["train_name"],
            "total_stations": len(schedule["route"]),
            "source": schedule["route"][0]["station_name"],
            "destination": schedule["route"][-1]["station_name"]
        }
        return result
    return None

def get_seat_availability(train_no, from_station, to_station, date):
    url = "https://irctc1.p.rapidapi.com/api/v1/checkSeatAvailability"
    params = {
        "trainNo": train_no,
        "fromStationCode": from_station,
        "toStationCode": to_station,
        "date": date
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    if data["status"]:
        return data["data"]
    return None

# print(API_KEY)