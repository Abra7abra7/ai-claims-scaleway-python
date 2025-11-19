# User Guide - AI Claims Processing System

## Úvod

Tento systém umožňuje automatizované spracovanie poistných nárokov pomocou umelej inteligencie. Systém dokáže:
- Extrahovať text z PDF dokumentov (OCR)
- Anonymizovať citlivé osobné údaje
- Analyzovať nároky pomocou AI s rôznymi typmi analýz

## Prístup k systému

### Frontend (Používateľské rozhranie)
```
http://YOUR_SERVER_IP:8501
```

### Backend API (Pre programátorský prístup)
```
http://YOUR_SERVER_IP:8000/docs
```

## Používateľské rozhranie

Systém má dve hlavné sekcie:

### 1. Nahlásenie poistnej udalosti

**Účel:** Nahrávanie dokumentov k poistnej udalosti

**Postup:**
1. Kliknite na "Nahlásenie poistnej udalosti" v ľavom menu
2. Kliknite na "Browse files" alebo pretiahnite súbory
3. Vyberte jeden alebo viac PDF súborov
4. Kliknite "Odoslať"
5. Počkajte na potvrdenie o úspešnom nahratí

**Podporované formáty:**
- PDF súbory
- Viacero súborov naraz (všetky sa zoskupia do jedného nároku)

**Čo sa deje na pozadí:**
1. Súbory sa nahrávajú do Scaleway Object Storage
2. Systém automaticky spúšťa OCR (extrakciu textu)
3. Text sa anonymizuje (odstránia sa citlivé údaje)
4. Nárok čaká na schválenie administrátorom

### 2. Admin Dashboard

**Účel:** Prehľad a správa nárokov

**Funkcie:**

#### Zobrazenie nárokov
- Každý nárok má jedinečné ID
- Status nároku:
  - **PROCESSING** - Prebieha spracovanie dokumentov
  - **WAITING_FOR_APPROVAL** - Čaká na schválenie a analýzu
  - **ANALYZED** - Analýza dokončená

#### Zobrazenie dokumentov
Pre každý nárok vidíte:
- Zoznam všetkých nahraných dokumentov
- Pôvodný text (výsledok OCR)
- Anonymizovaný text (citlivé údaje nahradené)

**Príklad anonymizácie:**
```
Pôvodný text:
"Pacient Ján Novák, rodné číslo 901231/1234, 
telefón +421 901 234 567"

Anonymizovaný text:
"Pacient <OSOBA>, rodné číslo <RODNE_CISLO>, 
telefón <TELEFON>"
```

#### AI Analýza

**Postup:**
1. Počkajte kým nárok prejde do statusu "WAITING_FOR_APPROVAL"
2. V sekcii "AI Analýza" vyberte typ analýzy z dropdown menu
3. Prečítajte si popis vybraného typu analýzy
4. Kliknite "Schváliť a Analyzovať"
5. Počkajte na dokončenie analýzy (zvyčajne 5-30 sekúnd)
6. Obnovte stránku pre zobrazenie výsledkov

**Typy analýz:**

1. **Štandardná analýza**
   - Základná analýza poistnej udalosti
   - Vhodné pre väčšinu prípadov
   - Poskytuje odporúčanie, dôvod a confidence score

2. **Detailná zdravotná analýza**
   - Špecializovaná na zdravotné nároky
   - Analyzuje ICD-10 kódy
   - Hodnotí vhodnosť liečby
   - Identifikuje medicínske kódy

3. **Detekcia podvodov**
   - Zameraná na identifikáciu podozrivých prvkov
   - Hľadá nekonzistencie v dokumentoch
   - Poskytuje fraud risk score
   - Vypíše red flags (varovné signály)

4. **Rýchle posúdenie**
   - Zjednodušená rýchla analýza
   - Vhodné pre jednoduché prípady
   - Stručné vysvetlenie

5. **Slovenská analýza**
   - Celá analýza v slovenskom jazyku
   - Výsledky a vysvetlenia po slovensky

#### Výsledky analýzy

Po dokončení analýzy uvidíte:

