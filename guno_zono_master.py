
import tkinter as tk
from tkinter import messagebox
import random, json, os, sys

COLORS = ["Red","Green","Blue","Yellow"]
COLOR_HEX = {
    "Red":"#ff4b2b","Green":"#16a085",
    "Blue":"#00c6ff","Yellow":"#f1c40f","Wild":"#2c3e50"
}
WORLD_EVENTS = ["STABLE","GLITCH","GRAVITY SWAP","BLACKOUT","DOUBLE DATA"]
PROFILE_FILE = "zono_master_profile.json"

def play_sound(kind="play"):
    try:
        if sys.platform.startswith("win"):
            import winsound
            tones={"play":(800,120),"draw":(500,200),"win":(1000,400),"lose":(300,400)}
            f,d=tones.get(kind,(700,150))
            winsound.Beep(f,d)
    except: pass

class Card:
    def __init__(self,color,value):
        self.color=color; self.value=value
    def playable(self,top):
        return self.color==top.color or self.value==top.value or self.color=="Wild"

class GunoZonoMaster:
    def __init__(self,root):
        self.root=root
        self.root.title("GUNO ZONO : HORIZON PROTOCOL – MASTER")
        self.root.geometry("1400x900")
        self.root.configure(bg="#050505")

        self.profile=self.load_profile()
        self.deck=self.create_deck()
        self.turn=0; self.direction=1; self.draw_stack=0
        self.event_counter=0; self.active_event="STABLE"

        self.players=[
            {"name":"ALPHA (YOU)","hand":[],"human":True,"ai":None},
            {"name":"BETA-7","hand":[],"human":False,"ai":"normal"},
            {"name":"ZERO-X (BOSS)" if self.profile["wins"]>=10 else "GAMMA-9","hand":[],"human":False,"ai":"boss"},
            {"name":"DELTA-2","hand":[],"human":False,"ai":"normal"}
        ]

        for p in self.players:
            p["hand"]=[self.draw_card() for _ in range(7)]

        self.top_card=self.draw_card()
        while self.top_card.color=="Wild":
            self.top_card=self.draw_card()

        self.build_ui()
        self.refresh_ui()

    def load_profile(self):
        if not os.path.exists(PROFILE_FILE):
            return {"wins":0,"credits":500,"xp":0,"level":1}
        return json.load(open(PROFILE_FILE))

    def save_profile(self):
        json.dump(self.profile,open(PROFILE_FILE,"w"),indent=2)

    def create_deck(self):
        deck=[]
        for c in COLORS:
            for i in range(10): deck.append(Card(c,i))
            for s in ["Skip","Reverse","Draw3"]:
                deck+=[Card(c,s),Card(c,s)]
        for _ in range(6):
            deck+=[Card("Wild","Wild"),Card("Wild","WildDraw5")]
        random.shuffle(deck)
        return deck

    def draw_card(self):
        if not self.deck: self.deck=self.create_deck()
        return self.deck.pop()

    def build_ui(self):
        self.center=tk.Canvas(self.root,width=160,height=230,bg="#000",highlightthickness=2)
        self.center.place(x=620,y=280)
        self.event_lbl=tk.Label(self.root,fg="#f9d423",bg="#050505",font=("Impact",18))
        self.event_lbl.place(x=550,y=520)
        self.stats=tk.Label(self.root,fg="#00d2ff",bg="#050505",font=("Consolas",11,"bold"))
        self.stats.place(x=20,y=20)
        self.hand_frame=tk.Frame(self.root,bg="#050505")
        self.hand_frame.place(x=100,y=700,width=1200,height=150)

        self.bot_labels=[]
        pos=[(100,350),(620,80),(1100,350)]
        for i in range(3):
            lbl=tk.Label(self.root,fg="white",bg="#222",font=("Consolas",10,"bold"))
            lbl.place(x=pos[i][0],y=pos[i][1],width=220,height=60)
            self.bot_labels.append(lbl)

    def render_top_card(self):
        self.center.delete("all")
        c=self.top_card
        color="#000" if self.active_event=="BLACKOUT" else COLOR_HEX[c.color]
        self.center.create_rectangle(10,10,150,220,fill=color,outline="white",width=2)
        if self.active_event!="BLACKOUT":
            self.center.create_text(80,115,text=str(c.value),fill="white",font=("Impact",32))

    def refresh_ui(self):
        self.stats.config(text=f"LVL {self.profile['level']} | XP {self.profile['xp']} | WINS {self.profile['wins']} | CREDITS {self.profile['credits']}")
        self.event_lbl.config(text=f"WORLD EVENT : {self.active_event}")
        self.render_top_card()

        for i,lbl in enumerate(self.bot_labels, start=1):
            p=self.players[i]
            lbl.config(text=f"{p['name']}\nCARDS: {len(p['hand'])}", bg="#00ff00" if self.turn==i else "#333")

        for w in self.hand_frame.winfo_children(): w.destroy()

        if self.turn==0:
            for i,card in enumerate(self.players[0]["hand"]):
                cv=tk.Canvas(self.hand_frame,width=90,height=120,bg="#111")
                cv.create_rectangle(5,5,85,115,fill=COLOR_HEX[card.color],outline="white")
                cv.create_text(45,60,text=str(card.value),fill="white",font=("Arial",10,"bold"))
                cv.bind("<Button-1>",lambda e,idx=i:self.play_card(idx))
                cv.pack(side="left",padx=4)
        else:
            self.root.after(900,self.ai_turn)

    def play_card(self,idx):
        p=self.players[self.turn]
        card=p["hand"][idx]
        if not card.playable(self.top_card): return
        play_sound("play")
        p["hand"].pop(idx)
        self.apply_card(card)
        if not p["hand"]: self.end_game(p); return
        self.next_turn()

    def ai_turn(self):
        p=self.players[self.turn]
        playable=[c for c in p["hand"] if c.playable(self.top_card)]
        if playable:
            if p["ai"]=="boss":
                playable.sort(key=lambda c:("Draw" in str(c.value) or c.color=="Wild"),reverse=True)
            card=playable[0]
            p["hand"].remove(card)
            self.apply_card(card)
        else:
            n=max(1,self.draw_stack)
            p["hand"]+=[self.draw_card() for _ in range(n)]
            self.draw_stack=0
        if not p["hand"]: self.end_game(p); return
        self.next_turn()

    def apply_card(self,card):
        self.top_card=card
        if "Draw" in str(card.value):
            self.draw_stack+=10 if self.active_event=="DOUBLE DATA" else 5
        elif card.value=="Reverse": self.direction*=-1
        elif card.value=="Skip": self.turn=(self.turn+self.direction)%4
        elif card.color=="Wild": self.top_card.color=random.choice(COLORS)

    def next_turn(self):
        self.event_counter+=1
        self.active_event=random.choice(WORLD_EVENTS) if self.event_counter%5==0 else "STABLE"
        self.turn=(self.turn+self.direction)%4
        self.refresh_ui()

    def end_game(self,winner):
        if winner["human"]:
            play_sound("win")
            self.profile["wins"]+=1
            self.profile["credits"]+=1000
            self.profile["xp"]+=500
            if self.profile["xp"]>=self.profile["level"]*1000:
                self.profile["level"]+=1; self.profile["xp"]=0
            self.save_profile()
            messagebox.showinfo("ZONO","VICTORY CONFIRMED. RANK INCREASED.")
        else:
            play_sound("lose")
        self.root.destroy()

if __name__=="__main__":
    root=tk.Tk()
    GunoZonoMaster(root)
    root.mainloop()
