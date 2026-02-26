import streamlit as st
from mistralai import Mistral # On utilise le SDK Mistral
from search_test import search

st.title("🩺 Assistant Invivox")
st.write("Posez vos questions cliniques pour trouver la meilleure formation.")

# Récupération de la clé API dans les Secrets (Settings sur Streamlit Cloud)
mistral_api_key = st.secrets["MISTRAL_API_KEY"]

if not mistral_api_key:
    st.info("Clé API manquante dans les secrets.", icon="🗝️")
else:
    # Initialisation du client Mistral
    client = Mistral(api_key=mistral_api_key)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Affichage de l'historique
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Champ de saisie
    if prompt := st.chat_input("Ex: Chirurgie du genou LCA"):

        # 1. Affichage du message utilisateur
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Logique Assistant
        with st.chat_message("assistant"):
            # --- ÉTAPE RECHERCHE ---
            with st.spinner("Recherche dans le catalogue..."):
                results = search(prompt)
            
            if results:
                # On prépare un texte de réponse avec les résultats
                response_text = "Voici les formations pertinentes que j'ai trouvées :\n\n"
                for res in results:
                    unique_id = res.get('unique_id', '')
                    url = f"https://invivox.com/fr/training/detail/{unique_id}"
                    response_text += f"- **{res['name']}** (Score: {res['score']}%)\n  [Voir la formation]({url})\n\n"
            else:
                response_text = "Désolé, je n'ai pas trouvé de formation correspondant à votre recherche."

            # --- ÉTAPE STREAMING (Optionnel avec texte fixe) ---
            # Pour faire un effet "IA", on l'affiche simplement
            st.markdown(response_text)
            
        # Sauvegarde dans l'historique
        st.session_state.messages.append({"role": "assistant", "content": response_text})
