# Import required libraries for FastAPI and Twilio VoiceResponse
from fastapi import FastAPI, Request, Form
from fastapi.responses import Response
from twilio.twiml.voice_response import Gather, VoiceResponse
import json
import os
import random
from dotenv import load_dotenv
from api import get_pnr_status, get_train_status, get_train_schedule

load_dotenv()
# Initialize FastAPI application
app = FastAPI()
sessions = {}
bookings = {}
# Root endpoint - returns server status
@app.get("/")
async def root():
    """Health check endpoint to verify server is running."""
    return {"message": "Server Running"}    


# Initial voice endpoint - greets user and prompts language selection
@app.api_route("/voice", methods=["GET", "POST"])
async def voice():
    """
    Entry point for incoming calls. 
    Presents welcome message and language selection (English/Hindi).
    """
    response = VoiceResponse()

    # Create gather object to collect 1 digit input for language selection
    gather = Gather(
        num_digits=1,
        action="/language",
        method="POST"
    )

    gather.say(
        "Welcome to IRCTC Enquiry System. "
        "Press 1 for English. "
        "Press 2 for Hindi."
    )

    response.append(gather)
    response.say("No input received. Please try again.")
    response.redirect("/voice")

    return Response(str(response), media_type="application/xml")

BOOKING_FILE = "bookings.json"

