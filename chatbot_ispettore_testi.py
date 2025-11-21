import json
import ollama
import os
from spellchecker import SpellChecker

# =========================================================
#  1. DATABASE DI ESEMPI (RAG)
# =========================================================

def carica_database():
    if not os.path.exists("database_testi.json"):
        raise FileNotFoundError(
            "Il file database_testi.json non esiste nella cartella del progetto."
        )
    with open("database_testi.json", "r", encoding="utf-8") as f:
        return json.load(f)


def similarita(a, b):
    """Semplice misura di similarità basata sulle parole condivise."""
    set_a = set(a.lower().split())
    set_b = set(b.lower().split())
    return len(set_a.intersection(set_b))


def recupera_contesto(database, testo_utente, top_k=3):
    """Restituisce i top_k esempi più simili come contesto per la RAG."""
    punteggi = []
    for entry in database:
        score = similarita(testo_utente, entry["sbagliato"])
        punteggi.append((score, entry))

    punteggi.sort(key=lambda x: x[0], reverse=True)
    migliori = [entry for _, entry in punteggi[:top_k]]

    contesto = ""
    for i, es in enumerate(migliori, start=1):
        contesto += (
            f"Esempio {i} (testo corretto da te in passato):\n"
            f"- Testo sbagliato: {es['sbagliato']}\n"
            f"- Correzione: {es['corretto']}\n\n"
        )
    return contesto

# =========================================================
#  2. PROMPT MIGLIORATO (OBBLIGO CORREZIONE TUTTI ERRORI)
# =========================================================

SYSTEM_PROMPT = """
Sei un correttore professionale di testi italiani.

Hai due compiti distinti:

1) Fornire un ELENCO DELLE CORREZIONI:
   - Elenca solo errori REALI presenti nel testo originale
   - Spiega cosa era sbagliato e perché
   - Non ignorare alcun errore ortografico o di punteggiatura
   - Se una parola è corretta, NON segnalarla come errore

2) Restituire la VERSIONE CORRETTA del testo:
   - Mantieni lo stesso significato dell’utente
   - Puoi modificare il tono della frase senza alterarne il senso
   - Correggi tutti gli errori: ortografia, grammatica, concordanze, punteggiatura, maiuscole
   - Aggiungi la punteggiatura mancante o rimuovi quella scorretta quando necessario per migliorare la leggibilità
   - Tutti i nomi propri devono iniziare con la lettera maiuscola
   - La prima lettera di ogni frase deve essere maiuscola
   - NON lasciare errori residui
   - NON inventare parole
   - NON aggiungere o interpretare contenuti
   - NON copiare errori dal testo originale

FORMATTA ESATTAMENTE COSÌ:

---CORREZIONI E SPIEGAZIONI---
- [errore] → [correzione]: [spiegazione breve]

---VERSIONE CORRETTA---
[frase corretta qui]
"""


# =========================================================
#  3. FUNZIONE DI CORREZIONE ORTOGRAFICA DI BACKUP
# =========================================================

spell = SpellChecker(language='it') #se il modello non correge la parola, il backup controlla la parola e la correge se è errata

def correzione_ortografica_backup(testo):
    parole = testo.split()
    parole_corrette = []
    for parola in parole:
        if spell.unknown([parola]):
            parola_corr = spell.correction(parola)
            if parola_corr is None:
                parola_corr = parola  # lascia la parola originale se non trova correzione
            parole_corrette.append(parola_corr)
        else:
            parole_corrette.append(parola)
    return ' '.join(parole_corrette)

# =========================================================
#  4. FUNZIONE DI CAPITALIZZAZIONE NOMI E FRASI
# =========================================================

def capitalizza_nomi_e_frasi(testo):
    # Capitalizza la prima lettera di ogni frase
    frasi = testo.split(". ")
    frasi = [f.strip().capitalize() if f else "" for f in frasi]
    testo = ". ".join(frasi)

    # Capitalizza nomi propri comuni (aggiungi altri se vuoi)
    nomi_propri = ["Marco", "Luca", "Maria", "Anna", "Giovanni"]
    for nome in nomi_propri:
        testo = testo.replace(nome.lower(), nome)
    return testo

# =========================================================
#  5. FUNZIONE DI ANALISI
# =========================================================

def analizza_testo(modello, testo_utente, database):    #parte centrale 
    contesto = recupera_contesto(database, testo_utente)   #recupera contesto rag

    prompt = f"""                                                   
Questi sono esempi che hai corretto in passato (memoria RAG):    

{contesto}

Ora correggi questo nuovo testo seguendo rigorosamente le istruzioni:

TESTO DELL'UTENTE:
{testo_utente}
"""

    try:                                        #viene chiamato ollama per effettuare la correzione
        risposta = ollama.chat(
            model=modello,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ]
        )
        testo_corretto = risposta.message["content"].strip()

        # applica correzione ortografica di backup e capitalizzazione
        if "---VERSIONE CORRETTA---" in testo_corretto:
            parti = testo_corretto.split("---CORREZIONI E SPIEGAZIONI---")
            versione = parti[0].replace("---VERSIONE CORRETTA---", "").strip()
            versione_finale = correzione_ortografica_backup(versione)
            versione_finale = capitalizza_nomi_e_frasi(versione_finale)
            correzioni = parti[1].strip() if len(parti) > 1 else ""
            return f"---VERSIONE CORRETTA---\n{versione_finale}\n\n---CORREZIONI E SPIEGAZIONI---\n{correzioni}"
        else:
            return capitalizza_nomi_e_frasi(correzione_ortografica_backup(testo_corretto))
    except AttributeError:
        return str(risposta)
    except Exception as e:
        return f"Errore durante l'analisi: {str(e)}"

# =========================================================
#  6. MAIN LOOP
# =========================================================

def main():                                        
    modello = "llama3.2:3b-instruct-q4_0"            #contiene 3 miliardi di parametri, quantizzato 4bit
    print(f"\nModello utilizzato: {modello}\n")

    try:
        database = carica_database()
    except Exception as e:
        print("Errore nel caricare il database:", e)
        return

    print("=== Chatbot Ispettore Testi ===")
    print("Inserisci un testo da analizzare.")         #viene richiesto un testo da inviare al modello
    print("Digita 'exit' per terminare.\n")            #se l'utente scrive 'exit', si esce del programma

    while True:
        try:
            testo = input("\nTesto:\n> ").strip()
        except KeyboardInterrupt:
            print("\nUscita dal programma.")
            break

        if testo.lower() == "exit":
            print("Chiusura...")
            break

        if len(testo) == 0:
            print("Inserisci un testo valido.")
            continue

        print("\nAnalisi e correzione in corso...\n")

        risultato = analizza_testo(modello, testo, database)
        print("\nRisultato:")
        print("----------------------------------")
        print(risultato)
        print("----------------------------------")

# =========================================================
#  7. AVVIO SCRIPT
# =========================================================

if __name__ == "__main__":
    main()
