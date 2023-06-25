from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from flask import Flask, request, jsonify, redirect, Response
import json
import random
import os

# Connect to our local MongoDB
#client = MongoClient('mongodb://localhost:27017/')

mongodb_hostname = os.environ.get("MONGO_HOSTNAME","localhost")
client = MongoClient('mongodb://'+mongodb_hostname+':27017/')

# Choose InfoSys database
db = client['DigitalAirlines']
users = db['users']
flights = db['flights']
reservations = db['reservations']
# Initiate Flask App
app = Flask(__name__)

#auto insert admin to the database
admin = {'username': 'admin', 'password': '1', 'email': 'admin@email.com', 'first_name': 'John', 'last_name': 'Doe', 'birthdate': '23/03/1993', 'country': 'Greece', 'passport_number': 'V4595348', 'role': 'admin'}
existing_user = users.find_one({'username': 'admin'})
if not existing_user:
# Insert the new user
    users.insert_one(admin)#register to the app


isloggedin = False
isuser = False
username1 = "None"

#register to the app
@app.route("/register", methods=["POST"])
def register():
    #get data from user input 
    username = request.form.get("username")
    email = request.form.get("email")
    
    #find if there is already a user registered with either email or username that the user gave 
    existing_user = users.find_one({"$or": [{"email": email}, {"username": username}]})

    if existing_user: #if another user exists show message
        return Response("username or email already exists!",status=409,mimetype="application/json") #status 409 - Conflict

    # Collect user registration data
    user = {
        "username": username,
        "email": email,
        "first_name": request.form.get("first_name"),
        "last_name": request.form.get("last_name"),
        "password": request.form.get("password"),
        "birthdate": request.form.get("birthdate"),
        "country": request.form.get("country"),
        "passport_number": request.form.get("passport_number"),
        "role": "user"
    }

    #make user registration (add the user info in the users collection)
    users.insert_one(user)
    return Response("Succesfully registered!",status=201,mimetype="application/json") #status 201 - Created

#login to the app
@app.route("/login", methods=["POST"])
def login():
    global isloggedin #global variable to track if a user is logged in 
    global isuser #global variable to track the role of the logged in user
    global username1 #global variable to track the logged in users username
    
    if isloggedin: #if user is already loggged in (isloggedin = True) send message
        return Response("You are already logged in.", status=403, mimetype="application/json") #status 403 - Forbidden
    else:               
        #user input credentials
        email = request.form.get("email") 
        password = request.form.get("password")
        
        #find registered user with the credentials 
        user = users.find_one({"email": email, "password": password})
    
        if user: #if user exists
            isloggedin = True #set islogged in to true so now the program knows that the user is logged in 
            username1 = user["username"] #input the username to username1
            
            #check the role of the logged in user
            if user["role"] == "admin": #if admin
                isuser = False 
                return Response("Successfully logged in! Welcome admin.", status=200, mimetype="application/json") #status 200 - OK
            else: #if simple user
                isuser= True
                return Response("Successfully logged in! Welcome user.", status=200, mimetype="application/json") #status 200 - OK
        else:
            return Response("Invalid email or password.", status=401, mimetype="application/json") #status 401 - Unauthorized
               
#logout from the app
@app.route("/logout", methods=["GET"])
def logout():
    global isloggedin
    
    if isloggedin: #if user is already loggged in (isloggedin = True) send message
        isloggedin = False #set the global isloggedin to False
        return Response("You are logged out!", status=200, mimetype="application/json") #status 200 - OK
    else:
        return Response("You are not logged in!", status=401, mimetype="application/json") #status 401 - Unauthorized

#user interface (endpoints that only a user can access)