**Odporúčanie:**
- **APPROVE** - Schváliť nárok
- **REJECT** - Zamietnuť nárok
- **INVESTIGATE** - Vyžaduje ďalšie prešetrenie

**Confidence (Istota):**
- Hodnota 0.0 - 1.0
- Vyššia hodnota = vyššia istota AI v rozhodnutí
- Príklad: 0.9 = 90% istota

**Reasoning (Dôvod):**
- Detailné vysvetlenie rozhodnutia
- Citácie z dokumentov
- Odôvodnenie

**Missing Info (Chýbajúce informácie):**
- Zoznam chýbajúcich dokumentov alebo informácií
- Čo je potrebné doplniť

**Príklad výsledku:**
```json
{
  "recommendation": "APPROVE",
  "confidence": 0.9,
  "reasoning": "Claim documents provide clear evidence of injury...",
  "missing_info": []
}
```

## Časté otázky (FAQ)

### Q: Ako dlho trvá spracovanie dokumentov?
**A:** OCR a anonymizácia zvyčajne trvá 2-5 sekúnd na dokument. Pri viacerých dokumentoch sa spracovávajú paralelne.

### Q: Prečo sa mi nezobrazuje text po nahratí?
**A:** Počkajte chvíľu a obnovte stránku. Spracovanie môže trvať niekoľko sekúnd. Ak problém pretrváva, skontrolujte logy.

### Q: Môžem nahrať viac ako 3 súbory naraz?
**A:** Áno, systém podporuje nahrávanie viacerých súborov. Všetky sa zoskupia do jedného nároku.

### Q: Aké údaje sa anonymizujú?
**A:** 
- Mená osôb
- Telefónne čísla
- Email adresy
- Slovenské rodné čísla
- IBAN čísla účtov

### Q: Môžem vidieť pôvodný text pred anonymizáciou?
**A:** Áno, v Admin Dashboard vidíte oba texty vedľa seba - pôvodný aj anonymizovaný.

### Q: Čo znamená "Service tier capacity exceeded"?
**A:** Dosiahli ste limit Mistral API. Počkajte chvíľu alebo upgradujte váš Mistral plán.

### Q: Ako môžem pridať vlastný typ analýzy?
**A:** Upravte súbor `app/prompts.py` a pridajte nový prompt do slovníka `PROMPTS`. Reštartujte backend.

### Q: Sú dokumenty bezpečne uložené?
**A:** Áno, všetky dokumenty sú:
- Uložené v private S3 bucket
- Prístupné len cez presigned URLs (časovo obmedzené)
- Anonymizované pred odoslaním do AI

### Q: Môžem exportovať výsledky?
**A:** Momentálne nie, ale výsledky sú uložené v databáze a môžete ich získať cez API endpoint `/claims/{claim_id}`.

### Q: Ako môžem zmazať nárok?
**A:** Momentálne nie je implementované v UI. Môžete to urobiť cez databázu alebo API.

## API Použitie

Pre programátorský prístup k systému:

### Získanie zoznamu nárokov
```bash
curl http://YOUR_SERVER_IP:8000/claims/
```

### Získanie detailu nároku
```bash
curl http://YOUR_SERVER_IP:8000/claims/1
```

### Nahranie súborov
```bash
curl -X POST http://YOUR_SERVER_IP:8000/upload/ \
  -F "files=@document1.pdf" \
  -F "files=@document2.pdf"
```

### Získanie zoznamu promptov
```bash
curl http://YOUR_SERVER_IP:8000/prompts/
```

### Schválenie a analýza
```bash
curl -X POST http://YOUR_SERVER_IP:8000/approve/1 \
  -H "Content-Type: application/json" \
  -d '{"prompt_id": "detailed_medical"}'
```

## Podpora

Pre technické problémy:
- Skontrolujte logy: `docker compose logs`
- GitHub Issues: https://github.com/Abra7abra7/ai-claims-scaleway-python/issues
- Email: [váš support email]

## Changelog

### Verzia 1.0.0 (2024-11-19)
- Prvé vydanie
- Multi-file upload
- OCR pomocou Mistral Document AI
- Anonymizácia pomocou Microsoft Presidio
- 5 typov AI analýz
- Streamlit frontend
- FastAPI backend
- Celery async processing
