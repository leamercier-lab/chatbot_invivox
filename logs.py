import pandas as pd
from github import Github
from datetime import datetime
import io
import streamlit as st

def log_to_github(question, results):
    try:
        token = st.secrets["GH_TOKEN"]
        repo_name = "leamercier-lab/chatbot_invivox"
        g = Github(token)
        repo = g.get_repo(repo_name)

        # --- LA MODIFICATION EST ICI ---
        # On extrait les unique_id de chaque dictionnaire 'res' dans la liste 'results'
        # On les sépare par un "|" pour ne pas casser le format CSV
        liste_ids = [str(res.get('unique_id', 'id_inconnu')) for res in results]
        ids_string = "|".join(liste_ids)
        # -------------------------------

        new_log = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "question": question.replace(",", " "),  # Sécurité pour le CSV
            "ids_formations": ids_string
        }

        new_df = pd.DataFrame([new_log])

        try:
            # Récupération et mise à jour du fichier existant
            contents = repo.get_contents("logs_questions.csv")
            old_df = pd.read_csv(io.StringIO(contents.decoded_content.decode('utf-8')))
            updated_df = pd.concat([old_df, new_df], ignore_index=True)

            repo.update_file(
                contents.path,
                f"Log: {new_log['timestamp']}",
                updated_df.to_csv(index=False),
                contents.sha
            )
        except:
            # Création si premier log
            repo.create_file("logs_questions.csv", "init logs", new_df.to_csv(index=False))

    except Exception as e:
        print(f"Erreur Log: {e}")