#search the existing flights in the database
@app.route('/searchflight', methods=['POST'])
def search_flight():        
    global isloggedin #global variable to track if a user is logged in 
    global isuser #global variable to track the role of the logged in user 
    
    if isloggedin: #if user is logged in continue
        departure_airport = request.form.get("departure_airport")
        arrival_airport = request.form.get("arrival_airport")
        date = request.form.get("date")
        all_flights = request.form.get("all_flights")
            
        results = []
        iterable = flights.find({})	
            
        #search in the whole flights collection            
        for flight in iterable:
            #if the all_flights var has elements then show all the registered flights in the system
            if all_flights:
                flight['_id'] = str(flight['_id'])
                results.append(flight)
            #if user gave input for only the airports then find flights according airports only 
            elif (departure_airport and arrival_airport) and (flight['departure_airport'] == departure_airport and flight['arrival_airport'] == arrival_airport):
                flight['_id'] = str(flight['_id'])
                results.append(flight)
            #if user gave data for all three inputs then find flights according to all three 
            elif (departure_airport and arrival_airport and date) and (flight['departure_airport'] == departure_airport and flight['arrival_airport'] == arrival_airport and flight['date'] == date):
                flight['_id'] = str(flight['_id'])
                results.append(flight)
            #if user gave input only for date then find flights according to this date 
            elif (date) and (flight['date'] == date):
                flight['_id'] = str(flight['_id'])
                results.append(flight)
                
    
        if results: #if results variable have values inside it then show them
            response = {'message': 'Flights found', 'data': results}
            return jsonify(response)
        else: #if results variable is empty the show No results found
            response = {'message': 'No flights found'}
            return jsonify(response)
    else:
        return Response("You must login first!", status=401, mimetype="application/json") #status 401 - Unauthorized  

#show flight details
@app.route('/getflightdetails', methods=['POST'])
def get_flight_details():
    global isloggedin #global variable to track if a user is logged in 
    global isuser #global variable to track the role of the logged in user
    
    if isloggedin: #if user is logged in continue
        isloggedin = True
        
        if isuser: #if logged in user has the role of a simple user continue 
            #get data from user input  
            flight_id = request.form.get('flight_id')
            #find the flight with the inputed id
            flight = flights.find_one({"flight_id": flight_id})
            
            if flight: #if flight id exists 
                flight = {'flight_id': flight["flight_id"],'departure_airport':flight["departure_airport"],'arrival_airport':flight["arrival_airport"], 'date':str(flight["date"]), 'economy_left':flight["economy_left"], 'economy_cost':flight["economy_cost"], 'business_left':flight["business_left"], 'business_cost':flight["business_cost"]}
                
                return jsonify(flight) #return flights details
            else: #if flight does not exist     
                return Response('There are no registered flights with this id.',status=404,mimetype='application/json') #status 401 - Not Found
        else:
            return Response("Only users can access this endpoint", status=401, mimetype="application/json") #status 401 - Unauthorized
    else:
        return Response("You must login first!", status=401, mimetype="application/json") #status 401 - Unauthorized
             
