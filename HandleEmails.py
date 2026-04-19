import re
import json
import re
import csv

def load_members_csv(csv_path: str):
    members = {}

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            lid = row["Lidnummer"].strip()

            voornaam = row.get("Voornaam", "").strip()
            tussen = row.get("Tussenvoegsel", "").strip()
            achternaam = row.get("Achternaam", "").strip()

            full_name = " ".join([voornaam, tussen, achternaam]).strip().replace("  ", " ")

            members[lid] = {
                "Lidnummer": lid,
                "Voornaam": voornaam.lower(),
                "Tussenvoegsel": tussen.lower(),
                "Achternaam": achternaam.lower(),
                "Naam": full_name.lower()
            }

    return members


def normalize_name(name: str) -> str:
    return " ".join(name.lower().strip().split())


def parse_email(email_text: str):

    lines = [line.strip() for line in email_text.splitlines() if line.strip()]

    data = {}

    lj = []
    lr = []
    dh = []

    current_section = None
    name_key = None

    def to_bool(value: str) -> bool:
        return bool(value.strip())

    for line in lines:

        # --- SECTION DETECTION ---
        if "Persoonlijke gegevens" in line:
            current_section = "persoonlijk"
            continue
        elif "Leiden – Jeugd" in line:
            current_section = "LJ"
            continue
        elif "Leiden – Recreanten" in line:
            current_section = "LR"
            continue
        elif "Den Haag – Trainingen" in line:
            current_section = "DH"
            continue
        elif "Opties" in line:
            current_section = "opties"
            continue
        elif "Aanvullende informatie" in line:
            current_section = "aanvullend"
            continue

        # --- PERSOONLIJKE GEGEVENS ---
        if current_section == "persoonlijk":
            if ":" in line:
                key, value = map(str.strip, line.split(":", 1))
                data[key] = value.lower()

                if key.lower() == "naam":
                    name_key = normalize_name(value)

        # --- TRAININGEN (ONLY SELECTED) ---
        elif current_section in ["LJ", "LR", "DH"]:
            match = re.match(r"^([A-Z]{2}_[A-Z]{2}\d+)\b\s*(.*)$", line)

            if match:
                code, rest = match.groups()

                if rest.strip():
                    if current_section == "LJ":
                        lj.append(code)
                    elif current_section == "LR":
                        lr.append(code)
                    elif current_section == "DH":
                        dh.append(code)

        # --- OPTIES (KEY: BOOL) ---
        elif current_section == "opties" or current_section == "aanvullend":
            if ":" in line:
                key, value = map(str.strip, line.split(":", 1))
                data[key] = to_bool(value)

                if key.startswith("DH_") and to_bool(value):
                    dh.append(key)
    if not name_key:
        raise ValueError("Naam not found in email")

    # add training lists
    data["LJ"] = lj
    data["LR"] = lr
    data["DH"] = dh

    return name_key, data

def input_trial(x,y):
    # x=inputs[0]
    # y=inputs[1]
    return x

def parse_multiple_emails(email_texts,csv_path):
    # email_texts = inputs[0]
    # csv_path=inputs[1]
    members = load_members_csv(csv_path)
    name_index = {v["Naam"]: k for k, v in members.items()}

    output = {}
    output = {}

    for email in email_texts:
        name, data = parse_email(email)

        lidnummer = name_index.get(name)
        if lidnummer and lidnummer in members:
            data.update(members[lidnummer])
            data["Lidnummer"] = lidnummer

            output[lidnummer] = data
        else:
            
            output[name] = data
            

    return json.dumps(output)

# -----------------------
# Example usage
# -----------------------
if __name__ == "__main__":
    email_input = ["""**Persoonlijke gegevens**
Naam: Olaf Verburg
Adres: vrouwensteeg 2a
Postcode / Plaats: 2312dz
Telefoonnummer: 0624492104
E-mailadres: olaf.verburg@gmail.com
Geboorte datum: [your-birth]
**Gekozen trainingen**
**Leiden – Jeugd (LJ)**
LJ_DI2 Dinsdag 19.15-20.15 uur (snel uur/gevorderden vanaf welp 2de jaars (<55.0 sec/2 rnd))
LJ_DO1 Donderdag 18.00-19.00 uur
**Leiden – Recreanten (LR)**
LR_MA2 
LR_DO2 Donderdag 19.15-20.15 uur
LR_VR 
LR_ZA1 
**Den Haag – Trainingen (DH)**
DH_MA1 
DH_MA2 
DH_DI1 
DH_DI2 
DH_WO1 
DH_WO2 
DH_WO3 
DH_DO1 
DH_DO2 
DH_VR1 
DH_VR2 
**Opties**
L_WedstrijdenLeiden: Ik doe mee.
L_Training_Geven_Leiden Ik wil training geven in Leiden
DH_LangeBaanWedstrijden: 
DH_MarathonWedstrijden: 
DH_ZesBanen: Ik doe mee aan de zes banen competitie
DH_Geen_wedstrijden: 
DH_nog_normaal_kaartje_in_bezit: 
DH_Doorlooppasje: 
DH_Stoppen: 
DH_TrainerDH: 
**Aanvullende informatie**
Opmerking: [your-subject]
JaNAw: 
NeeNAw: Nee, ik geef geen toestemming voor het gebruik van beeldmateriaal op de website van de ijsclub en overige social media van de ijsclub.

""", """
    **Persoonlijke gegevens**
    Naam: Firstname Lastname
    Adres: adres
    Postcode_Plaats: 1234 AB Stompwijk
    Telefoonnummer: 0612345678
    E-mailadres: henshensen530@gmail.com
    Geboorte datum: [your-birth]
    **Gekozen trainingen**
    **Leiden – Jeugd (LJ)**
    LJ_DI2 Dinsdag 19.15-20.15 uur (snel uur/gevorderden vanaf welp 2de jaars (<55.0 sec/2 rnd))
    LJ_DO1 
    **Leiden – Recreanten (LR)**
    LR_MA2 
    LR_DO2 
    LR_VR Vrijdag 19.15-20.15 uur
    LR_ZA1 
    **Den Haag – Trainingen (DH)**
    DH_MA1 
    DH_MA2 
    DH_DI1 
    DH_DI2 Dinsdag 2 18.30-19.45 uur, (neo)senioren, Jun. A, B
    DH_WO1 
    DH_WO2 
    DH_WO3 
    DH_DO1 
    DH_DO2 
    DH_VR1 
    DH_VR2 
    **Opties**
    L_WedstrijdenLeiden: Ik doe mee.
    L_Training_Geven_Leiden 
    DH_LangeBaanWedstrijden: 
    DH_MarathonWedstrijden: Ik doe mee aan gewestelijke marathoncompetitie
    DH_ZesBanen: 
    DH_Geen_wedstrijden: 
    DH_nog_normaal_kaartje_in_bezit: 
    DH_Doorlooppasje: Ik wil komend seizoen een doorlooppasje/passeerpas (Pasje voor ouder om schaatsen aan te doen)
    DH_Stoppen: 
    DH_TrainerDH: 
    **Aanvullende informatie**
    Opmerking: [your-subject]
    JaNAw: Ja, ik geef toestemming voor het gebruik van beeldmateriaal op de website van de ijsclub en overige social media van de ijsclub.
    NeeNAw: 


    """]

    csv_path="/Users/olafv/Desktop/Automation/LidmaatschapNAW.csv"
    output = parse_multiple_emails(email_input,csv_path)

    print(output)