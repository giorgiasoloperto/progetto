# Ispettore Testi – Correttore ortografico intelligente (RAG + LLM + SpellChecker)

Questo progetto implementa un correttore automatico avanzato di testi in italiano, basato su:

- Ollama + Llama 3.2 (o altro modello compatibile)
- RAG (Retrieval Augmented Generation) per recuperare esempi passati come contesto
- SpellChecker per correzioni di backup
- Regole personalizzate per garantire:
  - Correzione completa di tutti gli errori
  - Formattazione controllata
  - Capitalizzazione nomi e frasi
  - Nessuna aggiunta o invenzione di contenuti

L’obiettivo è ottenere un correttore coerente, strutturato e affidabile che restituisce:

1. Elenco degli errori trovati con spiegazione  
2. Versione corretta del testo, pronta all’uso

---

## Funzionalità principali

### 1. RAG — Recupero esempi dal database  
Il file `database_testi.json` contiene una serie di testi “sbagliato → corretto”.  
Il sistema seleziona automaticamente gli esempi più simili al testo dell’utente e li usa come contesto per migliorare la qualità della correzione.

### 2. Prompt di sistema altamente strutturato  
Il modello segue un template rigido che impone:

- individuazione solo di errori reali  
- spiegazione sintetica  
- versione finale senza errori residui  
- rispetto del significato originario  

### 3. SpellChecker di backup  
Interviene quando il modello non corregge parole errate.

### 4. Capitalizzazione intelligente  
Corregge:
- iniziali delle frasi  
- nomi propri comuni (configurabili)

### 5. Interfaccia testuale semplice  
Loop interattivo in cui l’utente inserisce un testo e riceve:
---VERSIONE CORRETTA---
...

---CORREZIONI E SPIEGAZIONI---
...


---

## Requisiti

Assicurati di avere:

- Python 3.9+
- Ollama installato → https://ollama.com/
- Modello Llama compatibile (es. llama3.2:3b-instruct-q4_0)
- Dipendenze Python:

```bash
pip install pyspellchecker ollama