def load_bookings():
    if os.path.exists(BOOKING_FILE):
        try:
            with open(BOOKING_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_bookings(data):
    with open(BOOKING_FILE, "w") as f:
        json.dump(data, f, indent=4)

bookings = load_bookings()

# Helper function to retrieve train timing information from JSON file
def get_train_timing(train_no):
    """
    Fetch departure and arrival times for a given train number from irctc.json.
    Returns timing details or 'not found' message.
    """
    with open(r"C:\Users\aadar\OneDrive\画像\infosys\ivr-middle_ware\irctc.json") as f:
        data = json.load(f)

    if train_no in data:
        train = data[train_no]
        return f"Train departs at {train['departure']} and arrives at {train['arrival']}."
    return "Train not found."

# Endpoint to process simulated text input and respond with voice
@app.post("/process")
async def process(
    simulated_text: str = Form(None)
):
    """
    Process simulated text input, perform basic intent detection,
    and return appropriate voice response.
    """
    user_text = simulated_text.lower()

    # Basic Intent Detection - match keywords to determine user intent
    if "pnr" in user_text:
        result = get_pnr_status("PNR123")
    elif "train" in user_text:
        result = get_train_timing("12345")
    else:
        result = "Sorry, I did not understand your request."

    # Create and send voice response
    response = VoiceResponse()
    response.say(result)
    response.hangup()

    return Response(content=str(response), media_type="application/xml")

# Import Twilio client for making outbound calls
from twilio.rest import Client

# Twilio credentials and phone number configuration
ACCOUNT_SID = os.getenv('ACCOUNT_SID')
AUTH_TOKEN = os.getenv('AUTH_TOKEN')
TWILIO_NUMBER = os.getenv('TWILIO_NUMBER')  # US Twilio phone number

# Initialize Twilio client
client = Client(ACCOUNT_SID, AUTH_TOKEN)

# Endpoint to trigger outbound calls
@app.get("/trigger-call")
async def trigger_call():
    """
    Initiate an outbound call from Twilio to the specified Indian number.
    Returns call SID and status.
    """
    call = client.calls.create(
        to="+919490957383",  # Recipient's Indian phone number
        from_=TWILIO_NUMBER,
        url="https://ivr-app.onrender.com/voice"
    )

    return {"status": "calling..."}


# Language selection endpoint - handles digit 1 or 2 input
@app.api_route("/language", methods=["GET", "POST"])
async def language(request: Request):
    """
    Process language selection input.
    Digit 1 -> English (proceeds to main menu)
    Digit 2 -> Hindi (under development)
    """
    form_data = await request.form()
    digit = form_data.get("Digits")

    response = VoiceResponse()

    if digit == "1":
        # English selected - display main menu options
        gather = Gather(
        input="speech dtmf",
        num_digits=1,
        action="/process-intent",
        language="en-IN",
        speechTimeout="auto",
        method="POST",
        hints="pnr status,train status,train schedule,book ticket"

    )
        gather.say(
        "hey Itachi, How can I help you today?"
)
        response.append(gather)
    elif digit == "2":
        # Hindi selected - notify not available
        response.say("Hindi option is under development.")
        response.hangup()
    else:
        # Invalid selection - redirect to voice
        response.say("Invalid selection.")
        response.redirect("/voice")

    return Response(str(response), media_type="application/xml")

# Main menu endpoint - handles user's service selection
# @app.api_route("/main-menu", methods=["GET", "POST"])
# async def main_menu(request: Request):
#     """
#     Process main menu selection and route to appropriate service.
#     Options: PNR status, train status, schedule, booking info, cancellation policy.
#     """
#     form_data = await request.form()
#     digit = form_data.get("Digits")

#     response = VoiceResponse()

#     if digit == "1":
#         # Option 1: PNR Status - collect 10 digit PNR number
#         gather = Gather(
#             num_digits=10,
#             action="/pnr",
#             method="POST"
#         )
#         gather.say("Please enter your 10 digit PNR number.")
#         response.append(gather)

#     elif digit == "2":
#         # Option 2: Train Running Status - collect 5 digit train number
#         gather = Gather(
#             num_digits=5,
#             action="/train-status",
#             method="POST"
#         )
#         gather.say("Please enter your 5 digit train number.")
#         response.append(gather)

#     elif digit == "3":
#         # Option 3: Train Schedule - collect 5 digit train number
#         gather = Gather(
#             num_digits=5,
#             action="/train-schedule",
#             method="POST"
#         )
#         gather.say("Please enter your 5 digit train number.")
#         response.append(gather)

#     elif digit == "4":
#         # Option 4: Ticket Booking Information
#         response.say(
#             "Tickets can be booked through the IRCTC website or mobile application. "
#             "Booking opens 120 days before departure."
#         )
#         response.redirect("/repeat-menu")

#     elif digit == "5":
#         # Option 5: Cancellation Policy
#         response.say(
#             "Cancellation charges depend on timing. "
#             "If cancelled more than 48 hours before departure, minimal charges apply."
#         )
#         response.redirect("/repeat-menu")

#     elif digit == "9":
#         # Option 9: Repeat menu - redirect to voice (start over)
#         response.redirect("/voice")

#     elif digit == "0":
#         # Option 0: Exit call
#         response.say("Thank you for calling IRCTC. Goodbye.")
#         response.hangup()

#     else:
#         # Invalid selection - redirect to start
#         response.say("Invalid option selected.")
#         response.redirect("/voice")

#     return Response(str(response), media_type="application/xml")

# # PNR status endpoint - provides ticket information
# @app.api_route("/pnr", methods=["GET", "POST"])
# async def pnr(request: Request):

#     form_data = await request.form()
#     pnr_number = form_data.get("Digits")

#     response = VoiceResponse()

#     response.say(
#         f"PNR number {pnr_number}. "
#         "Your ticket is confirmed. Coach S 3. Seat 45."
#     )

#     gather = Gather(
#         input="speech dtmf",
#         action="/process-intent",
#         language="en-IN",
#         speechTimeout="auto"
#     )

#     gather.say("Is there anything else I can help you with?")

#     response.append(gather)

#     return Response(str(response), media_type="application/xml")

# # Train status endpoint - provides real-time train running information
# @app.api_route("/train-status", methods=["GET", "POST"])
# async def train_status(request: Request):
#     """
#     Retrieve and announce train running status and expected arrival time.
#     """
#     form_data = await request.form()
#     train_number = form_data.get("Digits")

#     response = VoiceResponse()

#     response.say(
#         f"Train number {train_number} is running on time. "
#         "Expected arrival at 4 PM."
#     )
#     gather = Gather(
#     input="speech dtmf",
#     action="/process-intent",
#     language="en-IN",
#     speechTimeout="auto"
# )


#     gather.say(
#         "Is there anything else I can help you with?"
#     )

#     response.append(gather)

#     return Response(str(response), media_type="application/xml")

# # Train schedule endpoint - provides departure and arrival information
# @app.api_route("/train-schedule", methods=["GET", "POST"])
# async def train_schedule(request: Request):
#     """
#     Retrieve and announce train schedule including departure and arrival stations/times.
#     """
#     form_data = await request.form()
#     train_number = form_data.get("Digits")

#     response = VoiceResponse()

#     response.say(
#         f"Train number {train_number} departs from Chennai at 10 AM "
#         "and arrives in Bangalore at 4 PM."
#     )
#     gather = Gather(
#     input="speech dtmf",
#     action="/process-intent",
#     language="en-IN",
#     speechTimeout="auto"
# )

#     gather.say(
#         "Is there anything else I can help you with?"
#     )

#     response.append(gather)

#     return Response(str(response), media_type="application/xml")


# # Repeat menu endpoint - allows user to return to main menu
# @app.api_route("/repeat-menu", methods=["GET", "POST"])
# async def repeat_menu():
#     """
#     Display main menu again after completing a service.
#     Allows user to select another service or exit.
#     """
#     response = VoiceResponse()

#     # Recreate main menu gather
#     gather = Gather(
#         num_digits=1,
#         action="/main-menu",
#         method="POST"
#     )

#     gather.say(
#         "Press 1 for PNR Status. "
#         "Press 2 for Train Running Status. "
#         "Press 3 for Train Schedule. "
#         "Press 4 for Ticket Booking Information. "
#         "Press 5 for Cancellation Policy. "
#         "Press 9 to repeat this menu. "
#         "Press 0 to exit."
#     )

#     response.append(gather)
#     response.hangup()

#     return Response(str(response), media_type="application/xml")


@app.post("/process-intent")
async def process_intent(request: Request):

    form = await request.form()

    speech = form.get("SpeechResult")
    digits = form.get("Digits")

    response = VoiceResponse()

    if speech:

        text = (speech or "").lower()
        if "no" in text or "thank you" in text or "thanks" in text or "exit" in text or "goodbye" in text or "nothing else" in text or "no thanks" in text:
            response.say("Thank you for calling IRCTC. Have a nice day.")
            response.hangup()
            return Response(str(response), media_type="application/xml")

        if "pnr" in text:
            response.redirect("/ask-pnr")

        elif "train" in text and ("status" in text or "running" in text or "live" in text):
            response.redirect("/ask-train")

        elif "schedule" in text or "timing" in text:
            response.redirect("/ask-schedule")

        elif "book" in text or "ticket booking" in text:
            response.redirect("/ask-origin")
            
        elif "cancel" in text or "ticket cancel" in text:
            response.redirect("/ask-cancel-pnr")

        else:
            gather = Gather(
                input="speech dtmf",
                action="/process-intent",
                language="en-IN",
                speechTimeout="auto"
            )

            gather.say("Sorry, I did not understand. Please say PNR status, train status, booking, or cancellation.")

            response.append(gather)
            return Response(str(response), media_type="application/xml")

    elif digits:

        if digits == "1":
            response.redirect("/ask-pnr")

        elif digits == "2":
            response.redirect("/ask-train")

        elif digits == "3":
            response.redirect("/ask-schedule")

        elif digits == "4":
            response.redirect("/ask-origin")

        elif digits == "9":
            response.redirect("/voice")

        elif digits == "0":
            response.say("Thank you for calling IRCTC. Goodbye.")
            response.hangup()

        else:
            response.say("Invalid option")
            response.redirect("/voice")

        return Response(str(response), media_type="application/xml")


@app.post("/ask-pnr")
async def pnr(request: Request):

    form_data = await request.form()
    pnr_number = form_data.get("Digits")
    if not pnr_number:
        speech = form_data.get("SpeechResult")
        if speech:
            pnr_number = "".join(filter(str.isdigit, speech))

    response = VoiceResponse()

    data = bookings.get(pnr_number)

    if data:
        status = data["status"]
        response.say(f"PNR number {pnr_number}. Your ticket is {status}")
    else:
        response.say("PNR not found.")
    gather = Gather(
        input="speech dtmf",
        action="/process-intent",
        language="en-IN",
        speechTimeout="auto"
    )

    gather.say("Is there anything else I can help you with?")
    response.append(gather)

    return Response(str(response), media_type="application/xml")

@app.post("/ask-origin")
async def ask_origin():

    response = VoiceResponse()

    gather = Gather(
    input="speech",
    action="/process-origin",
    language="en-IN",
    speechTimeout="auto"
)

    gather.say("From which station are you travelling?")

    response.append(gather)

    return Response(str(response), media_type="application/xml")

@app.post("/process-origin")
async def process_origin(request: Request):

    form = await request.form()

    origin = form.get("SpeechResult")
    call_sid = form.get("CallSid")

    response = VoiceResponse()

    # Handle silence / no speech detected
    if not origin:
        gather = Gather(
            input="speech",
            action="/process-origin",
            language="en-IN",
            speechTimeout="auto"
        )

        gather.say("I did not hear anything. Please say the station name again.")

        response.append(gather)

        return Response(str(response), media_type="application/xml")

    # Ensure session exists
    if call_sid not in sessions:
        sessions[call_sid] = {}

    sessions[call_sid]["origin"] = origin

    gather = Gather(
        input="speech",
        action="/process-destination",
        language="en-IN",
        speechTimeout="auto"
    )

    gather.say("Where do you want to travel?")

    response.append(gather)

    return Response(str(response), media_type="application/xml")

@app.post("/process-destination")
async def process_destination(request: Request):

    form = await request.form()

    destination = form.get("SpeechResult")
    call_sid = form.get("CallSid")

    # ensure session exists
    if call_sid not in sessions:
        sessions[call_sid] = {}

    sessions[call_sid]["destination"] = destination

    response = VoiceResponse()

    gather = Gather(
    input="speech",
    action="/process-date",
    language="en-IN",
    speechTimeout="auto"
)

    gather.say("What date do you want to travel?")

    response.append(gather)

    return Response(str(response), media_type="application/xml")

@app.post("/process-date")
async def process_date(request: Request):

    form = await request.form()

    date = form.get("SpeechResult")
    call_sid = form.get("CallSid")

    if call_sid not in sessions:
        sessions[call_sid] = {}

    sessions[call_sid]["date"] = date

    response = VoiceResponse()

    gather = Gather(
        input="speech dtmf",
        action="/process-class",
        language="en-IN",
        speechTimeout="auto"
    )

    gather.say(
        "Which class would you like to travel? "
        "You can say sleeper, AC 3 tier, or AC 2 tier."
    )

    response.append(gather)

    return Response(str(response), media_type="application/xml")

@app.post("/confirm-booking")
async def confirm_booking(request: Request):

    form = await request.form()

    speech = form.get("SpeechResult")
    digits = form.get("Digits")
    call_sid = form.get("CallSid")

    response = VoiceResponse()

    confirm = False

    text = (speech or "").lower().strip()

    if any(word in text for word in ["yes", "yeah", "yup", "confirm", "correct"]):
        confirm = True
    elif digits == "1":
        confirm = True

    if confirm:
        data = sessions.get(call_sid, {})

        origin = data.get("origin")
        destination = data.get("destination")
        date = data.get("date")
        travel_class = data.get("class")

        import random
        pnr = str(random.randint(1000000000, 9999999999))

        bookings[pnr] = {
            "origin": origin,
            "destination": destination,
            "date": date,
            "class": travel_class,
            "status": "Booked"
        }
        save_bookings(bookings)
        response.say("Your ticket has been successfully booked.")
        response.say(f"Your PNR number is {pnr}.")
        response.say("For full ticket details and confirmation, please visit IRCTC website or app.")

    else:
        response.say("Booking cancelled.")

    response.hangup()

    return Response(str(response), media_type="application/xml")
@app.post("/ask-train")
async def ask_train():

    response = VoiceResponse()

    gather = Gather(
        input="speech dtmf",
        num_digits=5,
        action="/train-status",
        method="POST"
    )

    gather.say("Please say or enter your five digit train number")

    response.append(gather)

    return Response(str(response), media_type="application/xml")

@app.post("/train-status")
async def train_status(request: Request):
    form_data = await request.form()
    # print("FULL TWILIO FORM:", form_data)
    train_number = form_data.get("Digits")
    if not train_number:
        speech = form_data.get("SpeechResult")
        if speech:
            train_number = "".join(filter(str.isdigit, speech))
    print("TRAIN NUMBER:", train_number)
    response = VoiceResponse()
    data = get_train_status(train_number)
    if data:
        station = data["current_station"]
        delay = data["delay"]
        response.say(
            f"Train number {train_number} is currently at {station} "
            f"and running {delay} minutes late."
        )
    else:
        response.say("Unable to fetch train running status right now.")
    gather = Gather(
        input="speech dtmf",
        action="/process-intent",
        language="en-IN",
        speechTimeout="auto"
    )
    gather.say("Anything else I can help you with?")
    response.append(gather)
    return Response(str(response), media_type="application/xml")

@app.post("/ask-schedule")
async def ask_schedule():

    response = VoiceResponse()

    gather = Gather(
        input="speech dtmf",
        num_digits=5,
        action="/train-schedule"
    )

    gather.say("Please say or enter the train number")

    response.append(gather)

    return Response(str(response), media_type="application/xml")

@app.post("/train-schedule")
async def train_schedule(request: Request):

    form_data = await request.form()
    train_number = form_data.get("Digits")
    if not train_number:
        speech = form_data.get("SpeechResult")
        if speech:
            train_number = "".join(filter(str.isdigit, speech))
    response = VoiceResponse()

    data = get_train_schedule(train_number)

    if data:
        source = data["source"]
        destination = data["destination"]

        response.say(
            f"Train {train_number} starts from {source} and ends at {destination}"
        )
    else:
        response.say("Unable to fetch train schedule.")

    gather = Gather(
        input="speech dtmf",
        action="/process-intent",
        language="en-IN",
        speechTimeout="auto"
    )

    gather.say("Is there anything else I can help you with?")
    response.append(gather)

    return Response(str(response), media_type="application/xml")

@app.post("/process-class")
async def process_class(request: Request):

    form = await request.form()

    travel_class = form.get("SpeechResult")
    call_sid = form.get("CallSid")

    if call_sid not in sessions:
        sessions[call_sid] = {}

    sessions[call_sid]["class"] = travel_class

    origin = sessions[call_sid].get("origin")
    destination = sessions[call_sid].get("destination")
    date = sessions[call_sid].get("date")

    response = VoiceResponse()

    gather = Gather(
    input="speech dtmf",
    action="/confirm-booking",
    language="en-IN",
    speechTimeout="auto",
    timeout=5
)

    gather.say(
        f"You want to travel from {origin} to {destination} on {date} "
        f"in {travel_class} class. "
        "Say yes or press 1 to confirm booking."
    )

    response.append(gather)

    return Response(str(response), media_type="application/xml")

@app.post("/ask-cancel-pnr")
async def ask_cancel_pnr():

    response = VoiceResponse()

    gather = Gather(
        input="speech dtmf",
        action="/cancel-ticket",
        language="en-IN",
        speechTimeout="auto"
    )

    gather.say("Please say or enter your PNR number to cancel your ticket")

    response.append(gather)

    return Response(str(response), media_type="application/xml")

@app.post("/cancel-ticket")
async def cancel_ticket(request: Request):

    form = await request.form()

    pnr = form.get("Digits")

    if not pnr:
        speech = form.get("SpeechResult")
        if speech:
            pnr = "".join(filter(str.isdigit, speech))

    response = VoiceResponse()

    if pnr in bookings:
        bookings[pnr]["status"] = "Cancelled"

        # ✅ THIS IS THE IMPORTANT LINE
        save_bookings(bookings)

        response.say(f"Your ticket with PNR {pnr} has been cancelled successfully.")
    else:
        response.say("Invalid PNR number.")

    response.hangup()

    return Response(str(response), media_type="application/xml")