#reserve a ticket
@app.route('/ticketreservation', methods=['POST'])
def reserve_ticket():
    global isloggedin #global variable to track if a user is logged in 
    global isuser #global variable to track the role of the logged in user
    
    if isloggedin: #if user is logged in continue
        isloggedin = True
        
        if isuser: #if logged in user has the role of a simple user continue 
            #get data from user input
            flight_id = request.form.get('flight_id')
            first_name = request.form.get("first_name")
            last_name = request.form.get("last_name")
            passport_number = request.form.get("passport_number")
            birthdate = request.form.get("birthdate")
            email = request.form.get("email")
            ticket_class = request.form.get("ticket_class")
            
            #search in users collection with the data that user inputed
            user = users.find_one({"first_name": first_name, "last_name": last_name, "passport_number": passport_number, "birthdate": birthdate, "email": email})
            
            if not user: #if there is not found a user with this data 
                return Response("The personal info you entered are wrong.", status=400, mimetype="application/json") #status 400 - Bad Request
            
            # reserve a economy class ticket    
            if ticket_class == "economy":
                #search in flights collection for the flight with the id the user inputed
                flight = flights.find_one({"flight_id": flight_id})
                if flight: #if the flight id is found then continue
                    if int(flight["economy_left"]) >= 1: #see if there are economy tickets left
                        #give a random number between 0 and 99999999 for the ticket ID
                        ticketid = random.randint(0,99999999)
                        ticket_id = str(ticketid)
                        #search the reservations collection for this ticket_id
                        iterable = reservations.find_one({"ticket_id": ticket_id})
                        
                        #if the ticket_id is found then give another random number and loop until ticket_id is unique
                        while iterable:
                            ticketid = random.randint(0,99999999)
                            ticket_id = str(ticketid)
                            
                        #prepare reservation data in reservation variable
                        reservation = {
                            "first_name": first_name,
                            "last_name": last_name,
                            "birthdate": birthdate,
                            "email": email,
                            "passport_number": passport_number,
                            "ticket_class": ticket_class,
                            "ticket_id": ticket_id,
                            "flight_id": flight_id
                        }
                        #subtract one ticket from the ticket_left and economy_left
                        updated_ticket_left = int(flight["tickets_left"]) - 1
                        updated_economy_left = int(flight["economy_left"]) - 1
                        #insert a new reservation
                        reservations.insert_one(reservation)
                        #update ticket availability in the flight with the id that was inputed in the beggining
                        flights.update_one({"flight_id": flight_id}, {"$set": {"economy_left": str(updated_economy_left), "tickets_left": str(updated_ticket_left)}})

                        return Response("Reservation completed successfully! You have reserved an economy class ticket",status=200,mimetype="application/json") #status 200 - OK
                    else:
                        return Response("There are no economy tickets left for this flight!", status=409, mimetype="application/json") #status 409 - Conflict
                else:
                    return Response("There are no flights with this ID!", status=404, mimetype="application/json") #status 404 - Not Found
            #reserve a business class ticket
            elif ticket_class == "business":
                #search in flights collection for the flight with the id the user inputed
                flight = flights.find_one({"flight_id": flight_id})
                if flight:
                    if int(flight["business_left"]) >= 1: #see if there are business tickets left
                        #give a random number between 0 and 99999999 for the ticket ID
                        ticketid = random.randint(0,99999999)
                        ticket_id = str(ticketid)
                        #search the reservations collection for this ticket_id
                        iterable = reservations.find_one({"ticket_id": ticket_id})
                        
                        #if the ticket_id is found then give another random number and loop until ticket_id is unique
                        while iterable:
                            ticket_id = random.randint(0,99999999)
                        
                        #prepare reservation data in reservation variable             
                        reservation = {
                            "first_name": first_name,
                            "last_name": last_name,
                            "birthdate": birthdate,
                            "email": email,
                            "passport_number": passport_number,
                            "ticket_class": ticket_class,
                            "ticket_id": ticket_id,
                            "flight_id": flight_id
                        }
                        #subtract one ticket from the ticket_left and business_left
                        updated_ticket_left = int(flight["tickets_left"]) - 1
                        updated_business_left = int(flight["business_left"]) - 1
                        #insert a new reservation
                        reservations.insert_one(reservation)
                        #update ticket availability in the flight with the id that was inputed in the beggining
                        flights.update_one({"flight_id": flight_id}, {"$set": {"business_left": str(updated_business_left), "tickets_left": str(updated_ticket_left)}})

                        return Response("Reservation completed successfully! You have reserved a business class ticket",status=200,mimetype="application/json") #status 200 - OK
                        
                    else: #if there are no business tickets left
                        return Response("There are no business tickets left for this flight!", status=409, mimetype="application/json") #status 409 - Conflict
                else:
                    return Response("There are no flights with this ID!", status=404, mimetype="application/json") #status 404 - Not Found
            else:
                return Response("You entered a non available ticket class!", status=400, mimetype="application/json") #status 400 - Bad Request
        else:
            return Response("Only users can access this endpoint", status=401, mimetype="application/json") #status 401 - Unauthorized
    else:
        return Response("You must login first!", status=401, mimetype="application/json") #status 401 - Unauthorized
               
