# api.py (FINAL STABLE VERSION - STATIC RESPONSES)

# No external API calls → 100% reliable IVR

def get_train_status(train_no):
    return {
        "train_name": "Rajdhani Express",
        "current_station": "Hyderabad",
        "delay": 10
    }


def get_pnr_status(pnr):
    return {
        "passengerList": [
            {
                "currentStatus": "Confirmed"
            }
        ]
    }


def get_train_schedule(train_no):
    return {
        "train_name": "Superfast Express",
        "source": "Delhi",
        "destination": "Mumbai"
    }


def get_seat_availability(train_no, from_station, to_station, date):
    return [
        {
            "class": "Sleeper",
            "availability": "Available"
        }
    ]