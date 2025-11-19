Tu je návrh architektúry a plánu pre **Proof of Concept (PoC)**, ktorý je optimalizovaný na rýchlosť vývoja („time-to-market“) a nízku cenu.

---

### **1\. Odporúčaný Tech Stack (PoC \- Rýchle & Lacné)**

Pre PoC nepotrebujete zložitý microservices cluster. Potrebujete monolitickú architektúru, ktorá sa ľahko nasadí.

* **Backend:** **Python \+ FastAPI**.  
  * *Prečo:* Rýchly, moderný, asynchrónny (skvelý pre AI requesty), automatická dokumentácia (Swagger UI).  
* **Frontend:** **Streamlit**.  
  * *Prečo:* Toto je najdôležitejšia voľba pre "rýchlo doručiteľné". Streamlit umožňuje vytvoriť UI v Pythone bez znalosti HTML/CSS/JS. Je ideálny pre interné nástroje, dashboardy a "Human-in-the-loop" rozhrania.  
* **Databáza (Metadata \+ Vektory):** **PostgreSQL \+ pgvector**.  
  * *Prečo:* Scaleway ponúka Managed Database for PostgreSQL. Rozšírenie `pgvector` vám umožní ukladať vektory v tej istej DB ako používateľské dáta. Nemusíte platiť za ďalšiu službu (ako Pinecone).  
* **Task Queue (Asynchrónne úlohy):** **Celery \+ Redis**.  
  * *Prečo:* Kroky 2 až 6 môžu trvať dlho. Používateľ nemôže čakať s otvoreným prehliadačom. Celery bude procesovať dokumenty na pozadí.  
* **Hosting (Scaleway):**  
  * **Scaleway Container Registry:** Na uloženie Docker images.  
  * **Scaleway Serverless Containers** (alebo jedna lacná inštancia **Stardust/Learning**): Pre backend a frontend. Serverless škáluje na nulu (šetrí peniaze), ale pre PoC je často jedna VM (Virtual Machine) za 10 €/mesiac jednoduchšia na správu (Docker Compose).  
  * **Object Storage (S3 compatible):** Na ukladanie PDF a obrázkov.

---

### **2\. Architektúra a Workflow (Technický pohľad)**

Tu je rozpis, ako jednotlivé kroky technicky implementovať:

#### **Krok 0: Infraštruktúra**

* Všetko beží v kontajneroch (Docker).  
* Dáta sú šifrované v pokoji (v DB a Object Storage).

#### **Krok 1: Upload a Validácia**

* **Frontend (Streamlit):** Používateľ nahrá súbory.  
* **Backend:** Rýchla kontrola formátu (MIME type), veľkosti a základná kontrola vírusov (voliteľné).  
* **Akcia:** Súbory sa nahrajú do **Scaleway Object Storage** (bucket `raw-documents`). V DB sa vytvorí záznam `Claim` so statusom `PROCESSING`.

#### **Krok 2: OCR a Extrakcia (Mistral OCR)**

* **Worker (Celery):** Stiahne dokument, pošle ho do **Mistral Document AI API**.  
* **Výstup:** Získate Markdown/Text reprezentáciu dokumentu.  
* **Uloženie:** Text sa uloží do DB k príslušnému claimu.

#### **Krok 3: Očistenie dát (Cleaning)**

* *Pozor:* Tu by som bol opatrný s posielaním dát do externej AI pred anonymizáciou.  
* **Riešenie:** Pre PoC použite Python knižnice (`symspellpy` pre preklepy, `unidecode` pre diakritiku, Regex pre formátovanie). Ak musíte použiť LLM na opravu gramatiky, uistite sa, že máte s Mistralom podpísanú DPA (Data Processing Agreement), inak porušujete logiku "najprv očistiť, potom anonymizovať".  
* **Odporúčanie:** Zatiaľ riešte len základné čistenie Python skriptom, aby ste neposielali PII (osobné údaje) von pred krokom 4\.

#### **Krok 4: Anonymizácia (Microsoft Presidio)**

* **Lokálny beh:** Microsoft Presidio beží ako Python knižnica priamo vo vašom kontajneri (nevolá externú API, čo je super pre bezpečnosť).  
* **Proces:** Presidio nájde mená, rodné čísla, EČV, adresy a nahradí ich za `<PERSON>`, `<DATE>`, atď. Zároveň si uložíte "mapu" (deanonymizačný kľúč), ak by ste to potrebovali vrátiť späť (voliteľné, pre analýzu zvyčajne netreba).  
* **Status:** Zmena statusu v DB na `WAITING_FOR_APPROVAL`.

#### **Krok 5: Human-in-the-loop (Frontend)**

