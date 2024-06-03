import tkinter as tk
from tkinter import ttk,messagebox
import json
import socket
import time

class LetnjaLigaApp:
    def __init__(self,root):
        self.root = root
        self.root.title("Turnir u malom fudbalu")
        self.teams = self.load_teams()
        self.create_main_widgets()
    def load_teams(self):
        with open('timovi.json','r') as file:
            return json.load(file)
    
    def create_main_widgets(self):
        self.match_button = tk.Button(self.root,width=30,pady=10,text="Utakmica",command=self.start_match)
        self.match_button.pack(pady=20)

        self.add_team_button = tk.Button(self.root,width=30,pady=10,text="Dodaj ekipu", command = self.add_team)
        self.add_team_button.pack(pady=20)

        self.add_player_button = tk.Button(self.root,width=30,pady=10,text="Dodaj igraca",command = self.add_player)
        self.add_player_button.pack(pady=20)

        self.results_button = tk.Button(self.root,width=30,pady=10,text="Rezulati",command = self.show_results)
        self.results_button.pack(pady=20)

        self.exit_button = tk.Button(self.root,width=30,pady=10,text="Izlaz",command = self.root.quit)
        self.exit_button.pack(pady=20)

    def start_match(self):
        match_window = tk.Toplevel(self.root)
        match_window.title("Utakmica")
        match_window.geometry("300x600")
        
        self.team1_label = tk.Label(match_window,text="Tim 1")
        self.team1_label.pack()
        
        self.team1_select = ttk.Combobox(match_window,values=list(self.teams.keys()))
        self.team1_select.pack()
        self.team1_select.bind("<<ComboboxSelected>>",lambda _:self.load_players(match_window,self.team1_select,self.team1_players))
        
        self.team1_players = tk.Listbox(match_window)
        self.team1_players.pack()

        self.team2_label = tk.Label(match_window,text="Tim 2")
        self.team2_label.pack()
        
        self.team2_select = ttk.Combobox(match_window,values=list(self.teams.keys()))
        self.team2_select.pack()
        self.team2_select.bind("<<ComboboxSelected>>",lambda _:self.load_players(match_window,self.team2_select,self.team2_players))
        
        self.team2_players = tk.Listbox(match_window)
        self.team2_players.pack()

        self.team1_score = 0
        self.team2_score = 0
        
        self.team1_score_label = tk.Label(match_window,text="0")
        self.team1_score_label.pack()

        self.team2_score_label = tk.Label(match_window,text="0")
        self.team2_score_label.pack()

        self.goal_button = tk.Button(match_window,width=30,pady=10,text="Gol",command = lambda:self.add_goal())
        self.goal_button.pack()

        self.end_match_button = tk.Button(match_window,width=30,pady=10,text="Kraj utakmice",command = lambda: self.end_match(match_window))
        self.end_match_button.pack()

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
            print(f"Igrac {selected_player} je postigao gol za ekipu 1")
            self.add_scorer(selected_player)
        elif selected_team2:
            self.team2_score +=1
            self.team2_score_label.config(text=f"{self.team2_score}")
            selected_player = self.team2_players.get(selected_team2)
            print(f"Igrac {selected_player} je postigao gol za ekipu 2")
            self.add_scorer(selected_player)
        else:
            messagebox.showerror("Greska","Morate izabrati igraca koji je postigao gol")
    
    def add_scorer(self,player):
        try:
            with open('strelci.json','r') as file:
                scorers = json.load(file)
        except FileNotFoundError:
                scorers = []
            
        player_found = False
        for scorer in scorers:
            if scorer['ime'] == player:
                scorer['brojGolova']+=1
                player_found = True
                break
        
        if player_found == False:
            scorers.append({"ime":player,"brojGolova":1})
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
            self.send_match_data(match_data)
            match_window.destroy()

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
        add_team_window.geometry("300x300")
        
        tk.Label(add_team_window,text="Naziv ekipe: ").pack()
        
        team_name_entry = tk.Entry(add_team_window)
        team_name_entry.pack()
        tk.Button(add_team_window,text="Dodaj",command= lambda : self.save_team(add_team_window,team_name_entry)).pack()

    def save_team(self,add_team_window,team_name_entry):
        team_name = team_name_entry.get()
        if team_name and team_name not in self.teams:
            self.teams[team_name] = []
            self.save_teams()
            messagebox.showinfo("Uspeh","Tim uspesno dodat!")
            add_team_window.destroy()
        else:
            messagebox.showerror("Greska","Neispravan naziv ekipe ili ekipa vec postoji")
    
        
    def add_player(self):
        add_player_window = tk.Toplevel(self.root)
        add_player_window.title("Dodaj igraca")
        add_player_window.geometry("300x300")
        
        tk.Label(add_player_window,text="Naziv ekipe:").pack()
        team_select = ttk.Combobox(add_player_window,values = list(self.teams.keys()))
        team_select.pack()
        
        tk.Label(add_player_window,text="Ime i prezime igraca:").pack()
        player_name_entry=tk.Entry(add_player_window)
        player_name_entry.pack()
        tk.Button(add_player_window,text="Dodaj",command=lambda: self.save_player(add_player_window,team_select,player_name_entry)).pack()


    def save_player(self,add_player_window,team_select,player_name_entry):
        team_name = team_select.get()
        player_name = player_name_entry.get()
        if team_name and player_name:
            self.teams[team_name].append(player_name)
            self.save_teams()
            messagebox.showinfo("Uspeh","Igrac uspesno dodat")
        else:
            messagebox.showerror("Greska","Neispravan naziv ekipe ili ime igraca")
        
    def show_results(self):
        results_window = tk.Toplevel(self.root)
        results_window.title("Rezultati")
        results_text = tk.Text(results_window)
        results_text.pack()
        req = {'action':'get_games'}
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
            s.connect(('localhost',8001))
            s.sendall(json.dumps(req).encode('utf-8'))
            response = s.recv(4096).decode('utf-8')
            games = json.loads(response)
            for game in games:
                results_text.insert(tk.END,f"Datum : {game[1]}, Vreme : {game[2]}, {game[3]} {game[5]} {game[4]}\n")
        results_text.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("300x400")
    app = LetnjaLigaApp(root)
    root.mainloop()


        
        

                

