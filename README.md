# YpoxreotikiErgasia23_e20019_Gavrielatos_Evangelos

# Εισαγωγή
Η εργασία αυτή υλοποιεί μια εφαρμογή Flask που χρησιμοποιεί τη βιβλιοθήκη PyMongo για να συνδεθεί σε ένα τοπικό MongoDB και να εκτελέσεις λειτουργίες βάσης δεδομένων. Επιτρέπει σε χρήστες να δημιουργούν λογαριασμούς να κάνουν κρατήσεις 
πτήσεων, να αναζητούν πτήσεις σε ένα σύστημα αεροπορικών εισητηρίων να κάνουν κρατήσεις αεροπορικών εισητηρίων και αρκετά άλλα που θα παρουσιαστούν αναλυτικά στη συνέχεια.

# Ανάλυση σύνδεσης
Αρχικά συνδέουμε την εφαρμογή με την MongoDB βάση δεδομένων μέσω του MongoClient. Η διεύθυνση του MongoDB server παίρνεται από τη μεταβλητή περιβάλλοντος mongoHostName.
```
hostname = os.environ.get('mongoHostName')
client = MongoClient(hostname, 27017)
```
Αυτό γίνεται για να τρέχει το πρόγραμμα μέσω του docker και όχι από ένα απλό localhost.
******************************************************************************************************************************************************************************************************************************
Στη συνέχεια ορίζονται οι συλλογές της βάσης δεδομένων που θα χρησιμοποιηθούν για την αποθήκευση πληροφοριών χρηστών, πτήσεων και κρατήσεων.
```
db = client['DigitalAirlines']
users = db['users']
flights = db['flights']
reservations = db['reservations']
```
******************************************************************************************************************************************************************************************************************************
Και τέλος δημιουργούμαι μια νέα Flask εφαρμογή 
```
app = Flask(__name__)
```
******************************************************************************************************************************************************************************************************************************
Οι global μεταβλητές 
```
isloggedin = False
isuser = False
username1 = "None"
```
χρησιμοποιούνται αργότερα στο πρόγραμμα για να ελέγχουμε αν ο χρήστης είναι συνδεδεμένος στην εφαρμογή, τι ρόλο έχει και ποιό είναι το username του αντίστοιχα. 

# Λειτουργίες Συστήματος

__@app.route("/register", methods=["POST"])__

Σε αυτό το endpoint αναπτύσσεται μια ενέργεια εγγραφής στην εφαρμογή. 

Οι πληροφορίες που ο χρήστης παρέχει συλλέγονται από το αίτημα (request) και αποθηκεύονται στις μεταβλητές username και email.Γίνεται έλεγχος για να διαπιστωθεί εάν υπάρχει ήδη χρήστης με ίδιο username ή το ίδιο email στη βάση δεδομένων. 

Αυτό γίνεται αναζητώντας έναν υπάρχοντα χρήστη με τη χρήση της μέθοδου find_one() στη συλλογή (collection) "users" και χρησιμοποιώντας τον τελεστή $or για να ελέγξει εάν υπάρχει είτε ίδιο email είτε ίδιο όνομα χρήστη.

Εάν υπάρχει ήδη ένας χρήστης με τις ίδιες πληροφορίες, επιστρέφεται ένα μήνυμα λάθους στη μορφή ενός αντικειμένου Response με κωδικό κατάστασης 409 (Conflict). 

Εάν δεν υπάρχει ο χρήστης, δημιουργείται ένα αντικείμενο με τις πληροφορίες που έδωσε ο χρήστης. Οι πληροφορίες αποθηκεύονται σε ένα λεξικό με τα πεδία "username", "email", "first_name", "last_name", "password", 
"birthdate", "country", "passport_number" και "role". Στο πεδίο "role" αποθηκεύεται αυτόματα η ιδιότητα του "user" καθώς με βάση την εκφώνηση μόνο users μπορούν να κάνουν register.

Το αντικείμενο του χρήστη προστίθεται στη συλλογή "users" με τη χρήση της μεθόδου insert_one().

