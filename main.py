from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import os
import re

def setup_driver():
    options = Options()
    options.add_argument("--headless")  # Activer le mode headless si nécessaire
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver_service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=driver_service, options=options)
    return driver

def get_filename():
    """Générer un nom de fichier basé sur la date et l'heure actuelles dans le répertoire 'data'."""
    directory = "ScriptWeb/data"
    if not os.path.exists(directory):
        os.makedirs(directory)  # Créer le répertoire s'il n'existe pas
    return os.path.join(directory, datetime.now().strftime("%Y-%m-%d-%H:%M:%S") + ".txt")

def write_to_file(data, filename):
    """Écrire les données dans un fichier texte."""
    with open(filename, "a", encoding="utf-8") as file:
        for line in data:
            file.write(f"{line}\n")

def extract_relevant_data(row_text):
    """Extraire le détail du contrôle, la note et les coefficients."""
    try:
        # Extraire "Détail sur le contrôle" entre "Détail" et la première virgule
        detail_controle = re.search(r"Détail.*?contrôle", row_text)
        detail_controle = (
            re.sub(r".*?\b(sur le|sur|le)\b", "", detail_controle.group(0)).strip()
            if detail_controle
            else "Non trouvé"
        )
        
        # Extraire la note entre "Note" et avant "Coefficient"
        note = re.search(r"Note\s*([\d,]+)", row_text)
        note = note.group(1).strip() if note else "Non trouvé"
        
        # Extraire les coefficients numériques après "Coef"
        coefficients = re.findall(r"Coef.*?(\d+)", row_text)
        coef_epreuve = coefficients[0] if len(coefficients) > 0 else "Non trouvé"
        coef_matiere = coefficients[1] if len(coefficients) > 1 else "Non trouvé"
        
        # Formater proprement les données pour éviter les erreurs
        return (
            detail_controle, 
            note if note != "Non trouvé" else "", 
            coef_epreuve if coef_epreuve != "Non trouvé" else "", 
            coef_matiere if coef_matiere != "Non trouvé" else ""
        )
    except Exception as e:
        return f"Erreur: {e}", "", "", ""

def get_latest_file(exclude_file=None):
    """Récupérer le fichier le plus récent dans le répertoire 'data', en excluant un fichier spécifique si fourni."""
    directory = "ScriptWeb/data"
    files = [
        os.path.join(directory, f) for f in os.listdir(directory) 
        if os.path.isfile(os.path.join(directory, f))
    ]
    files = sorted(files, key=os.path.getmtime, reverse=True)  # Trier par date de modification décroissante
    if exclude_file:
        files = [f for f in files if f != exclude_file]  # Exclure le fichier actuel
    return files[0] if files else None


def detect_new_entries(new_file, old_file):
    """
    Compare le contenu de deux fichiers et identifie les nouvelles lignes dans le nouveau fichier.
    :param new_file: Chemin du fichier récemment généré.
    :param old_file: Chemin du fichier précédent.
    :return: Liste des nouvelles lignes.
    """
    with open(new_file, "r", encoding="utf-8") as nf, open(old_file, "r", encoding="utf-8") as of:
        new_lines = set(nf.readlines())  # Convertir en ensemble pour des recherches rapides
        old_lines = set(of.readlines())
    
    new_entries = new_lines - old_lines  # Identifier les lignes présentes dans le nouveau fichier mais pas dans l'ancien
    return list(new_entries)

def scrape_webaurion():
    driver = setup_driver()
    wait = WebDriverWait(driver, 8)
    filename = get_filename()  # Générer le nom du fichier actuel

    try:
        login_url = "https://webaurion.centralelille.fr/faces/Login.xhtml"
        driver.get(login_url)
        
        # Connexion et navigation (comme dans votre code existant)
        username_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
        password_field = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "j_idt27")
        username_field.send_keys("$$$$$$$")
        password_field.send_keys("$$$$$$$")
        login_button.click()
        time.sleep(1)

        submenu_44413 = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "submenu_44413")))
        submenu_44413.click()
        time.sleep(2)
        submenu_3056364 = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "submenu_3056364")))
        submenu_3056364.click()
        time.sleep(2)
        item_3084597 = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "item_3084597")))
        item_3084597.click()
        time.sleep(1.5)

        while True:
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            tbody = soup.find("tbody", id="form:j_idt181_data")
            if tbody:
                rows = tbody.find_all("tr", class_=["ui-widget-content", "ui-datatable-even", "CursorInitial"])
                data_to_write = []
                for row in rows:
                    columns = [col.text.strip() for col in row.find_all("td")]
                    row_text = ", ".join(columns)
                    
                    # Extraire les données pertinentes
                    detail, note, coef_epreuve, coef_matiere = extract_relevant_data(row_text)
                    data_to_write.append(f"Détail: {detail} & Note: {note} & Coef Épreuve: {coef_epreuve} & Coef Matière: {coef_matiere}")
                
                write_to_file(data_to_write, filename)
            else:
                pass

            try:
                next_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "ui-paginator-next")))
                if "ui-state-disabled" in next_button.get_attribute("class"):
                    break
                next_button.click()
                time.sleep(3)
            except Exception:
                break

        # Comparer avec le fichier précédent
        previous_file = get_latest_file(exclude_file=filename)
        if previous_file:
            new_entries = detect_new_entries(filename, previous_file)
            if new_entries:
                print("\nNouvelles notes trouvées :")
                print("\n".join(new_entries))
            else:
                print("\nAucune nouvelle note.")
        else:
            print("\nAucun fichier précédent trouvé pour comparaison.")

    except Exception as e:
        print(f"Erreur lors du traitement : {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    start_time = time.time()  # Début du chronométrage
    scrape_webaurion()
    end_time = time.time()  # Fin du chronométrage

    elapsed_time = end_time - start_time  # Temps écoulé en secondes
    print(f"Le programme a pris {elapsed_time:.2f} secondes.")