#show users reservations
@app.route('/showreservations', methods=['GET'])
def show_reservations():
    global isloggedin #global variable to track if a user is logged in 
    global isuser #global variable to track the role of the logged in user
    global username1 #global variable to track the logged in users username
    
    if isloggedin: #if user is logged in continue
        isloggedin = True
        
        if isuser: #if logged in user has the role of a simple user continue 
            #search in users collection for the personal info of the logged in user
            user = users.find_one({"username": username1}) 

            results = []
            #find the reservations that the logged in user has completed by the passport_number of the user
            iterable = reservations.find({"passport_number": user["passport_number"]})
            #store all reservations made by the logged in user in a variable
            for reservation in iterable:
                reservation["_id"] = str(reservation["_id"])
                results.append(reservation)
                    
            if results: #if variable is full show results 
                response = {'message': 'Results found', 'data': results}
                return jsonify(response)
            else: #if variable is empty show message 
                return Response("You have made no reservations yet!", status=404, mimetype="application/json") #status 404 - Not Found
        else:
            return Response("Only users can access this endpoint", status=401, mimetype="application/json") #status 401 - Unauthorized
    else:
        return Response("You must login first!", status=401, mimetype="application/json") #status 401 - Unauthorized
               
#show specific reservation's details
@app.route('/reservationdetails', methods=['POST'])
def show_reservation_details():
    global isloggedin #global variable to track if a user is logged in 
    global isuser #global variable to track the role of the logged in user
    
    if isloggedin: #if user is logged in continue
        isloggedin = True
        
        if isuser: #if logged in user has the role of a simple user continue
            #get data from user input
            ticket_id = request.form.get('ticket_id')
            #search in reservations collection to find a reservation with the ticket_id that the user inputed
            reservation = reservations.find_one({"ticket_id": ticket_id})
            
            if reservation: #if reservation is found
                #search in the flights collection for the flight with the same flight id as the reservations
                flight_id = reservation["flight_id"]
                flight = flights.find_one({"flight_id": flight_id})
                
                #combine results from reservations collection and flights collection
                result = {
                    'Personal Info': {
                        'first_name': reservation['first_name'],
                        'last_name': reservation['last_name'],
                        'birthdate': reservation['birthdate'],
                        'email': reservation['email'],
                        'passport_number': reservation['passport_number'],
                        'ticket_class': reservation['ticket_class']
                    },
                    'Flight Details': {
                        'date': flight['date'],
                        'departure_airport': flight['departure_airport'],
                        'arrival_airport': flight['arrival_airport']
                    }
                }
                
                return jsonify(result) #return results
            else:      
                return Response('There are no reservations with this ticket ID.',status=404, mimetype='application/json') #status 404 - Not Found
        else:
            return Response("Only users can access this endpoint", status=401, mimetype="application/json") #status 401 - Unauthorized
    else:
        return Response("You must login first!", status=401, mimetype="application/json") #status 401 - Unauthorized
        
#delete reservation
@app.route('/deletereservation', methods=['POST'])
def delete_reservation():
    global isloggedin #global variable to track if a user is logged in 
    global isuser #global variable to track the role of the logged in user
    
    if isloggedin: #if user is logged in continue
        isloggedin = True
        
        if isuser: #if logged in user has the role of a simple user continue
            #get data from user input
            ticket_id = request.form.get('ticket_id')
            #search in reservations collection to find a reservation with the ticket_id that the user inputed
            reservation = reservations.find_one({"ticket_id": ticket_id})
            
            if reservation: #if reservation is found
                #search in the flights collection for the flight with the same flight id as the reservations
                flight_id = reservation["flight_id"]
                flight = flights.find_one({"flight_id": flight_id})
                
                if reservation["ticket_class"] == "economy": #if the ticket is of class economy 
                    
                    #add one ticket to the availability of the flight
                    updated_ticket_left = int(flight["tickets_left"]) + 1 
                    updated_economy_left = int(flight["economy_left"]) + 1
                    #delete the reservation
                    reservations.delete_one(reservation)
                    #update the flight with the new ticket availability
                    flights.update_one({"flight_id": flight_id}, {"$set": {"economy_left": str(updated_economy_left), "tickets_left": str(updated_ticket_left)}})
                    
                    return Response("You successfully canceled your economy class ticket reservation!",status=200,mimetype="application/json") #status 200 - OK
                
                else: #if the ticket is of class business
                    
                    #add one ticket to the availability of the flight
                    updated_ticket_left = int(flight["tickets_left"]) + 1 
                    updated_business_left = int(flight["business_left"]) + 1
                    #delete the reservation
                    reservations.delete_one(reservation)
                    #update the flight with the new ticket availability
                    flights.update_one({"flight_id": flight_id}, {"$set": {"business_left": str(updated_business_left), "tickets_left": str(updated_ticket_left)}})
                    
                    return Response("You successfully canceled your business class ticket reservation!",status=200,mimetype="application/json") #status 200 - OK                   
            else:      
                return Response('There are no reservations with this ticket ID.',status=404, mimetype='application/json') #status 404 - Not Found
        else:
            return Response("Only users can access this endpoint", status=401, mimetype="application/json") #status 401 - Unauthorized
    else:
        return Response("You must login first!", status=401, mimetype="application/json") #status 401 - Unauthorized
        
