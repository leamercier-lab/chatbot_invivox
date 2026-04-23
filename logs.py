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

        # Préparation de la donnée
        new_log = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "question": question,
            "results_returned": ", ".join([str(res['name']) for res in results]) if results else "Aucun résultat"
        }
        new_df = pd.DataFrame([new_log])

        try:
            # 1. On récupère le fichier existant
            contents = repo.get_contents("logs_questions.csv")
            old_df = pd.read_csv(io.StringIO(contents.decoded_content.decode('utf-8')))
            updated_df = pd.concat([old_df, new_df], ignore_index=True)

            # 2. On met à jour
            repo.update_file(
                contents.path,
                f"Log: nouvelle question - {new_log['timestamp']}",
                updated_df.to_csv(index=False),
                contents.sha
            )
        except:
            # Si le fichier n'existe pas encore, on le crée
            repo.create_file(
                "logs_questions.csv",
                "Initialisation des logs",
                new_df.to_csv(index=False)
            )
    except Exception as e:
        print(f"Erreur lors du logging : {e}")