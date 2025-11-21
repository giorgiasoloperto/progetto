import gradio as gr
from chatbot_ispettore_testi import analizza_testo, carica_database

# Caricamento del database
try:
    database = carica_database()
except Exception as e:
    database = []
    print("Errore nel caricare il database:", e)

MODELLO = "llama3.2:3b-instruct-q4_0"

# Funzione wrapper per Gradio
def esegui_correzione(testo_utente):
    if not testo_utente.strip():
        return "⚠️ Inserisci un testo valido."
    return analizza_testo(MODELLO, testo_utente, database)

# Interfaccia grafica
with gr.Blocks(title="Ispettore Testi – Correttore IA") as demo:

    gr.Markdown(
        """
        # 📝 **Ispettore Testi – Correttore Professionale**
        Inserisci un testo in italiano e il sistema lo correggerà seguendo le tue regole personalizzate
        (punteggiatura, tono, ortografia, RAG).
        """
    )

    with gr.Row():
        input_box = gr.Textbox(
            label="Inserisci il testo da analizzare",
            placeholder="Scrivi qui il testo con errori...",
            lines=6
        )

    bottone = gr.Button("Analizza e Correggi")

    output_box = gr.Markdown(
        label="Risultato",
        value="Il risultato apparirà qui...",
    )

    bottone.click(fn=esegui_correzione, inputs=input_box, outputs=output_box)

# Avvio app
if __name__ == "__main__":
    demo.launch()