* Administrátor (likvidátor) otvorí Streamlit dashboard.  
* Vidí: Pôvodný text vs. Anonymizovaný text.  
* **Akcia:** Ak Presidio zlyhalo (napr. neodstránilo meno), admin to ručne označí/upraví.  
* **Tlačidlo:** "Schváliť pre analýzu".  
* **Backend:** Uloží schválenú verziu textu, vytvorí embeddingy (vektory) pomocou **Mistral Embeddings API** a uloží ich do **PostgreSQL (pgvector)**.

#### **Krok 6: AI Analýza (RAG \+ Mistral Chat)**

* **Retrieval:** Na základe zvolených promptov (napr. "Je nárok oprávnený podľa výluk?") systém vyhľadá relevantné časti z vektorovej DB (dokumenty poistnej zmluvy, všeobecné podmienky \+ aktuálny dokument udalosti).  
* **Generovanie:** Volanie **Mistral Large** alebo **Mistral Small** s kontextom.  
* **Výstup:** JSON štruktúra s odporúčaním (Schváliť/Zamietnuť/Došetriť) a odôvodnením.

---

### **3\. Implementačný plán (Krok za krokom)**

#### **Fáza 1: Setup (1-2 dni)**

1. Vytvoriť účet na **Scaleway** a **Mistral AI**.  
2. Nastaviť **PostgreSQL** na Scaleway.  
3. Pripraviť repozitár s `docker-compose.yml` (obsahujúci FastAPI, Streamlit, Redis).

#### **Fáza 2: Backend Core (3-4 dni)**

1. Vytvoriť FastAPI endpointy pre upload (`/upload`).  
2. Nastaviť Celery worker pre OCR.  
3. Integrácia **Microsoft Presidio** (skúste najprv základný model, pre slovenčinu možno budete musieť doplniť vlastné "recognizers" cez Regex – napr. pre slovenské Rodné číslo).

#### **Fáza 3: Frontend & HITL (3-4 dni)**

1. Vytvoriť Streamlit appku.  
2. Stránka 1: "Nahlásenie udalosti" (Upload).  
3. Stránka 2: "Admin Dashboard" – tabuľka claimov, detail claimu s farebným zvýraznením anonymizovaných entít (Presidio vracia pozície entít, Streamlit `annotated_text` komponent to vie pekne zobraziť).

#### **Fáza 4: RAG & Analýza (3-4 dni)**

1. Implementácia `pgvector`.  
2. Logika pre volanie Mistral Chat API s definovanými promptami.  
3. Generovanie PDF reportu (napr. pomocou knižnice `ReportLab` alebo `WeasyPrint` v Pythone).

---

### **4\. Ukážka kódu (Python \- FastAPI \+ Presidio)**

Pre lepšiu predstavu, ako jednoducho sa robí anonymizácia v Pythone:

Python  
\# backend/services/anonymizer.py  
from presidio\_analyzer import AnalyzerEngine  
from presidio\_anonymizer import AnonymizerEngine

\# Inicializácia enginov  
analyzer \= AnalyzerEngine()  
anonymizer \= AnonymizerEngine()

def anonymize\_text(text: str):  
    \# 1\. Analýza (Hľadanie entít)  
    \# Pre slovenčinu je vhodné pridať custom patterny alebo použiť multilingválne modely  
    results \= analyzer.analyze(text=text, language='en') \# Zatiaľ 'en', pre SK treba doladiť config

    \# 2\. Anonymizácia (Nahradenie)  
    anonymized\_result \= anonymizer.anonymize(  
        text=text,  
        analyzer\_results=results  
    )  
      
    return anonymized\_result.text

### **5\. Odhad nákladov (Mesačne na Scaleway)**

Pre PoC verziu (Lacná verzia):

* **Compute (Instance):** 1x GP1-XS alebo menšia Learning Instance (cca 10 \- 20 €).  
* **Database:** Managed PostgreSQL (cca 15 €) alebo Docker kontajner na inštancii (0 €, ale vy spravujete zálohy). Odporúčam Managed DB pre pokoj v duši.  
* **Object Storage:** 75 GB je zadarmo, potom pár centov.  
* **Mistral API:** Pay-as-you-go. Pre PoC to bude pár eur (podľa počtu dokumentov).  
* **Celkom:** **\~30 € \- 50 € mesačne**.

### **Zhrnutie a Ďalší krok**

Tento stack (**FastAPI, Streamlit, Postgres/pgvector, Docker**) na **Scaleway** je:

1. **EU Compliant** (Hosting v Paríži/Varšave, Mistral je FR).  
2. **Lacný** (Open source komponenty, lacný cloud).  
3. **Rýchly na vývoj** (Python ekosystém).

**Chceli by ste, aby som vám pripravil štruktúru `docker-compose.yml` súboru pre tento projekt, aby ste mohli okamžite začať?**