#delete account
@app.route('/deleteaccount', methods=['GET'])
def delete_account():
    global isloggedin #global variable to track if a user is logged in 
    global isuser #global variable to track the role of the logged in user
    global username1 #global variable to track the logged in users username
    
    if isloggedin: #if user is logged in continue	
        
        if isuser: #if logged in user has the role of a simple user continue
            #find if there is already a user registered with either email or username that the user gave
            existing_user = users.find_one({"username": username1})
            
            if existing_user: #if user exists delete registration and show message
                users.delete_one(existing_user)
                isloggedin = False
                return Response("You have successfully deleted your account!",status=200, mimetype="application/json") #status 200 - OK  
        else:
            return Response("Only users can access this endpoint", status=401, mimetype="application/json") #status 401 - Unauthorized
    else:
        return Response("You must login first!", status=401, mimetype="application/json") #status 401 - Unauthorized

#admin interface (endpoints that only admin can access)

#create a flight
@app.route('/createflight', methods=['POST'])
def create_flight():
    global isloggedin #global variable to track if a user is logged in 
    global isuser #global variable to track the role of the logged in user
    
    if isloggedin: #if user is logged in continue
        isloggedin = True
        
        if not isuser: #if logged in user has the role of admin continue
            #get data from admin input
            departure_airport = request.form.get("departure_airport")
            arrival_airport = request.form.get("arrival_airport")
            date = request.form.get("date")
            economy_left = request.form.get("economy_left")
            economy_cost = request.form.get("economy_cost")
            business_left = request.form.get("business_left")
            business_cost = request.form.get("business_cost")
            #give a random number between 0 and 9999 for the flight ID
            flightid = random.randint(0,9999)
            
            flight_id = str(flightid)
            #search the reservations collection for this flight_id
            iterable = flights.find_one({"flight_id": flight_id})
                        
            #if the flight_id is found then give another random number and loop until flight_id is unique
            while iterable:
                flightid = random.randint(0,9999)        
                flight_id = str(flightid)
            
            economy_total = economy_left
            business_total = business_left
            tickets_total = str(int(economy_left) + int(business_left))
            tickets_left = tickets_total
            #add a new flight with the data that the admin inputed
            flights.insert_one({"flight_id": flight_id, "departure_airport": departure_airport, "arrival_airport": arrival_airport, "date": date, "tickets_total": tickets_total, "tickets_left": tickets_left, "economy_total": economy_total, "economy_left": economy_left, "economy_cost": economy_cost, "business_total": business_total, "business_left": business_left, "business_cost": business_cost})
            
            return Response("Flight successfully added!",status=200,mimetype="application/json") #status 200 - OK
                            
        else:
            return Response("Only admins can access this endpoint", status=401, mimetype="application/json") #status 401 - Unauthorized
    else:
        return Response("You must login first!", status=401, mimetype="application/json") #status 401 - Unauthorized

