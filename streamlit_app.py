import streamlit as st
from mistralai import Mistral # On utilise le SDK Mistral

from logs import log_to_github
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
    if prompt := st.chat_input("Ex: Chirurgie du genou"):

        # 1. Affichage du message utilisateur
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Logique Assistant
        with st.chat_message("assistant"):
            # --- ÉTAPE RECHERCHE ---
            with st.spinner("Recherche dans le catalogue..."):
                results = search(prompt)
                log_to_github(prompt, results)
            if results:
                response_text = "Voici les formations pertinentes que j'ai trouvées :\n\n"
                for res in results:
                    # Nettoyage du nom pour éviter les bugs de formatage
                    name = str(res['name']).strip()
                    unique_id = res.get('unique_id', '')
                    score = res['score']
                    url = f"https://invivox.com/fr/training/detail/{unique_id}"
                    
                    # Construction d'une ligne propre
                    # Le \n assure que chaque élément est bien traité comme un nouveau point de liste
                    response_text += f"### {name}\n" # Titre en plus gros
                    response_text += f"🎯 **Score : {score}%** \n" # Deux espaces à la fin pour le saut de ligne
                    response_text += f"🔗 [Consulter le programme]({url})\n\n"
                    response_text += "---\n" # Une petite ligne de séparation
            else:
                response_text = "Désolé, je n'ai pas trouvé de formation correspondant à votre recherche."

            # --- ÉTAPE STREAMING (Optionnel avec texte fixe) ---
            # Pour faire un effet "IA", on l'affiche simplement
            st.markdown(response_text)
            
        # Sauvegarde dans l'historique
        st.session_state.messages.append({"role": "assistant", "content": response_text})
