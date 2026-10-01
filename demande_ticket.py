import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os

# Importation pour gérer les images
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Importation de votre module d'analyse
try:
    import categorie
except ImportError:
    categorie = None

try:
    from integration_ticket import process_ticket_complete
    from rag_module_5 import load_documents, build_chunks, KnowledgeBase
    INTEGRATION_AVAILABLE = True
except ImportError:
    INTEGRATION_AVAILABLE = False

try:
    from chatbot import ChatbotWindow
except ImportError:
    ChatbotWindow = None

class MaintenanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Demande tickets")
        self.root.geometry("950x780")
        self.root.configure(bg="#E8F5E9")
        
        # =====================================================================
        # INITIALISATION DE LA KB POUR L'INTÉGRATION
        # =====================================================================
        self.kb = None
        self.ticket_counter = 0
        
        if INTEGRATION_AVAILABLE:
            try:
                print("Initialisation de la Knowledge Base...")
                docs = load_documents("./knowledge_base")
                chunks = build_chunks(docs)
                self.kb = KnowledgeBase()
                self.kb.index_chunks(chunks)
                print("Knowledge Base chargée avec succès !")
            except Exception as e:
                print(f"Erreur lors du chargement de la KB : {e}")
                messagebox.showwarning(
                    "Avertissement",
                    f"La Knowledge Base n'a pas pu être chargée.\nL'interface continuera avec categorie.py uniquement.\nErreur: {e}"
                )

        # Style général ttk
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("TLabel", background="#FFFFFF", foreground="#2E7D32", font=("Arial", 10))
        style.configure("Header.TLabel", background="#FFFFFF", foreground="#2E7D32", font=("Arial", 14, "bold"))
        style.configure("TButton", font=("Arial", 10, "bold"), padding=6)
        
        # --- EN-TÊTE AVEC LOGO ---
        header_frame = tk.Frame(root, bg="#FFFFFF", bd=1, relief="solid")
        header_frame.pack(fill="x", padx=20, pady=15)

        # Chargement et affichage du logo depuis dossierIMG/logo_ispm.png
        logo_path = os.path.join("IMG", "logo_ispm.png")
        self.logo_img = None
        
        if PIL_AVAILABLE and os.path.exists(logo_path):
            try:
                img = Image.open(logo_path)
                img = img.resize((50, 50), Image.Resampling.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(img)
                logo_label = tk.Label(header_frame, image=self.logo_img, bg="#FFFFFF")
                logo_label.pack(side="left", padx=(15, 5), pady=10)
            except Exception as e:
                print(f"Erreur de chargement du logo : {e}")

        # Titre à côté du logo
        title_label = tk.Label(header_frame, text="mAIntenance & Assistance", font=("Arial", 16, "bold"), fg="#2E7D32", bg="#FFFFFF")
        title_label.pack(side="left", padx=10, pady=15)
        
        badge_label = tk.Label(header_frame, text=" Système Actif ", font=("Arial", 9, "bold"), fg="#2E7D32", bg="#C8E6C9", padx=8, pady=4)
        badge_label.pack(side="right", padx=15)

        # --- FORMULAIRE DE TICKET ---
        form_frame = tk.Frame(root, bg="#FFFFFF", padx=20, pady=20, bd=1, relief="solid")
        form_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(form_frame, text="Créer un nouveau ticket d'incident", font=("Arial", 12, "bold"), fg="#2E7D32", bg="#FFFFFF").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        # ID Utilisateur
        tk.Label(form_frame, text="ID Utilisateur :", bg="#FFFFFF", fg="#333333").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_id = tk.Entry(form_frame, width=25, font=("Arial", 10), bd=1, relief="solid")
        self.entry_id.grid(row=1, column=1, sticky="w", pady=5, padx=10)

        # Nom & Prénoms
        tk.Label(form_frame, text="Nom & Prénoms :", bg="#FFFFFF", fg="#333333").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_name = tk.Entry(form_frame, width=35, font=("Arial", 10), bd=1, relief="solid")
        self.entry_name.grid(row=2, column=1, sticky="w", pady=5, padx=10)

        # Département
        tk.Label(form_frame, text="Département :", bg="#FFFFFF", fg="#333333").grid(row=3, column=0, sticky="w", pady=5)
        self.combo_dept = ttk.Combobox(form_frame, values=["Marketing", "Communication", "Ressources Humaines", "IT / Technique", "Infrastructure", "Direction"], width=33, state="readonly")
        self.combo_dept.grid(row=3, column=1, sticky="w", pady=5, padx=10)

        # Poste
        tk.Label(form_frame, text="Poste occupé :", bg="#FFFFFF", fg="#333333").grid(row=4, column=0, sticky="w", pady=5)
        self.entry_poste = tk.Entry(form_frame, width=35, font=("Arial", 10), bd=1, relief="solid")
        self.entry_poste.grid(row=4, column=1, sticky="w", pady=5, padx=10)

        # Message / Description
        tk.Label(form_frame, text="Message / Problème :", bg="#FFFFFF", fg="#333333").grid(row=5, column=0, sticky="nw", pady=5)
        self.text_message = tk.Text(form_frame, width=40, height=4, font=("Arial", 10), bd=1, relief="solid")
        self.text_message.grid(row=5, column=1, sticky="w", pady=5, padx=10)

        # Boutons (Envoyer / Annuler)
        btn_frame = tk.Frame(form_frame, bg="#FFFFFF")
        btn_frame.grid(row=6, column=1, sticky="e", pady=(15, 0))

        btn_annuler = tk.Button(btn_frame, text="Annuler", command=self.clear_form, bg="#E0E0E0", fg="#333333", relief="flat", padx=10, pady=5)
        btn_annuler.pack(side="left", padx=5)

        btn_envoyer = tk.Button(btn_frame, text="Envoyer le ticket", command=self.submit_ticket, bg="#4CAF50", fg="#FFFFFF", relief="flat", padx=10, pady=5)
        btn_envoyer.pack(side="left", padx=5)

        # --- TABLEAU DE SUIVI DES TICKETS ---
        table_frame = tk.Frame(root, bg="#FFFFFF", padx=15, pady=15, bd=1, relief="solid")
        table_frame.pack(fill="both", expand=True, padx=20, pady=15)

        lbl_suivi = tk.Label(table_frame, text="Mes tickets (Double-cliquez pour ouvrir le Chatbot d'analyse)", font=("Arial", 12, "bold"), fg="#2E7D32", bg="#FFFFFF")
        lbl_suivi.pack(anchor="w", pady=(0, 10))

        # Configuration du Treeview avec colonnes adaptées aux textes multiples
        columns = ("ID", "Catégorie", "Équipe", "Priorité", "Équipement", "Statut")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=5)
        
        self.tree.heading("ID", text="ID Ticket")
        self.tree.heading("Catégorie", text="Catégorie(s)")
        self.tree.heading("Équipe", text="Équipe assignée")
        self.tree.heading("Priorité", text="Priorité")
        self.tree.heading("Équipement", text="Équipement(s)")
        self.tree.heading("Statut", text="Statut")

        self.tree.column("ID", width=80, anchor="center")
        self.tree.column("Catégorie", width=180, anchor="w")
        self.tree.column("Équipe", width=120, anchor="w")
        self.tree.column("Priorité", width=90, anchor="center")
        self.tree.column("Équipement", width=130, anchor="w")
        self.tree.column("Statut", width=90, anchor="center")

        self.tree.pack(fill="both", expand=True)

        # Liaison du double-clic pour ouvrir le chatbot
        self.tree.bind("<Double-1>", self.open_chatbot)

        # Exemple initial
        self.tree.insert("", "end", values=("#TICK-892", "Matériel informatique", "IT", "moyenne", "souris", "Stand-by"))

    def submit_ticket(self):
        user_id = self.entry_id.get().strip()
        name = self.entry_name.get().strip()
        dept = self.combo_dept.get().strip()
        poste = self.entry_poste.get().strip()
        message = self.text_message.get("1.0", tk.END).strip()

        if not user_id or not name or not dept or not poste or not message:
            messagebox.showwarning("Champs manquants", "Veuillez remplir tous les champs du formulaire.")
            return

        self.ticket_counter += 1
        ticket_id = f"#TICK-{self.ticket_counter:03d}"
        
        # Valeurs par défaut
        categorie_nom = "Autre ou indéterminé"
        equipe = "Support Technique"
        priorite = "faible"
        equipement = "Non identifié"
        statut = "En cours"
        
        # =====================================================================
        # TRAITEMENT AVEC PIPELINE COMPLET (integration_ticket.py)
        # =====================================================================
        if INTEGRATION_AVAILABLE and self.kb is not None:
            try:
                print(f"\n--- Traitement ticket {ticket_id} ---")
                result = process_ticket_complete(message, ticket_id, self.kb)
                
                # Extraction depuis le résultat fusionné
                categorie_nom = result["classification"]["categories_detectees"]
                equipe = result["classification"]["equipe_assignee"]
                priorite = result["classification"]["priorite"]
                equipement = result["diagnostic"]["equipement"]
                
                # Stockage du résultat complet pour utilisation ultérieure (chatbot)
                self.last_ticket_result = result
                
                print(f"[SUCCESS] Ticket analysé via pipeline complet")
                print(f"  Catégorie: {categorie_nom}")
                print(f"  Équipe: {equipe}")
                print(f"  Priorité: {priorite}")
                
            except Exception as e:
                print(f"Erreur lors du traitement par integration_ticket : {e}")
                # Fallback sur categorie.py
                if categorie:
                    try:
                        json_result_str = categorie.process_ticket(message)
                        analysis = json.loads(json_result_str)
                        
                        categorie_nom = analysis.get("categorie", categorie_nom)
                        equipe = analysis.get("equipe_assignee", equipe)
                        priorite = analysis.get("priorite", priorite)
                        
                        diagnostic = analysis.get("diagnostic_extrait", {})
                        equipement = diagnostic.get("equipement", "Non identifié")
                        
                        self.last_ticket_result = analysis
                        
                    except Exception as e2:
                        print(f"Erreur fallback categorie : {e2}")
        
        # =====================================================================
        # FALLBACK : TRAITEMENT AVEC categorie.py UNIQUEMENT
        # =====================================================================
        elif categorie:
            try:
                json_result_str = categorie.process_ticket(message)
                analysis = json.loads(json_result_str)
                
                categorie_nom = analysis.get("categorie", categorie_nom)
                equipe = analysis.get("equipe_assignee", equipe)
                priorite = analysis.get("priorite", priorite)
                
                diagnostic = analysis.get("diagnostic_extrait", {})
                equipement = diagnostic.get("equipement", "Non identifié")
                
                self.last_ticket_result = analysis
                
            except Exception as e:
                print(f"Erreur lors de l'analyse du module categorie : {e}")
                self.last_ticket_result = None

        # Insertion dans le tableau avec les multiples catégories et équipements
        self.tree.insert("", 0, values=(ticket_id, categorie_nom, equipe, priorite, equipement, statut))

        messagebox.showinfo("Succès", f"Ticket {ticket_id} analysé avec succès !")
        self.clear_form()

    def open_chatbot(self, event):
        """Ouvre le chatbot lié au ticket sélectionné via un double-clic"""
        selected_item = self.tree.selection()
        if not selected_item:
            return
        
        values = self.tree.item(selected_item, "values")
        ticket_id = values[0]
        message = f"Problème global sur équipements : {values[4]} (Catégories : {values[1]})"

        if ChatbotWindow is None:
            messagebox.showerror("Erreur", "Le fichier chatbot.py est introuvable ou mal importé.")
            return

        missing_info = [
            "À quel moment précis l'incident est-il apparu ?",
            "Avez-vous déjà effectué des manipulations ?"
        ]
        
        # Essayer d'extraire les infos manquantes depuis le dernier résultat
        if hasattr(self, 'last_ticket_result') and self.last_ticket_result:
            try:
                # Si c'est un résultat d'integration_ticket (avec "diagnostic")
                if isinstance(self.last_ticket_result, dict) and "diagnostic" in self.last_ticket_result:
                    missing_info = self.last_ticket_result["diagnostic"].get("informations_manquantes", missing_info)
                # Sinon si c'est un résultat de categorie.py (avec "informations_manquantes")
                elif isinstance(self.last_ticket_result, dict) and "informations_manquantes" in self.last_ticket_result:
                    missing_info = self.last_ticket_result.get("informations_manquantes", missing_info)
            except:
                pass

        ChatbotWindow(self.root, ticket_id, message, missing_info)

    def clear_form(self):
        self.entry_id.delete(0, tk.END)
        self.entry_name.delete(0, tk.END)
        self.combo_dept.set('')
        self.entry_poste.delete(0, tk.END)
        self.text_message.delete("1.0", tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = MaintenanceApp(root)
    root.mainloop()