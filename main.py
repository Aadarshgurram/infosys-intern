# Import required libraries for FastAPI and Twilio VoiceResponse
from fastapi import FastAPI, Request, Form
from fastapi.responses import Response
from twilio.twiml.voice_response import Gather, VoiceResponse
import json
import os
from dotenv import load_dotenv
from api import get_pnr_status, get_train_status, get_train_schedule

load_dotenv()
# Initialize FastAPI application
app = FastAPI()
sessions = {}
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
        "Welcome to IRCTC Railway Enquiry System. "
        "Press 1 for English. "
        "Press 2 for Hindi."
    )

    response.append(gather)
    response.say("No input received. Goodbye.")
    response.hangup()

    return Response(str(response), media_type="application/xml")


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
        url="https://unproving-nestor-metaphrastically.ngrok-free.dev/voice"
    )

    return {"call_sid": call.sid, "status": call.status}


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
        "hey Itachi, How can I help you today? "
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

        text = speech.lower()
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

        elif "book" in text:
            response.redirect("/ask-origin")

        else:
            response.say("Sorry I did not understand")
            response.redirect("/voice")
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

    data = get_pnr_status(pnr_number)

    if data:
        passenger = data["passengerList"][0]
        status = passenger["currentStatus"]

        response.say(
            f"PNR number {pnr_number}. Your ticket status is {status}"
        )
    else:
        response.say("Sorry, I could not fetch the PNR status right now.")

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

    origin = sessions.get(call_sid, {}).get("origin", "unknown")
    destination = sessions.get(call_sid, {}).get("destination", "unknown")

    response = VoiceResponse()

    gather = Gather(
    input="speech dtmf",
    action="/confirm-booking",
    language="en-IN"
)

    gather.say(
        f"You want to travel from {origin} to {destination} on {date}. "
        "Say yes or press 1 to confirm booking."
    )

    response.append(gather)

    return Response(str(response), media_type="application/xml")

@app.post("/confirm-booking")
async def confirm_booking(request: Request):

    form = await request.form()

    speech = form.get("SpeechResult")
    digits = form.get("Digits")

    response = VoiceResponse()

    if speech and "yes" in speech.lower():
        response.say("Your ticket has been successfully booked.")
        response.say("Your PNR number is 4567891234.")

    elif digits == "1":
        response.say("Your ticket has been successfully booked.")
        response.say("Your PNR number is 4567891234.")

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