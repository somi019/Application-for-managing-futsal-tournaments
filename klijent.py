import tkinter as tk
from tkinter import ttk,messagebox
import json
import socket
import time
import os
from functools import reduce

class LetnjaLigaApp:
    def __init__(self,root):
        self.root = root
        self.teams = self.load_teams()
        self.center_window(root,400,500)
        self.create_main_widgets()
        
    def load_teams(self):
        with open('timovi.json','r') as file:
            return json.load(file)
        
    def center_window(self,window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_main_widgets(self):
        self.root.title("Letnja Liga - Glavni Meni")
        self.root.configure(bg="#2c3e50")

        title_label = tk.Label(self.root, text="Letnja Liga", font=("Helvetica", 24, "bold"), bg="#2c3e50", fg="white")
        title_label.pack(pady=20)

        button_style = {
            "width": 30,
            "pady": 10,
            "font": ("Helvetica", 12),
            "bg": "#1abc9c",
            "fg": "white",
            "activebackground": "#16a085",
            "activeforeground": "white",
            "bd": 0,
            "highlightthickness": 0
        }

        self.match_button = tk.Button(self.root, text="Utakmica", command=self.start_match, **button_style)
        self.match_button.pack(pady=10)

        self.add_team_button = tk.Button(self.root, text="Dodaj ekipu", command=self.add_team, **button_style)
        self.add_team_button.pack(pady=10)

        self.add_player_button = tk.Button(self.root, text="Dodaj igrača", command=self.add_player, **button_style)
        self.add_player_button.pack(pady=10)

        self.results_button = tk.Button(self.root, text="Rezultati", command=self.show_results, **button_style)
        self.results_button.pack(pady=10)

        self.stats_button = tk.Button(self.root, text="Statistika", command=self.show_stats, **button_style)
        self.stats_button.pack(pady=20)

        self.exit_button = tk.Button(self.root, text="Izlaz", command=self.root.quit, **button_style)
        self.exit_button.pack(pady=10)


    def start_match(self):
        match_window = tk.Toplevel(self.root)
        match_window.title("Utakmica")
        self.center_window(match_window,450, 800)
        match_window.configure(bg="#34495e")

        self.root.withdraw()
        match_window.protocol("WM_DELETE_WINDOW", lambda: self.on_window_close(match_window))

        label_style = {"bg": "#34495e", "fg": "white", "font": ("Helvetica", 14)}

        self.team1_label = tk.Label(match_window, text="Tim 1", **label_style)
        self.team1_label.grid(row=0, column=0, padx=20, pady=5, sticky='w')
        
        self.team1_select = ttk.Combobox(match_window, values=list(self.teams.keys()))
        self.team1_select.grid(row=1, column=0, padx=20, pady=5, sticky='w')
        self.team1_select.bind("<<ComboboxSelected>>", lambda _: self.load_players(match_window, self.team1_select, self.team1_players))
        
        self.team1_players = tk.Listbox(match_window, bg="#ecf0f1", fg="#2c3e50", font=("Helvetica", 12), height=15)
        self.team1_players.grid(row=2, column=0, padx=20, pady=5, sticky='w')

        self.team2_label = tk.Label(match_window, text="Tim 2", **label_style)
        self.team2_label.grid(row=0, column=1, padx=20, pady=5, sticky='e')
        
        self.team2_select = ttk.Combobox(match_window, values=list(self.teams.keys()))
        self.team2_select.grid(row=1, column=1, padx=20, pady=5, sticky='e')
        self.team2_select.bind("<<ComboboxSelected>>", lambda _: self.load_players(match_window, self.team2_select, self.team2_players))
        
        self.team2_players = tk.Listbox(match_window, bg="#ecf0f1", fg="#2c3e50", font=("Helvetica", 12), height=15)
        self.team2_players.grid(row=2, column=1, padx=20, pady=5, sticky='e')

        self.team1_score = 0
        self.team2_score = 0

        score_frame = tk.Frame(match_window, bg="#34495e")
        score_frame.grid(row=3, column=0, columnspan=2, pady=10)

        self.team1_score_label = tk.Label(score_frame, text="0", font=("Arial", 30), bg="#34495e", fg="white")
        self.team1_score_label.pack(side=tk.LEFT, padx=5)

        self.colon_label = tk.Label(score_frame, text=":", font=("Arial", 30), bg="#34495e", fg="white")
        self.colon_label.pack(side=tk.LEFT, padx=5)

        self.team2_score_label = tk.Label(score_frame, text="0", font=("Arial", 30), bg="#34495e", fg="white")
        self.team2_score_label.pack(side=tk.LEFT, padx=5)
        
        self.strelciUtakmice = {}

        button_style = {
            "width": 30,
            "pady": 10,
            "font": ("Helvetica", 12),
            "bg": "#1abc9c",
            "fg": "white",
            "activebackground": "#16a085",
            "activeforeground": "white",
            "bd": 0,
            "highlightthickness": 0
        }

        self.start_button = tk.Button(match_window, text="Započni utakmicu", command=lambda: self.start_game(), **button_style)
        self.start_button.grid(row=4, column=0, columnspan=2, pady=10)

        self.goal_button = tk.Button(match_window, text="Gol", state="disabled", command=lambda: self.add_goal(), **button_style)
        self.goal_button.grid(row=5, column=0, columnspan=2, pady=10)

        self.end_match_button = tk.Button(match_window, text="Kraj utakmice", state="disabled", command=lambda: self.end_match(match_window), **button_style)
        self.end_match_button.grid(row=6, column=0, columnspan=2, pady=10)

    def on_window_close(self,window):
        self.root.deiconify()
        window.destroy()
    
    def start_game(self):
        if self.team1_select.get() and self.team2_select.get():
            self.start_button.config(state=tk.DISABLED)
            self.goal_button.config(state=tk.NORMAL)
            self.end_match_button.config(state=tk.NORMAL)
            self.team1_select.config(state=tk.DISABLED)
            self.team2_select.config(state=tk.DISABLED)
        else:
            messagebox.showerror("Greška", "Morate izabrati oba tima pre početka utakmice.")


    def load_players(self,window,select,listbox):
        team = select.get()
        listbox.delete(0,tk.END)
        for player in self.teams[team]:
            listbox.insert(tk.END,player)
    def add_goal(self):
        selected_team1 = self.team1_players.curselection()
        selected_team2 = self.team2_players.curselection()

        if selected_team1:
            self.team1_score +=1
            self.team1_score_label.config(text=f"{self.team1_score}")
            selected_player = self.team1_players.get(selected_team1)

            if selected_player in self.strelciUtakmice:
                self.strelciUtakmice[selected_player] += 1
            else:
                self.strelciUtakmice[selected_player] = 1
        elif selected_team2:
            self.team2_score +=1
            self.team2_score_label.config(text=f"{self.team2_score}")
            selected_player = self.team2_players.get(selected_team2)

            if selected_player in self.strelciUtakmice:
                self.strelciUtakmice[selected_player] += 1
            else:
                self.strelciUtakmice[selected_player] = 1
        else:
            messagebox.showerror("Greska","Morate izabrati igraca koji je postigao gol")

    def add_scorers(self,match_scorers):
        try:
            with open('strelci.json','r') as file:
                scorers = json.load(file)
        except FileNotFoundError:
                scorers = []
            
        for player in match_scorers:
            player_found = False
            for scorer in scorers:
                if scorer['ime'] == player:
                    scorer['brojGolova']+=match_scorers[player]
                    player_found = True
                    break   
            if player_found == False:
                scorers.append({"ime":player,"brojGolova":match_scorers[player]})
        
        with open("strelci.json",'w') as file:
            json.dump(scorers,file)


    def end_match(self,match_window):
        if messagebox.askyesno("Kraj utakmice?","Da li ste sigurni?"):
            current_time = time.strftime("%d.%m.%Y %H:%M:%S")
            datum = current_time.split(" ")[0]
            vreme = current_time.split(" ")[1]
            match_data = {
                "datum" : datum,
                "vreme" : vreme,
                "tim1" : self.team1_select.get(),
                "tim2" : self.team2_select.get(),
                "rezultat" : f"{self.team1_score} : {self.team2_score}"
            }
            self.add_scorers(self.strelciUtakmice)
            self.send_match_data(match_data)
            self.log_match(match_data)
            self.on_window_close(match_window)

    def send_match_data(self,match_data):
        req = {'action':'add_game','data':match_data}
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
            s.connect(('localhost',8001))
            s.sendall(json.dumps(req).encode('utf-8'))
    
    def save_teams(self):
        with open('timovi.json','w') as file:
            json.dump(self.teams,file)
    
    def add_team(self):
        add_team_window = tk.Toplevel(self.root)
        add_team_window.title("Dodaj ekipu")
        self.center_window(add_team_window, 400, 500)
        add_team_window.configure(bg="#34495e")
        self.root.withdraw()
        add_team_window.protocol("WM_DELETE_WINDOW", lambda: self.on_window_close(add_team_window))

        label_style = {"bg": "#34495e", "fg": "white", "font": ("Helvetica", 14)}

        tk.Label(add_team_window, text="Naziv ekipe:", **label_style).grid(row=0, column=0, padx=10, pady=10, sticky="w")

        team_name_entry = tk.Entry(add_team_window, bg="#ecf0f1", fg="#2c3e50", font=("Helvetica", 12))
        team_name_entry.grid(row=0, column=1, padx=10, pady=10, sticky="e")

        button_frame = tk.Frame(add_team_window, bg="#34495e")
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)

        button_style = {
            "font": ("Helvetica", 12),
            "bg": "#1abc9c",
            "fg": "white",
            "activebackground": "#16a085",
            "activeforeground": "white",
            "bd": 0,
            "highlightthickness": 0,
            "width": 15
        }

        tk.Button(button_frame, text="Dodaj", command=lambda: self.save_team(team_name_entry,teamsList), **button_style).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Obrisi", command=lambda: self.delete_team(teamsList), **button_style).grid(row=0, column=1, padx=5)

        teamsList = tk.Listbox(add_team_window, bg="#ecf0f1", fg="#2c3e50", font=("Helvetica", 12), height=16)
        teamsList.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="we")
        for team in self.teams.keys():
            teamsList.insert(tk.END, team)

    def delete_team(self,teamsList):
        selected_team_index = teamsList.curselection()
        if selected_team_index:
            selected_team = teamsList.get(selected_team_index)
            del self.teams[selected_team]
            self.save_teams()
            teamsList.delete(selected_team_index)
        else:
            messagebox.showerror("Greska","Niste izabrali tim za brisanje!")

    def save_team(self,team_name_entry,teamsList):
        team_name = team_name_entry.get()
        if team_name and team_name not in self.teams:
            self.teams[team_name] = []
            self.save_teams()
            teamsList.insert(tk.END,team_name)
            team_name_entry.delete(0,tk.END)
        else:
            messagebox.showerror("Greska","Neispravan naziv ekipe ili ekipa vec postoji")
    
        
    def add_player(self):
        add_player_window = tk.Toplevel(self.root)
        add_player_window.title("Dodaj igrača")
        self.center_window(add_player_window, 450, 600)
        add_player_window.configure(bg="#34495e")
        self.root.withdraw()
        add_player_window.protocol("WM_DELETE_WINDOW", lambda: self.on_window_close(add_player_window))

        label_style = {"bg": "#34495e", "fg": "white", "font": ("Helvetica", 14)}

        tk.Label(add_player_window, text="Naziv ekipe:", **label_style).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        team_select = ttk.Combobox(add_player_window, values=list(self.teams.keys()))
        team_select.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        team_select.bind("<<ComboboxSelected>>", lambda _: self.load_players(add_player_window, team_select, team_players))

        team_players = tk.Listbox(add_player_window, bg="#ecf0f1", fg="#2c3e50", font=("Helvetica", 12), height=15)
        team_players.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="we")

        tk.Label(add_player_window, text="Ime i prezime igrača:", **label_style).grid(row=2, column=0, padx=10, pady=10, sticky="w")
        player_name_entry = tk.Entry(add_player_window, bg="#ecf0f1", fg="#2c3e50", font=("Helvetica", 12))
        player_name_entry.grid(row=2, column=1, padx=10, pady=10, sticky="e")

        button_frame = tk.Frame(add_player_window, bg="#34495e")
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)

        button_style = {
            "font": ("Helvetica", 12),
            "bg": "#1abc9c",
            "fg": "white",
            "activebackground": "#16a085",
            "activeforeground": "white",
            "bd": 0,
            "highlightthickness": 0,
            "width": 15
        }

        tk.Button(button_frame, text="Dodaj", command=lambda: self.save_player(team_players, team_select, player_name_entry), **button_style).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Obriši", command=lambda: self.delete_player(team_players, team_select), **button_style).grid(row=0, column=1, padx=5)

    def save_player(self,team_players,team_select,player_name_entry):
        team_name = team_select.get()
        player_name = player_name_entry.get()
        if team_name and player_name:
            self.teams[team_name].append(player_name)
            self.save_teams()
            team_players.insert(tk.END,player_name)
            player_name_entry.delete(0,tk.END)
        else:
            messagebox.showerror("Greska","Neispravan naziv ekipe ili ime igraca")

    def delete_player(self,team_players,team_select):
        selected_player_index = team_players.curselection()
        team = team_select.get()
        if selected_player_index and team:
            selected_player = team_players.get(selected_player_index)
            self.teams[team].remove(selected_player)
            self.save_teams()
            team_players.delete(selected_player_index)
        else:
            messagebox.showerror("Greska","Ne mozete obrisati igraca ako ih nema u timu")
        
    def show_results(self):
        results_window = tk.Toplevel(self.root)
        results_window.title("Rezultati")
        self.center_window(results_window, 600, 700)
        results_window.configure(bg="#34495e")
        
        results_text = tk.Text(results_window, bg="#ecf0f1", fg="#2c3e50", font=("Helvetica", 15))
        results_text.pack(padx=10, pady=10, fill="both", expand=True)

        req = {'action': 'get_games'}
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost', 8001))
            s.sendall(json.dumps(req).encode('utf-8'))
            response = s.recv(4096).decode('utf-8')
            games = json.loads(response)
            for game in games:
                results_text.insert(tk.END, f"Datum: {game[1]}, Vreme: {game[2]}, {game[3]} {game[5]} {game[4]}\n")

        results_text.config(state="disabled")
        
        button_frame = tk.Frame(results_window, bg="#34495e")
        button_frame.pack(pady=10)

        button_style = {
            "font": ("Helvetica", 12),
            "bg": "#1abc9c",
            "fg": "white",
            "activebackground": "#16a085",
            "activeforeground": "white",
            "bd": 0,
            "highlightthickness": 0,
            "width": 15
        }

        close_button = tk.Button(button_frame, text="Zatvori", command=results_window.destroy, **button_style)
        close_button.pack()

    def show_stats(self):
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Statistika")
        self.center_window(stats_window, 400, 300)
        stats_window.configure(bg="#34495e")

        label_style = {"bg": "#34495e", "fg": "white", "font": ("Helvetica", 14)}
        tk.Label(stats_window, text="Top 3 strelca:", **label_style).pack(pady=10)

        try:
            with open('strelci.json', 'r') as file:
                scorers = json.load(file)
        except FileNotFoundError:
            scorers = []

        if not scorers:
            tk.Label(stats_window, text="Nema podataka o strelcima", **label_style).pack(pady=10)
            return

        sorted_scorers = sorted(scorers, key=lambda x: x['brojGolova'], reverse=True)
        top_scorers = list(filter(lambda x: sorted_scorers.index(x) < 3, sorted_scorers))

        for scorer in top_scorers:
            tk.Label(stats_window, text=f"{scorer['ime']} - {scorer['brojGolova']}", **label_style).pack(pady=5)

        total_goals = reduce(lambda acc, scorer: acc + scorer['brojGolova'], scorers, 0)

        tk.Label(stats_window, text=f"Ukupan broj datih golova na turniru je: {total_goals}", **label_style).pack(pady=10)

        close_button = tk.Button(stats_window, text="Zatvori", command=stats_window.destroy, bg="#1abc9c", fg="white", font=("Helvetica", 12), activebackground="#16a085", activeforeground="white", bd=0, highlightthickness=0, width=15)
        close_button.pack(pady=10)

    def ensure_logs_directory_exists(self):
        if not os.path.exists('utakmice_logs'):
            os.makedirs('utakmice_logs')
    
    def log_match(self,match_data):
        self.ensure_logs_directory_exists()

        log_filename = f"utakmice_logs/{match_data['datum']}_{match_data['vreme'].replace(':','.')}_{match_data['tim1']}-{match_data['tim2']}.txt"
        with open(log_filename,"w") as log_file:
            log_file.write(f"Datum:{match_data['datum']}\n")
            log_file.write(f"Vreme:{match_data['vreme']}\n")
            log_file.write(f"Timovi:{match_data['tim1']} - {match_data['tim2']}\n")
            log_file.write(f"Rezultat:{match_data['rezultat']}\n")
            log_file.write(f"Golovi:\n")
            scorer_strings = map(lambda scorer: f"Igrac: {scorer}, broj golova: {self.strelciUtakmice[scorer]}\n",self.strelciUtakmice)
            log_file.writelines(scorer_strings)

if __name__ == "__main__":

    root = tk.Tk()
    app = LetnjaLigaApp(root)
    root.mainloop()