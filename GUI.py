import Anime1

import tkinter as tk

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        #self.pack()
        self.grid()
        self.anime_list = list()
        self.index = 0
        self.start=0
        self.end=0
        self.qsearchOn = tk.BooleanVar(value=True)
        self.create_widgets()

    def create_widgets(self):
        self.tickQSearch = tk.Checkbutton(
            self, text = " ",
            variable = self.qsearchOn,
            onvalue = True, offvalue = False
            )

        self.wBtSearch              = tk.Button(self)
        self.wBtSearch["text"]      = "Search"
        self.wBtSearch["command"]   = self.search

        self.wBtSelect              = tk.Button(self)
        self.wBtSelect["text"]      = "Select"
        self.wBtSelect["command"]   = self.select

        self.wBtStart               = tk.Button(self)
        self.wBtStart["text"]       = "Start"
        self.wBtStart["command"]    = self.setstart

        self.wBtEnd                 = tk.Button(self)
        self.wBtEnd["text"]         = "End"
        self.wBtEnd["command"]      = self.setend


        self.wBtScrap               = tk.Button(self)
        self.wBtScrap["text"]       = "Scrap"
        self.wBtScrap["command"]    = self.scrap

        self.wLbInfo                = tk.Label(self)
        self.wLbInfo["text"]        = "Info"
        #self.wLbInfo["command"]    = self.scrap

        self.wEnInput  = tk.Entry(self)
        self.wEnInput.config(width=100)
        self.wEnInput.bind("<Return>", self.search)
        self.wEnInput.bind("<KeyRelease>", self.quicksearch)
        
        self.wLbList   = tk.Listbox(self,selectmode=tk.SINGLE)
        self.wLbList.config(height=20,width=100)
        #self.wEnInput.bind("<Return>", self.select)
        
        #self.wEnInput.pack(side="top")
        #self.wBtSearch.pack(side="left")

        self.tickQSearch.grid(row=0, column=0)
        self.wEnInput.grid(row=0, column=1)
        self.wBtSearch.grid(row=0, column=2)
        self.wBtSelect.grid(row=0, column=3)

        self.wLbInfo.grid(row=1, column=1)
        self.wBtStart.grid(row=1, column=2)
        self.wBtEnd.grid(row=1, column=3)
        self.wBtScrap.grid(row=1, column=4)
        
        self.wLbList.grid(row=2, column=1)
        
        
        self.quit = tk.Button(
            self, text="QUIT", fg="red",command=self.master.destroy
            )
        #self.quit.pack(side="bottom")
        self.quit.grid(row=3, column=2)
        
    def search(self,event=None):
        pattern = self.wEnInput.get()
        self.anime_list = Anime1.search(pattern)
        anime_list = self.anime_list
        #print(len(anime_list))
        i = 1
        self.wLbList.delete(0,self.wLbList.size())
        while i<=len(anime_list):
            self.wLbList.insert(i,'%3d. %s'%(i,anime_list[i-1]['name']))
            i = i+1

    def quicksearch(self,event=None):
        #print(self.qsearchOn.get())
        if self.qsearchOn.get():
            self.search()
    
    def select(self,event=None):
        if len(self.anime_list)>0:
            selection = self.wLbList.curselection()
            if len(selection)>0:
                self.index = selection[0]
            else:
                return
            #print(self.index)
            anime = self.anime_list[self.index]
            self.wLbList.delete(0,self.wLbList.size())
            url_list = Anime1.getURLs(anime['url'])

            i=1
            while i<=len(url_list):
                self.wLbList.insert(i,'%3d. %s'%(i,url_list[i-1]['name']))
                i = i+1
        self.updateinfo()
        
    def setstart(self):
        self.start = self.wLbList.curselection()[0]
        self.updateinfo()
        
    def setend(self):
        self.end = self.wLbList.curselection()[0]
        self.updateinfo()

    def updateinfo(self):
        if len(self.anime_list)>0:
            anime = self.anime_list[self.index]['name']
        else:
            anime = 'not selected'
        info = 'Anime:%s \t start:%d \t end:%d '%(anime,self.start+1,self.end+1)
        self.wLbInfo["text"] = info
          
    def scrap(self,event=None):
        anime = self.anime_list[self.index]
        limit = (self.start,self.end)
        Anime1.scrap(anime,limit)
        info = 'done'
        self.wLbInfo["text"] = info

def main():
    root = tk.Tk()
    app = Application(master=root)
    app.master.title("Anime Scraper")
    app.mainloop()

if __name__=="__main__":
    main()
