import requests
from bs4 import BeautifulSoup
import threading
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# Configuration de l'e-mail
def send_email(subject, body):
    from_email = "youshii14@gmail.com"
    to_email = "youshii14@gmail.com"
    password = "fela khuz wclb zgnb"  # Remplacez par votre mot de passe d'application

    # Création de l'objet de message MIMEMultipart
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attachement du corps de l'e-mail
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connexion au serveur SMTP de Gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        print("E-mail envoyé avec succès")
    except Exception as e:
        print(f"Échec de l'envoi de l'e-mail : {e}")

def scrape_logements():
    try:
        # Define the URL
        url = "https://trouverunlogement.lescrous.fr/tools/36/search?bounds=5.2694745_43.6259224_5.5063013_43.4461058"

        # Send a GET request to the URL
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all the <div> elements with the specific class
            logement_divs = soup.find_all('div', class_='fr-card__body')

            logements = []
            for logement in logement_divs:
                # Extract the title, description, size, and other details
                title = logement.find('h3', class_='fr-card__title').get_text(strip=True)
                description = logement.find('p', class_='fr-card__desc').get_text(strip=True)
                size = logement.find('p', class_='fr-card__detail').get_text(strip=True)
                details = logement.find_all('p', class_='fr-card__detail')

                other_details = [detail.get_text(strip=True) for detail in details[1:]]

                logements.append({
                    'title': title,
                    'description': description,
                    'size': size,
                    'details': other_details
                })

            num_logements = len(logements)

            # Format the results
            results = f"Nombre total de logements trouvés : {num_logements}\n\n"

            if num_logements > 0:
                for logement in logements:
                    results += f"Title: {logement['title']}\n"
                    results += f"Description: {logement['description']}\n"
                    results += f"Size: {logement['size']}\n"
                    results += f"Details: {', '.join(logement['details'])}\n"
                    results += "-----\n"

                # Get the current date and time
                now = datetime.now()
                date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")

                subject = f"Résultats de la recherche ({date_time_str}) : {num_logements} logements trouvés"
                # Send the email with results only if there are logements found
                send_email(subject, results)
            else:
                print("Aucun logement trouvé.")

        else:
            print(f"Échec de la récupération de la page. Code d'état : {response.status_code}")

    except Exception as e:
        print(f"Une erreur s'est produite : {e}")

    # Schedule the function to run again in 60 seconds
    if not stop_event.is_set():
        threading.Timer(60, scrape_logements).start()

# Create an Event object to signal the stopping of the thread
stop_event = threading.Event()

try:
    # Start the initial function call
    scrape_logements()

    # Keep the main thread alive to allow periodic execution
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    # Set the stop_event when a keyboard interrupt is detected
    stop_event.set()
    print("Arrêt du thread de scraping fin.")