Τέλος επιστρέφεται ένα αντικείμενο Response με κωδικό κατάστασης 201 (Created) για να υποδείξει ότι η εγγραφή ολοκληρώθηκε με επιτυχία.
![image](https://github.com/VaggelisGavrielatos/YpoxreotikiErgasia23_e20019_Gavrielatos_Evangelos/assets/132483480/908d3501-657f-4409-9fb5-e31517c8a21a)

******************************************************************************************************************************************************************************************************************************
__@app.route("/login", methods=["POST"])__

Οι public μεταβλητές isloggedin, isuser και username1 χρησιμοποιούνται για να παρακολουθήσουν αν ο χρήστης είναι συνδεδεμένος, τον ρόλο του χρήστη και το όνομα χρήστη του συνδεδεμένου χρήστη.

Γίνεται έλεγχος για να ελεγχθεί αν ο χρήστης είναι ήδη συνδεδεμένος (isloggedin). Αν είναι ήδη συνδεδεμένος, επιστρέφεται ένα μήνυμα απόρριψης με κωδικό 403 (Forbidden) που δηλώνει ότι ο πόρος είναι απαγορευμένος. Αν ο χρήστης δεν είναι συνδεδεμένος, λαμβάνονται οι πιστοποιητικές πληροφορίες του χρήστη (email και κωδικός πρόσβασης) από την αίτηση POST.

Αναζητάμε στο collection των users αν για τα στοιχεία που εισήγαγε ο χρήστης υπάρχει κάποια αντίστοιχη εγγραφή στο σύστημα. Αν δεν υπάρχει κάποια εγγραφή που να αντιστοιχεί στα credentials εισαγωγής του χρήστη τότε επιστρέφεται μήνυμα λάθους με κωδικό 401 (Unauthorized). 
![image](https://github.com/VaggelisGavrielatos/YpoxreotikiErgasia23_e20019_Gavrielatos_Evangelos/assets/132483480/c80604fe-1c32-476a-9bc7-4c2b1d55885f)

Αλλιώς αν υπάρχει ο χρήστης τότε θέτουμε την μεταβλητή isloggedin σε True και στη μεταβλητή username1 αποθηκεύουμε το username του χρήστη που μόλις συνδέθηκε. Επίσης ανάλογα με τον ρόλο που έχει ο συνδεδεμένος χρήστης επιστρέφεται και το αντίστοιχο μήνυμα σύνδεσης με κωδικό 200 (OK). 
![image](https://github.com/VaggelisGavrielatos/YpoxreotikiErgasia23_e20019_Gavrielatos_Evangelos/assets/132483480/4f89dd30-eab3-4ee4-a620-0fe720e88492)
******************************************************************************************************************************************************************************************************************************
__@app.route("/logout", methods=["POST"])__

Αρχικά γίνεται έλεγχος για το εάν είναι συνδεδεμένος κάποιος χρήστης στην εφαρμογή. Αν δεν υπάρχει κάποιος συνδεδεμένος χρήστης τότε θα επιστραφεί μήνυμα λάθους με κωδικό 401 (Unauthorized).
![image](https://github.com/VaggelisGavrielatos/YpoxreotikiErgasia23_e20019_Gavrielatos_Evangelos/assets/132483480/507a2f27-021d-497d-b4e8-5a82123844ba)

Σε αντίθετη περίπτωση που ο χρήστης είναι συνδεδεμένος, τότε θέτεται η μεταβλητή isloggedin σε False και επιστρέφεται μήνυμα αποσύνδεσης με κωδικό 200 (OK).
![image](https://github.com/VaggelisGavrielatos/YpoxreotikiErgasia23_e20019_Gavrielatos_Evangelos/assets/132483480/c8ae707f-f4a5-408d-9c65-d7afe034b235)
****************************************************************************************************************************************************************************************************************************
__@app.route('/searchflight', methods=['POST'])__

Αρχικά γίνεται έλεγχος για το εάν είναι συνδεδεμένος κάποιος χρήστης στην εφαρμογή. Αν δεν υπάρχει κάποιος συνδεδεμένος χρήστης τότε θα επιστραφεί μήνυμα λάθους με κωδικό 401 (Unauthorized).
Στο συγκεκριμένο endpoint δεν υπάρχει έλεγχος για το αν ο χρήστης που είναι συνδεδεμένος είναι admin ή όχι καθώς τόσο ο admin όσο και οι απλοί users έχουν πρόσβαση στο συγκεκριμένο endpoint.

Το endpoint είναι σχεδιασμένο να δέχεται τιμές από τον χρήστη για τις εξής μεταβλητές "departure_airport", "arrival_airport", "date" και μια boolean μεταβλητή "all_flights". Ο χρήστης μπορεί να εισάγει τιμή σε μία δύο ή και όλες τις μεταβλητές. 
Ανάλογα με το ποιες μεταβλητές έχουν τιμή και τί ακριβώς τιμή έχουν γίνεται η αντίστοιχη αναζήτηση για το ποιές πτήσεις θα επιστραφούν. Αρχικά ορίζεται μια κενή λίστα results για να αποθηκευτούν εκεί τα απότελέσματα της αναζήτησης. 

Με τη βοήθεια της μεθόδου find() στο flights collection της βάσης δεδομένων, αναζητούνται οι πτήσεις ανάλογα με τα κριτήρια που έχουν δοθεί. Ανάλογα με τα πεδία που έχουν παρασχεθεί από τον χρήστη. Για παράδειγμα εάν έχουν παρασχεθεί αεροδρόμια αναχώρησης και άφιξης, εκτελείται έλεγχος για αντιστοιχία με τις πτήσεις που έχουν τα συγκεκριμένα αεροδρόμια. Εάν παρέχεται ημερομηνία, εκτελείται έλεγχος για αντιστοιχία με την προσδιορισμένη ημερομηνία. Ενω εάν το all_flights είναι αληθές, τότε επιστρέφονται όλες οι καταχωρήσεις πτήσεων από τη βάση δεδομένων.

Τα αποτελέσματα που πληρούν τα κριτήρια αποθηκεύονται στη λίστα results και προστίθενται τα κατάλληλα αναγνωριστικά στοιχεία για την εμφάνιση τους.

Αν η λίστα results είναι άδεια, επιστρέφεται ένα JSON αντικείμενο με μήνυμα "No flights found".
![image](https://github.com/VaggelisGavrielatos/YpoxreotikiErgasia23_e20019_Gavrielatos_Evangelos/assets/132483480/44fcfca9-5490-4095-9480-45f6324f3831)

Αν η λίστα results περιέχει αποτελέσματα, επιστρέφεται ένα JSON αντικείμενο με μήνυμα "Flights found" και τα αποτελέσματα της αναζήτησης.
![image](https://github.com/VaggelisGavrielatos/YpoxreotikiErgasia23_e20019_Gavrielatos_Evangelos/assets/132483480/adae34dd-8dbb-4d81-adc8-295cb8710f33)

****************************************************************************************************************************************************************************************************************************
__@app.route('/getflightdetails', methods=['POST'])__

Αρχικά γίνονται οι κλασσικοί έλεγχοι έτσι ώστε ο χρήστης που φτάνει στο συγκεκριμένο endpoint πρώτα να είναι συνδεδεμένος και δεύτερον να έχει τον ρόλο του user. Σε αντίθετες περιπτώσεις επιστρέφονται μηνύματα απόρριψης εισόδου στο συγκεκριμένο endpoint με κωδικούς 401 (Unauthorized) και τα δύο.

Στη συνέχεια λαμβάνει τα δεδομένα που υποβλήθηκαν από τον χρήστη μέσω της POST αίτησης. Αποθηκεύει το πεδίο "flight_id" από τη φόρμα που υποβλήθηκε.

Γίνεται αναζήτηση της πτήση με το συγκεκριμένο flight_id στη βάση δεδομένων και αν υπάρχει η πτήση, δημιουργεί ένα λεξικό με τα στοιχεία της πτήσης τα οποία επιστρέφονται σε μορφή JSON.
![image](https://github.com/VaggelisGavrielatos/YpoxreotikiErgasia23_e20019_Gavrielatos_Evangelos/assets/132483480/2eccc061-0ad9-4433-8d49-052b85c76c19)

Αν η πτήση δεν υπάρχει, επιστρέφει ένα μήνυμα λάθους ότι δεν υπάρχουν εγγεγραμμένες πτήσεις με αυτό το flight_id.
![image](https://github.com/VaggelisGavrielatos/YpoxreotikiErgasia23_e20019_Gavrielatos_Evangelos/assets/132483480/3cc54717-90e4-4791-85f5-fca8ec343d7c)

****************************************************************************************************************************************************************************************************************************
__@app.route('/ticketreservation', methods=['POST'])__

Αρχικά γίνονται οι έλεγχοι έτσι ώστε ο χρήστης που φτάνει στο συγκεκριμένο endpoint πρώτα να είναι συνδεδεμένος και δεύτερον να έχει τον ρόλο του user. Σε αντίθετες περιπτώσεις επιστρέφονται μηνύματα απόρριψης εισόδου στο συγκεκριμένο endpoint με κωδικούς 401 (Unauthorized) και τα δύο.

Ο χρήστης μέσω της αίτησης POST εισάγει τα προσωπικά του στοιχεία καθώς και τον τύπο του εισητηρίου που θέλει να κρατήσει (economy ή business σε οποιαδήποτε διαφορετική εισαγωγή εμφανίζεται μήνυμα λάθους με κωδικό 400 (Bad Request).
![image](https://github.com/VaggelisGavrielatos/YpoxreotikiErgasia23_e20019_Gavrielatos_Evangelos/assets/132483480/60f2fdf0-350c-48e4-be3d-7f546a53d11a)

Γίνεται μια αναζήτηση στο collection users για να διαπιστωθεί αν τα στοιχεία που εισήγαγε ο χρήστης είναι σωστά. Στην περίπτωση που δεν είναι κάποιο από αυτά σωστα δεν θα βρεθεί η εγγραφή του άρα θα επιστραφεί μήνυμα λάθους με κωδικό 400 (Bad Request).
![image](https://github.com/VaggelisGavrielatos/YpoxreotikiErgasia23_e20019_Gavrielatos_Evangelos/assets/132483480/0253542f-f235-4cf8-aee5-34e80d464d06)

Για την περίπτωση που ο χρήστης ζήτησε economy class ticket, αρχικά αναζητείται η πτήση με βάση το id που έδωσε ο χρήστης και αν δεν βρεθέι κάποια πτήση με αυτό το id τότε επιστρέφεται μήνυμα λάθους με κωδικό 404 (Not Found).
![image](https://github.com/VaggelisGavrielatos/YpoxreotikiErgasia23_e20019_Gavrielatos_Evangelos/assets/132483480/7db6d488-4910-453a-8b92-796153ff6d68)

Αν βρεθέι η πτήση με το id που έδωσε ο χρήστης και ελέγχεται αν υπάρχουν ακόμα διαθέσιμα εισητήρια της κατηγορίας economy στη συγκεκριμένη πτήση. Αν δεν υπάρχουν εμφανίζεται μήνυμα λάθους με κωδικό 409 (Conflict).
Στην αντιθετη περίπτωση που υπάρχουν ακόμα διαθέσιμα εισητήρια για τη συγκεκριμένη πτήση τότε αρχικά δίνεται στην κράτηση ένα μοναδικό ticket_id. Για το μοναδικό id της κράτησης δίνεται ένας τυχαίος αριθμός από το 0 έως το 99999999 και ελέγχεται εάν υπάρχει ήδη κάποια κράτηση στο collection reservations με αυτό το id και αν υπάρχει τότε δίνεται νέος τυχαίος αριθμός μέχρις ώτου να είναι μοναδικός στο collection. Έτσι δημιουργείται μια νέα κράτηση με τα στοιχεία τα οποία έδωσε ο χρήστης και το ticket_id που προέκυψε. 

Ταυτόχρονα ανανεώνονται και οι διαθεσιμότητες τόσο των συνολικών εισητηρίων όσο και μόνο των εισητηρίων κλάσης economy και ανανεώνεται η συγκεκριμένη πτήση με τις νέες διαθεσιμότητες. 
```
updated_ticket_left = int(flight["tickets_left"]) - 1
updated_economy_left = int(flight["economy_left"]) - 1
```
Τέλος επιστρέφεται μήνυμα επιτυχούς κράτησης εισητηρίου κλάσης economy.
![image](https://github.com/VaggelisGavrielatos/YpoxreotikiErgasia23_e20019_Gavrielatos_Evangelos/assets/132483480/56cb017a-2193-497e-8206-f11030c5ea44)

Για την περίπτωση που ο χρήστης ζήτησε business class ticket, αρχικά αναζητείται η πτήση με βάση το id που έδωσε ο χρήστης και αν δεν βρεθέι κάποια πτήση με αυτό το id τότε επιστρέφεται όπως πριν μήνυμα λάθους με κωδικό 404 (Not Found).

Αν βρεθέι η πτήση με το id που έδωσε ο χρήστης και ελέγχεται αν υπάρχουν ακόμα διαθέσιμα εισητήρια της κατηγορίας business στη συγκεκριμένη πτήση. Αν δεν υπάρχουν εμφανίζεται μήνυμα λάθους με κωδικό 409 (Conflict).
Στην αντιθετη περίπτωση που υπάρχουν ακόμα διαθέσιμα εισητήρια για τη συγκεκριμένη πτήση τότε αρχικά δίνεται στην κράτηση ένα μοναδικό ticket_id. Για το μοναδικό id της κράτησης δίνεται ένας τυχαίος αριθμός από το 0 έως το 99999999 και ελέγχεται εάν υπάρχει ήδη κάποια κράτηση στο collection reservations με αυτό το id και αν υπάρχει τότε δίνεται νέος τυχαίος αριθμός μέχρις ώτου να είναι μοναδικός στο collection. Έτσι δημιουργείται μια νέα κράτηση με τα στοιχεία τα οποία έδωσε ο χρήστης και το ticket_id που προέκυψε. 

Ταυτόχρονα ανανεώνονται και οι διαθεσιμότητες τόσο των συνολικών εισητηρίων όσο και μόνο των εισητηρίων κλάσης economy και ανανεώνεται η συγκεκριμένη πτήση με τις νέες διαθεσιμότητες. 
```
updated_ticket_left = int(flight["tickets_left"]) - 1
updated_business_left = int(flight["business_left"]) - 1
```
Τέλος επιστρέφεται μήνυμα επιτυχούς κράτησης εισητηρίου κλάσης business.
![image](https://github.com/VaggelisGavrielatos/YpoxreotikiErgasia23_e20019_Gavrielatos_Evangelos/assets/132483480/4be06bf2-ef8f-4891-a2a7-0795d67a6742)

****************************************************************************************************************************************************************************************************************************
__@app.route('/showreservations', methods=['GET'])__

Αρχικά γίνονται οι έλεγχοι έτσι ώστε ο χρήστης που φτάνει στο συγκεκριμένο endpoint πρώτα να είναι συνδεδεμένος και δεύτερον να έχει τον ρόλο του user. Σε αντίθετες περιπτώσεις επιστρέφονται μηνύματα απόρριψης εισόδου στο συγκεκριμένο endpoint με κωδικούς 401 (Unauthorized) και τα δύο.

Στη global μεταβλητή username1 είναι αποθηκευμένο το username του εκάστοτε συνδεδεμένου χρήστη και έτσι με βάση αυτό αναζητείται στο collection users ο συγκεκριμένος χρήστης (από τη στιγμή που είναι ήδη συνδεδεμένος δεν υπάρχει περίπτωση να μην βρεθεί οπότε δεν χρειάζεται να ελεγθεί αυτή η περίπτωης).

Δημιουργούμε μια κενή λίστα results έτσι ώστε να αποθηκεύσουμε εκεί τα αποτελέσματα που θα βρούμε στη συνέχεια. 

Ψάχνουμε στο collection reservations για να βρούμε κάποια ή κάποιες κρατήσεις με βάση το passport_number του εκάστοτε συνδεδεμένου χρήστη. Κάθε κράτηση που βρίσκουμε την βάζουμε στη λίστα results. 

Τέλος εάν το results είναι άδειο θα επιστραφεί μήνυμα "You have made no reservations yet!" με κωδικό 404 (Not Found).
Αλλιώς εάν το results έιναι γεμάτο θα επιστραφεί σε JSON μορφή μαζί με ένα μήνυμα 'Results found'. 
![image](https://github.com/VaggelisGavrielatos/YpoxreotikiErgasia23_e20019_Gavrielatos_Evangelos/assets/132483480/717c201a-ef00-44fe-a1b1-e5234e98094f)

****************************************************************************************************************************************************************************************************************************
__@app.route('/reservationdetails', methods=['POST'])__

Αρχικά γίνονται οι έλεγχοι έτσι ώστε ο χρήστης που φτάνει στο συγκεκριμένο endpoint πρώτα να είναι συνδεδεμένος και δεύτερον να έχει τον ρόλο του user. Σε αντίθετες περιπτώσεις επιστρέφονται μηνύματα απόρριψης εισόδου στο συγκεκριμένο endpoint με κωδικούς 401 (Unauthorized) και τα δύο.

Ο χρήστης καλείται κατά την αίτηση POST να εισάγει το ticket_id της κράτησης της οποίας θέλει να δεί τις λεπτομέριες. Γίνεται μια αναζήτηση στο collection reservations με βάση το ticket_id που έδωσε ο χρήστης. Σε περίπτωση που δεν βρεθεί κάποια κράτηση επιστρέφεται αντίστοιχο μήνυμα με κωδικό 404 (Not Found).
![image](https://github.com/VaggelisGavrielatos/YpoxreotikiErgasia23_e20019_Gavrielatos_Evangelos/assets/132483480/264a4dfe-1721-435b-b2b4-e6bdf9529b63)

Στην αντίθετη περίπτωση που το ticket_id είναι υπαρκτό ψάχνουμε να βρούμε την πτήση στην οποία αντιστοιχεί η συγκεκριμένη κράτηση (Δεν υπάρχει περίπτωση να μην βρεθεί καθώς το flight id που υπάρχει στην κράτηση είναι από προηγούμενο endpoint διασταυρωμένο ότι είναι υπαρκτό).
Στη συνέχεια δημιουργούμε ια λίστα result στην οποία μέσα βάζουμε τις απαραίτητες πληροφορίες ('Personal Info' και 'Flight Details') και την επιστρέφουμε σε JSON μορφή.
![image](https://github.com/VaggelisGavrielatos/YpoxreotikiErgasia23_e20019_Gavrielatos_Evangelos/assets/132483480/4488b0e4-e22e-45ca-99e2-3bcba02373fa)

****************************************************************************************************************************************************************************************************************************
__@app.route('/deletereservation', methods=['POST'])__
****************************************************************************************************************************************************************************************************************************
__@app.route('/deleteaccount', methods=['GET'])__
****************************************************************************************************************************************************************************************************************************
__@app.route('/createflight', methods=['POST'])__

Αρχικά γίνονται οι έλεγχοι έτσι ώστε ο χρήστης που φτάνει στο συγκεκριμένο endpoint πρώτα να είναι συνδεδεμένος και δεύτερον να έχει τον ρόλο του admin. Σε αντίθετες περιπτώσεις επιστρέφονται μηνύματα απόρριψης εισόδου στο συγκεκριμένο endpoint με κωδικούς 401 (Unauthorized) και τα δύο.

Ο admin εισάγει τα απαραίτητα δεδομένα για τη δημιουργία μιας νέας πτήσης "departure_airport", "arrival_airport", "date", "economy_left", "economy_cost", "business_left", "business_cost". 

Για το μοναδικό id της πτήσης δίνεται ένας τυχαίος αριθμός από το 0 έως το 9999 και ελέγχεται εάν υπάρχει ήδη κάποια πτήση στο collection flights με αυτό το id και αν υπάρχει τότε δίνεται νέος τυχαίος αριθμός μέχρις ώτου να είναι μοναδικός στο collection. 

Εισάγονται επίσης πεδία για τον αρχικό αριθμό εισητηρίων economy και business τα οποία παίρνουν τις τιμές "economy_left" και "business_left" (καθώς αφού μόλις δημιουργήθηκε αυτή η πτήση τα διαθέσιμα εισητήρια είναι και ο αρχικός αριθμός τους) καθώς και ο συνολικός αριθμός εισητηρίων που είναι το άθροισμα των "economy_left" και "business_left". 

Τέλος γίνεται insert_one η πτήση με τα στοιχεία αυτά και εμφανίζεται μήνυμα επιτυχούς προσθήκης της πτήσης με κωδικό 200 (OK).

![image](https://github.com/VaggelisGavrielatos/YpoxreotikiErgasia23_e20019_Gavrielatos_Evangelos/assets/132483480/d4693cf3-e71a-4381-9370-4628f35047f2)
****************************************************************************************************************************************************************************************************************************
__@app.route('/updateprice', methods=['POST'])__
****************************************************************************************************************************************************************************************************************************
__@app.route('/deleteflight', methods=['POST'])__
****************************************************************************************************************************************************************************************************************************
__@app.route('/adminflightdetails', methods=['POST'])__
****************************************************************************************************************************************************************************************************************************

