#update prices
@app.route('/updateprice', methods=['POST'])
def update_price():
    global isloggedin #global variable to track if a user is logged in 
    global isuser #global variable to track the role of the logged in user
    
    if isloggedin: #if user is logged in continue
        isloggedin = True
        
        if not isuser: #if logged in user has the role of admin continue
            #get data from admin input
            flight_id = request.form.get("flight_id")
            economy_cost = request.form.get("economy_cost")
            business_cost = request.form.get("business_cost")
            flight = flights.find_one({"flight_id": flight_id})
            
            if flight:
                if (business_cost and economy_cost):
                    flights.update_one({"flight_id": flight_id}, {"$set": {"economy_cost": economy_cost, "business_cost": business_cost}})
                    return Response("Economy and business tickets cost succesfully updated!",status=200,mimetype="application/json") #status 200 - OK
                elif (business_cost):
                    flights.update_one({"flight_id": flight_id}, {"$set": {"business_cost": business_cost}})
                    return Response("Business ticket cost succesfully updated!",status=200,mimetype="application/json") #status 200 - OK
                elif (economy_cost):
                    flights.update_one({"flight_id": flight_id}, {"$set": {"economy_cost": economy_cost}})
                    return Response("Economy ticket cost succesfully updated!",status=200,mimetype="application/json") #status 200 - OK
                else:
                    return Response("Please enter new prices first!",status=400,mimetype="application/json") #status 400 - Bad Request
            else:
                return Response('There are no flights with this ID.',status=404, mimetype='application/json') #status 404 - Not Found
        else:
            return Response("Only admins can access this endpoint", status=401, mimetype="application/json") #status 401 - Unauthorized
    else:
        return Response("You must login first!", status=401, mimetype="application/json") #status 401 - Unauthorized
        
#delete flight
@app.route('/deleteflight', methods=['POST'])
def delete_flight():        
    global isloggedin #global variable to track if a user is logged in 
    global isuser #global variable to track the role of the logged in user        
    
    if isloggedin: #if user is logged in continue
        if not isuser: #if logged in user has the role of admin continue        
            flight_id = request.form.get("flight_id")
            flight = flights.find_one({"flight_id": flight_id})
            
            if flight:
                reservation = reservations.find_one({"flight_id": flight_id})
                
                if not reservation:
                    flights.delete_one({"flight_id": flight_id})
                    return Response("Flight successfully deleted!",status=200,mimetype="application/json") #status 200 - OK
                else:
                    return Response('This flight has reservations so you can not delete it.',status=400, mimetype='application/json') #status 400 - Bad Request
            else:
                return Response('There are no flights with this ID.',status=404, mimetype='application/json') #status 404 - Not Found
        else:
            return Response("Only admins can access this endpoint", status=401, mimetype="application/json") #status 401 - Unauthorized        
    else:
        return Response("You must login first!", status=401, mimetype="application/json") #status 401 - Unauthorized        

#flight details
@app.route('/adminflightdetails', methods=['POST'])
def admin_flight_details():        
    global isloggedin #global variable to track if a user is logged in 
    global isuser #global variable to track the role of the logged in user 
    
    if isloggedin: #if user is logged in continue
        if not isuser: #if logged in user has the role of admin continue
            flight_id = request.form.get("flight_id")
            flight = flights.find_one({"flight_id": flight_id})
            
            if flight:
                reservations_flight = reservations.find({})
                reservation_data = []
                
                for reservation in reservations_flight:
                    if reservation["flight_id"] == flight_id:
                        reservation = {'first_name': reservation['first_name'], 'last_name': reservation['last_name'], 'ticket_class': reservation['ticket_class']}
                        reservation_data.append(reservation)
                
                result = {
                    'flight_id': flight["flight_id"],
                    'departure_airport':flight["departure_airport"],
                    'arrival_airport':flight["arrival_airport"],
                    'tickets_total': flight["tickets_total"], 
                    'tickets_by_class': {
                        'economy_total': flight["economy_total"],
                        'business_total': flight["business_total"]
                    },
                    'ticket_costs': {
                        'economy_cost':flight["economy_cost"],
                        'business_cost':flight["business_cost"],
                    },
                    'available_tickets': flight["tickets_left"],
                    'available_tickets_by_class': {
                        'economy_left':flight["economy_left"],
                        'business_left':flight["business_left"]
                    },
                    'reservations': reservation_data
                }
                
                return jsonify(result) #return flights details
            else:
                return Response('There are no flights with this ID.',status=404, mimetype='application/json') #status 404 - Not Found
        else:
            return Response("Only admins can access this endpoint", status=401, mimetype="application/json") #status 401 - Unauthorized
    else:
        return Response("You must login first!", status=401, mimetype="application/json") #status 401 - Unauthorized
    
# Run Flask App
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
