import pyglet
from mutagen import File
import io
import pickle
import math
from PIL import Image, ImageTk
from tkinter import messagebox
from tkinter.messagebox import showinfo, showerror
import threading
import time
import os
import sys
import pathlib
import pygubu
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from tkinter import simpledialog
import tkinterdnd2 as tkdnd
from pygubu.widgets.tkscrolledframe import TkScrolledFrame
from pygubu.widgets.scrolledframe import ScrolledFrame
import warnings

# Ignore all useless UserWarnings
warnings.simplefilter("ignore", UserWarning)

class BitPlayerApp:
    def __init__(self):
        # Initialize window
        self._window = tkdnd.TkinterDnD.Tk()
        self._window.rowconfigure(0, weight=1)
        self._window.columnconfigure(0, weight=1)
        self._window.rowconfigure(1, minsize=90)

        # Initialize image resources
        self._pauseButtonImage = tk.PhotoImage(file="resources/pause.png")
        self._clearButtonImage = tk.PhotoImage(file="resources/trash.png")
        self._importButtonImage = tk.PhotoImage(file="resources/download.png")
        self._addLabelImage = tk.PhotoImage(file="resources/add.png")
        self._playButtonImage = tk.PhotoImage(file="resources/play.png")
        self._backwardButtonImage = tk.PhotoImage(file="resources/backward.png")
        self._forwardButtonImage = tk.PhotoImage(file="resources/forward.png")
        self._loopButtonImage = tk.PhotoImage(file="resources/loop.png")
        
        # Initialize application variables
        self._player = pyglet.media.Player()
        self._screenWidth = self._window.winfo_width()
        self._screenHeight = self._window.winfo_height()
        self._songTilePreviewPosition = [450, 140]
        self._currentSong = None
        self._isPlaying = False
        self._isLooped = False
        self._importedAudioFilePath = None
        self._importedImageFilePath = None
        self._importedSongName = ""
        self._importedSongExtension = ""
        self.TILE_SIZE = 156
        self.COVER_ART_SIZE = self.TILE_SIZE - 6
        self._songTiles = []
        self._songImages = []
        self._songNames = []
        self._songFileExtensions = []
        self._songs = []
        self._rightSelectedSongName = None
        self._leftSelectedSongName = None
        self._songTilePreview = None
        self._songTilePreviewImage = None
        self._resume = False

        # Initialize all application widgets
        self._tabBar = ttk.Notebook(self._window)
        self._songLibraryFrame = tk.Frame(self._tabBar)
        self._songLibraryScrollFrame = TkScrolledFrame(self._songLibraryFrame, scrolltype="both", takefocus=False)
        self._songLibraryScrollFrame.innerframe.columnconfigure("0", uniform="None")
        self._songLibraryScrollFrame.innerframe.configure(background="#9b9b9b")
        self._songLibraryScrollFrame.configure(usemousewheel=True)
        self._songLibraryScrollFrame.pack(expand="true", fill="both", side="top")
        self._songLibraryFrame.configure(background="#9b9b9b", borderwidth="0", height="400", relief="sunken")
        self._songLibraryFrame.configure(width="600")
        self._songLibraryFrame.pack(anchor="center", expand="true", fill="both", side="top")

        self._tabBar.add(self._songLibraryFrame, padding="0", text="My Song Library")
        self._songImportFrame = tk.Frame(self._tabBar)

        self._audioFileBrowseButton = ttk.Button(self._songImportFrame, command=self.audioFileChooser)
        self._audioFileBrowseButton.configure(takefocus=False, text="Browse...")
        self._audioFileBrowseButton.place(anchor="center", height="26", width="65", x="50", y="120")

        self._imageFileBrowseButton = ttk.Button(self._songImportFrame, command=self.imageFileChooser)
        self._imageFileBrowseButton.configure(text="Browse...")
        self._imageFileBrowseButton.place(anchor="center", height="26", width="65", x="50", y="185")

        self._audioFilePromptLabel = tk.Label(self._songImportFrame)
        self._audioFilePromptLabel.configure(background="#9b9b9b", font="{Consolas} 10 {}", justify="left",
                                             relief="groove")
        self._audioFilePromptLabel.configure(text="Drag and drop audio file onto the \"plus\" or use the browse " +
                                             "buttons to import files manually.", wraplength="190")
        self._audioFilePromptLabel.place(anchor="center", height="70", width="200", x="115", y="42")

        self._imageFilePromptLabel = tk.Label(self._songImportFrame)
        self._imageFilePromptLabel.configure(background="#9b9b9b", font="{Consolas} 11 {}", justify="left",
                                             text="Image:")
        self._imageFilePromptLabel.place(anchor="center", height="20", width="90", x="43", y="160")

        self._audioFilePromptLabel = tk.Label(self._songImportFrame)
        self._audioFilePromptLabel.configure(background="#9b9b9b", font="{Consolas} 11 {}", justify="left",
                                             text="Audio:")
        self._audioFilePromptLabel.place(anchor="center", height="20", width="90", x="44", y="97")

        self._songImportFrameSeparator1 = ttk.Separator(self._songImportFrame)
        self._songImportFrameSeparator1.configure(orient="horizontal")
        self._songImportFrameSeparator1.place(anchor="center", width="570", x="300", y="230")

        self._songImportFrameSeparator2 = ttk.Separator(self._songImportFrame)
        self._songImportFrameSeparator2.configure(orient="horizontal")
        self._songImportFrameSeparator2.place(anchor="center", width="1", height="220", x="300", y="120")

        self._clearImportButton = tk.Button(self._songImportFrame, command=self.clearSongImport)
        self._clearImportButton.configure(font="{@Yu Gothic UI Semibold} 12 {}", background="#ff8585",
                                         activebackground="#ff6161", text=" Clear ", image=self._clearButtonImage,
                                         compound="right")
        self._clearImportButton.place(anchor="center", height="35", width="80", x="197", y="255")

        self._songImportButton = tk.Button(self._songImportFrame, command=self.importSong)
        self._songImportButton.configure(font="{@Yu Gothic UI Semibold} 12 {}", text="     Import Song   ",
                                         image=self._importButtonImage, compound="right")
        self._songImportButton.place(anchor="center", height="35", width="200", x="343", y="255")

        self._audioFileSelectionLabel = tk.Label(self._songImportFrame)
        self._audioFileSelectionLabel.configure(background="#9b9b9b", text="No file selected")
        self._audioFileSelectionLabel.place(anchor="nw", x="87", y="110")

        self._imageFileSelectionLabel = tk.Label(self._songImportFrame)
        self._imageFileSelectionLabel.configure(background="#9b9b9b", text="No file selected")
        self._imageFileSelectionLabel.place(anchor="nw", x="87", y="175")

        # Drag and drop file label
        self._addSongLabel = tk.Label(self._songImportFrame, compound="center", image =self._addLabelImage,
                                      borderwidth=2, relief="ridge")
        self._addSongLabel.place(anchor="center", x=self.getSongTilePreviewPosition(0),
                                 y=self.getSongTilePreviewPosition(1), width=self.TILE_SIZE, height=self.TILE_SIZE)
        self._addSongLabel.drop_target_register(tkdnd.DND_FILES)
        self._addSongLabel.dnd_bind('<<Drop>>', self.addDrop)

        self._songNamePromptLabel = tk.Label(self._songImportFrame)
        self._songNamePromptLabel.configure(background="#9b9b9b", font="{Consolas} 11 {}", justify="left", text="Name:")
        self._songNamePromptLabel.place(anchor="center", height="20", width="50", x="394", y="19")

        self._songNameEntryStringVariable = tk.StringVar()
        self._songNameEntry = tk.Entry(self._songImportFrame, textvariable=self._songNameEntryStringVariable)
        self._songNameEntry.configure(font="{Microsoft} 10 {}")
        self._songNameEntry.place(anchor="center", height="23", width=self.TILE_SIZE, x="450", y="40")

        self._songImportFrame.configure(background="#9b9b9b")
        self._songImportFrame.pack(expand="true", fill="both", side="top")

        self._tabBar.add(self._songImportFrame, padding="0", text="Import Songs")
        self._tabBar.configure(height="400", padding="0", width="600")
        self._tabBar.grid(row=0, column=0, sticky="NSEW")

        self._audioOperationsMenuFrame = tk.Frame(self._window, borderwidth="0", height="90", relief="groove", width="600")

        self._backwardButton = tk.Button(self._audioOperationsMenuFrame, command=self.backwardButton)
        self._backwardButton.configure(borderwidth="1", image=self._backwardButtonImage, relief="flat")
        self._backwardButton.place(anchor="center", x="250", y="50")

        self._playButton = tk.Button(self._audioOperationsMenuFrame, command=self.togglePlay)
        self._playButton.configure(borderwidth="0", image=self._playButtonImage, relief="flat")
        self._playButton.place(anchor="center", x="300", y="50")

        self._rightPlayerProgressLabel = tk.Label(self._audioOperationsMenuFrame)
        self._rightPlayerProgressLabel.configure(justify="right", text="00:00")
        self._rightPlayerProgressLabel.place(anchor="center", x="580", y="12")

        self._audioProgressSlider = ttk.Scale(self._audioOperationsMenuFrame, command=self.changePlayerProgress)
        self._audioProgressSlider.configure(from_="0", orient="horizontal", to="1000")
        self._audioProgressSlider.place(anchor="center", height="10", width="520", x="300", y="13")

        self._leftPlayerProgressLabel = tk.Label(self._audioOperationsMenuFrame)
        self._leftPlayerProgressLabel.configure(justify="right", text="00:00")
        self._leftPlayerProgressLabel.place(anchor="center", x="20", y="12")

        self._forwardButton = tk.Button(self._audioOperationsMenuFrame, command=self.forwardButton)
        self._forwardButton.configure(borderwidth="0", image=self._forwardButtonImage, relief="flat")
        self._forwardButton.place(anchor="center", x="350", y="50")

        self._loopButton = tk.Button(self._audioOperationsMenuFrame, command=self.toggleLoop)
        self._loopButton.configure(borderwidth='0', image=self._loopButtonImage, relief='flat')
        self._loopButton.place(anchor='center', height='25', width='30', x='190', y='49')

        self._volumeSlider = ttk.Scale(self._audioOperationsMenuFrame, command=self.changeVolume)
        self._volumeSlider.configure(from_="0", orient="horizontal", to="100", value="50")
        self._volumeSlider.place(anchor="center", height="10", width="100", x="500", y="50")

        self._volumeLabel = ttk.Label(self._audioOperationsMenuFrame)
        self._volumeLabel.configure(text="Volume")
        self._volumeLabel.place(anchor="center", x="422", y="48")

        self._audioOperationsMenuFrame.grid(row=1, column=0, sticky="EW") #place(anchor="sw", height="80", width="600", y="400")

        self._songTilePopupMenu = tk.Menu(self._window, tearoff=False)
        self._songTilePopupMenu.add_command(label="Information", command=self.getInformationForSongTile)
        self._songTilePopupMenu.add_command(label="Reload", command=self.refreshSongLibrary)
        self._songTilePopupMenu.add_command(label="Rename", command=self.renameSongTile)
        self._songTilePopupMenu.add_command(label="Delete", command=self.deleteSongTile)
        self._songTilePopupMenu.add_separator()
        self._songTilePopupMenu.add_command(label="Cancel", command=lambda: self._songTilePopupMenu.unpost())

        self._window.geometry(f"600x400+{math.trunc(self._window.winfo_screenwidth() / 2) - 300}+{math.trunc(self._window.winfo_screenheight() / 2) - 200}")
        self._window.configure(cursor="hand2", background="#ffffff", borderwidth="1")
        self._window.minsize(600, 400)
        self._window.title("8Bit-Player")
        self._window.iconbitmap("./resources/icon.ico")

        # Initialize bindings and tracings
        self._window.bind("<Configure>", self.resize)
        self._songNameEntryStringVariable.trace("w", self.updateSongNameEntry)
        self._audioProgressSlider.bind("<ButtonPress-1>", self.quickPause)
        self._audioProgressSlider.bind("<ButtonRelease-1>", self.quickPlay)
        self._audioProgressSlider.bind("<ButtonPress-3>", self.quickPause)
        self._audioProgressSlider.bind("<ButtonRelease-3>", self.quickPlay)

        # Initialize states
        self._player.volume = self.getVolume()
        self.loadSongLibrary()

    def getSongTilePreviewPosition(self, index=None):
        if index is not None:
            return self._songTilePreviewPosition[index]
        else:
            return self._songTilePreviewPosition

    def setSongTilePreviewPosition(self, newPosition):
        self._songTilePreviewPosition = newPosition

    def resize(self, event):
        windowWidth = self._window.winfo_width()
        windowHeight = self._window.winfo_height() - 90
        if self._screenWidth != self._window.winfo_width():
            print("RESIZE X") # DEBUG
            # Audio operations frame
            self._backwardButton.place(x=(windowWidth / 2) - 50)
            self._playButton.place(x=(windowWidth / 2))
            self._rightPlayerProgressLabel.place(x=(windowWidth - 20))
            self._audioProgressSlider.place(width=(windowWidth - 80), x=(windowWidth / 2))
            self._leftPlayerProgressLabel.place(x=20)
            self._forwardButton.place(x=(windowWidth / 2) + 50)
            self._loopButton.place(x=(windowWidth / 3.1578))
            self._volumeSlider.place(x=(windowWidth / 1.2))
            self._volumeLabel.place(x=(windowWidth / 1.2) - 85)

            # Song import frame
            self._songNamePromptLabel.place(x=(windowWidth / 1.3333 - 56))
            self._songNameEntry.place(x=(windowWidth / 1.3333))
            self._addSongLabel.place(x=(windowWidth / 1.3333))
            self._songImportFrameSeparator1.place(width=(windowWidth / 1.0526), x=(windowWidth / 2))
            self._songImportFrameSeparator2.place(x=(windowWidth / 2))
            self._clearImportButton.place(width=(windowWidth / 7.5), x=(windowWidth / 3.0456))
            self._songImportButton.place(width=(windowWidth / 3), x=(windowWidth / 1.7492))

            # Update screen width variable
            self._screenWidth = self._window.winfo_width()

        if self._screenHeight != self._window.winfo_height():
            print("RESIZE Y")  # DEBUG
            # Song import frame
            self._songNamePromptLabel.place(y=(windowHeight / 2.2142) - 120)
            self._songNameEntry.place(y=(windowHeight / 2.2142) - 100)
            self._addSongLabel.place(y=(windowHeight / 2.2142))
            self._songImportFrameSeparator1.place(y=(windowHeight / 1.3478))
            self._songImportFrameSeparator2.place(height=(windowHeight / 1.4090), y=(windowHeight / 2.5833))
            self._clearImportButton.place(height=(windowHeight / 8.8560), y=(windowHeight / 1.209) + (15 * (windowHeight / 310) - 15))
            self._songImportButton.place(height=(windowHeight / 8.8560), y=(windowHeight / 1.209) + (15 * (windowHeight / 310) - 15))

            # Update screen height variable
            self._screenHeight = self._window.winfo_height()

        self.setSongTilePreviewPosition([windowWidth / 1.3333, windowHeight / 2.2142])
        if self._songTilePreview is not None:
            self._songTilePreview.place(x=self.getSongTilePreviewPosition(0),
                                        y=self.getSongTilePreviewPosition(1), width=self.TILE_SIZE,
                                        height=self.TILE_SIZE)

    def dismissSplash(self):
        pass

    def quickPause(self, event=None):
        if self._isPlaying is True:
            self.pause()
            self._resume = True

    def quickPlay(self, event=None):
        if self._resume is True:
            self.play()
            self._resume = False

    def changeSongNameEntry(self, text):
        self._songNameEntryStringVariable.set(text)

    def updateSongNameEntry(self, container=None, value=None, name=None):
        self._importedSongName = self._songNameEntryStringVariable.get()
        if self._importedImageFilePath is not None:
            self.previewSongTile()
        print(self._importedSongName) # DEBUG

    def convertProgressToMinutes(self, progress, duration):
        seconds = duration * progress
        invertedSeconds = duration - seconds
        if invertedSeconds < 0:
            invertedSeconds = 0
            print("Time Error")
        minutes = seconds // 60
        invertedMinutes = invertedSeconds // 60
        seconds = seconds % 60
        invertedSeconds = invertedSeconds % 60
        return ["%d:%02d" % (minutes, seconds), "%d:%02d" % (invertedMinutes, invertedSeconds)]

    def convertSecondsToMinutes(self, seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        return "%d:%02d" % (minutes, seconds)

    def refreshProgressBar(self):
        while self._isPlaying:
            self.updatePlayerProgress()
            time.sleep(0.5)
            self.refreshProgressBar()

    def startProgressBar(self):
        refreshThread = threading.Thread(target=self.refreshProgressBar)
        refreshThread.start()

    def getVolume(self):
        volume = self._volumeSlider.get() / 100
        print(volume) # DEBUG
        return volume

    def changeVolume(self, event):
        print("Volume", event) # DEBUG
        self._player.volume = self.getVolume()

    def getPlayerProgress(self):
        progress = self._audioProgressSlider.get() / 1000
        print(progress) # DEBUG
        return progress

    def changePlayerProgress(self, event):
        if self._currentSong is not None:
            if self._isPlaying is True:
                self._player.seek(self._currentSong.duration * self.getPlayerProgress())
            elif self._isPlaying is False:
                self._player.seek(self._currentSong.duration * self.getPlayerProgress())
            self.updatePlayerProgress()
        elif self._currentSong is None:
            self._audioProgressSlider.configure(value=0)

    def updatePlayerProgress(self):
        progress = self._player.time / self._currentSong.duration * 1000
        if progress <= 1000:
            self._audioProgressSlider.configure(value=progress)
            timeProgress = self.convertProgressToMinutes((self._player.time / self._currentSong.duration), self._currentSong.duration)
            self._rightPlayerProgressLabel.configure(justify="left", text=timeProgress[1])
            self._leftPlayerProgressLabel.configure(justify="right", text=timeProgress[0])
            print("Position:", self._player.time, "Duration:", self._currentSong.duration) # DEBUG

        elif progress >= 1000:
            if self._isLooped is True:
                print("Repeat") # DEBUG
                self.playSong(self._currentSong)
            else:
                print("End")  # DEBUG
                self._audioProgressSlider.configure(value=0)
                self.pause()
                self._player.seek(0)
                timeProgress = self.convertProgressToMinutes((self._player.time / self._currentSong.duration),
                                                             self._currentSong.duration)
                self._rightPlayerProgressLabel.configure(justify="left", text=timeProgress[1])
                self._leftPlayerProgressLabel.configure(justify="right", text=timeProgress[0])

        print("Progress:", progress)

    def rightSelectSongTile(self, event, song):
        self._songTilePopupMenu.tk_popup(event.x_root, event.y_root)
        self._rightSelectedSongName = song

    def leftSelectSongTile(self, event, songIndex):
        if self._leftSelectedSongName is not None:
            self._songTiles[self._songNames.index(self._leftSelectedSongName)].configure(bg="#4d4d4d")
        self._songTiles[songIndex].configure(background="#0084ff")
        print("Now playing:", self._songNames[songIndex])
        self._leftSelectedSongName = self._songNames[songIndex]
        self.playSong(self._songs[songIndex])

    def deleteSongTile(self):
        if messagebox.askyesno("Delete?", f"Are you sure you want to delete \"{self._rightSelectedSongName}\"?"):
            songIndex = self._songNames.index(self._rightSelectedSongName)
            os.remove("./songs/" + self._rightSelectedSongName + self._songFileExtensions[songIndex])
            os.remove("./covers/" + self._rightSelectedSongName + ".png")
            self.refreshSongLibrary()

    def renameSongTile(self):
        songIndex = self._songNames.index(self._rightSelectedSongName)
        newName = simpledialog.askstring(title="Rename", prompt="Name:", initialvalue=self._rightSelectedSongName)
        if newName in self._songNames:
            copyIndex = self._songNames.index(newName)
        if newName is not None and self.isSongInLibrary(newName) is False and self.containsIllegals(newName) is False:
            print(self._songNames, songIndex)
            self.renameSong(songIndex, newName)
        elif self.isSongInLibrary(newName) is True and newName in self._songNames:
            if songIndex == copyIndex:
                self.refreshSongLibrary()
            elif songIndex != copyIndex:
                showerror("Error", "Song with name \"" + newName + "\" already exists")

    def getInformationForSongTile(self):
        songIndex = self._songNames.index(self._rightSelectedSongName)
        popup = tk.Toplevel(self._window)
        popup.geometry("260x140")
        popup.title("Information")
        popup.iconbitmap("./resources/icon.ico")
        popup.resizable(True, False)

        columns = ("Property", "Value")
        tree = ttk.Treeview(popup, height=3, columns=columns, show="headings")
        tree.heading("Property", text="Property")
        tree.column("Property", minwidth=0, width=60)
        tree.heading("Value", text="Value")
        tree.column("Value", minwidth=0, width=140)

        tree.insert('', tk.END, values=("Name", self._songNames[songIndex]))
        tree.insert('', tk.END, values=("Type", self._songFileExtensions[songIndex].strip(".").upper() + " File"))
        tree.insert('', tk.END, values=("Length", self.convertSecondsToMinutes(self._songs[songIndex].duration)))
        tree.pack(side="top", fill="x", padx=10)

        okButton = ttk.Button(popup, command=popup.destroy)
        okButton.configure(text="OK")
        okButton.pack(padx=10, pady=5, side="right")

    def loadSongLibrary(self):
        loadSongsThread = threading.Thread(target=self.populateSongLibrary)
        loadSongsThread.start()

    def emptySongLibrary(self):
        for tile in self._songTiles:
            tile.destroy()
        self._songTiles = []
        self._songImages = []
        self._songs = []
        self._songNames = []
        self._songFileExtensions = []
        self._rightSelectedSongName = None
        self._leftSelectedSongName = None
        self._currentSong = None
        self._resume = False
        self._rightPlayerProgressLabel.configure(justify="left", text="00:00")
        self._leftPlayerProgressLabel.configure(justify="right", text="00:00")
        self._audioProgressSlider.configure(value=0)

    def populateSongLibrary(self):
        # Add song button
        songs = os.listdir("./songs")
        print(songs)
        column = 0
        row = 0
        if songs != []:
            for i in range(len(songs)):
                song = self.splitAtExtension(songs[i])[0]
                print(song)
                self._songImages.append(tk.PhotoImage(file="covers/" + song + ".png"))
                self._songFileExtensions.append(self.splitAtExtension(songs[i])[1])
                self._songs.append(pyglet.media.load("songs/" + song + self.splitAtExtension(songs[i])[1]))
                self._songNames.append(song)
                songTile = tk.Canvas(self._songLibraryScrollFrame.innerframe, highlightthickness=0,
                                           background="#4d4d4d", relief="flat", borderwidth=0, width=self.TILE_SIZE,
                                           height=self.TILE_SIZE)
                songTile.create_image(self.TILE_SIZE / 2, self.TILE_SIZE / 2, anchor="center", image=self._songImages[i])
                text = songTile.create_text(self.TILE_SIZE / 2, self.TILE_SIZE - 8, anchor="s",
                                                justify="center", text=song, font="TkDefaultFont 9 bold",
                                                fill="white", width=self.COVER_ART_SIZE - 6)
                boundBox = songTile.bbox(text)
                rectangleTextBox = songTile.create_rectangle(boundBox, outline="#4f4f4f", fill="#757575")
                songTile.tag_raise(text, rectangleTextBox)
                songTile.grid(column=column, row=row, padx=1, pady=1)
                self._songTiles.append(songTile)

                songTile.bind("<Button-1>", lambda event, songIndex=i: self.leftSelectSongTile(event, songIndex))
                songTile.bind("<Button-3>", lambda event, songIndex=i: self.rightSelectSongTile(event, self._songNames[songIndex]))
                column += 1
                if column > 7:
                    column = 0
                    row += 1
            print(self._songs) # DEBUG
            showinfo("Information", "All songs loaded successfully")

    def splitAtExtension(self, filename):
        targetIndex = filename.rfind(".")
        list = [filename[:targetIndex], filename[targetIndex:]]
        return list

    def containsIllegals(self, name):
        if ("|" in name) or ("<" in name) or (">" in name) or ("\"" in name) or ("?" in name) or ("*" in name) or \
           ("?" in name) or ("*" in name) or (":" in name) or ("/" in name) or("/" in name) or (name == ""):
            return True
        else:
            return False

    def renameSong(self, index, newName):
        self.stop()
        os.rename("songs/" + self._rightSelectedSongName + self._songFileExtensions[index],
                  "songs/" + newName + self._songFileExtensions[index])
        os.rename("covers/" + self._rightSelectedSongName + ".png", "covers/" + newName + ".png")
        self.emptySongLibrary()
        self.loadSongLibrary()

    def refreshSongLibrary(self):
        self.stop()
        self.emptySongLibrary()
        self.loadSongLibrary()

    def addDrop(self, event):
        list = event.data.strip("{}").split("} {")
        print(list)
        if len(list) == 1 and list[0].endswith((".au", ".mp2", ".mp3", ".ogg", ".wav", ".wma")):
            filename = list[0]
            self.changeSongNameEntry(self.splitAtExtension(filename.split("/")[-1])[0])
            self._importedAudioFilePath = filename
            if self._importedImageFilePath is None:
                if self.getCoverArt() is False:
                    self._importedImageFilePath = "resources/default.png"
                elif self.getCoverArt() is True:
                    self._importedImageFilePath = "resources/art.png"

            # Edit file selection labels
            if len(self._importedAudioFilePath.split("/")[-1]) > 30:
                self._audioFileSelectionLabel.configure(text=self._importedAudioFilePath.split("/")[-1][:30] + "...")
            else:
                self._audioFileSelectionLabel.configure(text=self._importedAudioFilePath.split("/")[-1])

            if len(self._importedImageFilePath.split("/")[-1]) > 30:
                self._imageFileSelectionLabel.configure(text=self._importedImageFilePath.split("/")[-1][:30] + "...")
            else:
                self._imageFileSelectionLabel.configure(text=self._importedImageFilePath.split("/")[-1])

            self.previewSongTile()
        elif len(list) != 1:
            showerror("Error", "Only one file can be imported at a time")
        elif list[0].endswith(".ogg") is False:
            showerror("Error", "Only audio files are allowed (*.au, *.mp2, *.mp3, *.ogg, *.wav, *.wma)")

    def previewSongTile(self):
        self._songTilePreviewImage = tk.PhotoImage(file=self._importedImageFilePath)
        if self._songTilePreview is not None:
            self._songTilePreview.destroy()

        self._songTilePreview = tk.Canvas(self._songImportFrame, highlightthickness=0,
                             background="#4d4d4d", relief="flat", borderwidth=0, width=self.TILE_SIZE,
                             height=self.TILE_SIZE)
        self._songTilePreview.create_image(self.TILE_SIZE / 2, self.TILE_SIZE / 2, anchor="center", image=self._songTilePreviewImage)
        text = self._songTilePreview.create_text(self.TILE_SIZE / 2, self.TILE_SIZE - 8, anchor="s",
                                    justify="center", text=self._importedSongName, font="TkDefaultFont 9 bold",
                                    fill="white", width=self.COVER_ART_SIZE - 6)
        boundBox = self._songTilePreview.bbox(text)
        rectangleTextBox = self._songTilePreview.create_rectangle(boundBox, outline="#4f4f4f", fill="#757575")
        self._songTilePreview.tag_raise(text, rectangleTextBox)
        self._songTilePreview.place(anchor="center", x=self.getSongTilePreviewPosition(0),
                                    y=self.getSongTilePreviewPosition(1), width=self.TILE_SIZE, height=self.TILE_SIZE)

    def audioFileChooser(self):
        filetypes = [("Audio file", ("*.au", "*.mp2", "*.mp3", "*.ogg", "*.wav", "*.wma"))]
        filename = filedialog.askopenfilename(title="Import audio file", initialdir="/", filetypes=filetypes)
        print("Filename: ", filename) # DEBUG
        if filename != "":
            self._importedAudioFilePath = filename
            self.changeSongNameEntry(self.splitAtExtension(filename.split("/")[-1])[0])

            print("self._importedImageFilePath =", self._importedImageFilePath) # DEBUG
            if self._importedImageFilePath is None:
                if self.getCoverArt() is False:
                    self._importedImageFilePath = "resources/default.png"
                elif self.getCoverArt() is True:
                    self._importedImageFilePath = "resources/art.png"

            # Edit file selection labels
            if len(filename.split("/")[-1]) > 30:
                self._audioFileSelectionLabel.configure(text=filename.split("/")[-1][:30] + "...")
            else:
                self._audioFileSelectionLabel.configure(text=filename.split("/")[-1])

            if len(self._importedImageFilePath.split("/")[-1]) > 30:
                self._imageFileSelectionLabel.configure(
                    text=self._importedImageFilePath.split("/")[-1][:30] + "...")
            else:
                self._imageFileSelectionLabel.configure(text=self._importedImageFilePath.split("/")[-1])

            self.previewSongTile()

    def imageFileChooser(self):
        filetypes = [(f"Image files ({self.COVER_ART_SIZE}x{self.COVER_ART_SIZE}px)", "*.png")]
        filename = filedialog.askopenfilename(title="Import image file", initialdir="/", filetypes=filetypes)
        print("Filename: ", filename)  # DEBUG
        if filename != "":
            image = Image.open(filename)
            width, height = image.size
            print("Width: ", width, "Height: ", height) # DEBUG
            if width == self.COVER_ART_SIZE and height == self.COVER_ART_SIZE:
                if len(filename.split("/")[-1]) > 30:
                    self._imageFileSelectionLabel.configure(text=filename.split("/")[-1][:30] + "...")
                    self._importedImageFilePath = filename
                else:
                    self._imageFileSelectionLabel.configure(text=filename.split("/")[-1])
                    self._importedImageFilePath = filename

                self.previewSongTile()

    def isSongInLibrary(self, song):
        if song in self._songNames:
            return True
        else:
            return False

    def getCoverArt(self):
        if self._importedAudioFilePath is not None:
            file = File(self._importedAudioFilePath)
            if file.tags is not None:
                if "APIC:" in file.tags:
                    artwork = file.tags['APIC:'].data
                    image = Image.open(io.BytesIO(artwork))
                    print("Old Width:", image.width, "Old Height:", image.height) # DEBUG
                    newWidth = math.trunc(image.width * (self.COVER_ART_SIZE / max(image.width, image.height)))
                    newHeight = math.trunc(image.height * (self.COVER_ART_SIZE / max(image.width, image.height)))
                    image = image.resize((newWidth, newHeight), Image.ANTIALIAS)
                    print("New Width:", image.width, "New Height:", image.height) # DEBUG
                    image.save("resources/art.png")
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def importSong(self):
        if self._importedAudioFilePath is not None and self._importedImageFilePath is not None and \
           self.containsIllegals(self._importedSongName) is False and self.isSongInLibrary(self._importedSongName) \
           is False:
            # Save imported audio file
            importedAudioFile = open(self._importedAudioFilePath, "rb")
            savedAudioFile = open("songs/" + self._importedSongName +\
                                  self.splitAtExtension(self._importedAudioFilePath.split("/")[-1])[1], "wb")
            savedAudioFile.write(importedAudioFile.read())
            importedAudioFile.close()
            savedAudioFile.close()

            # Save imported image file
            importedImageFile = open(self._importedImageFilePath, "rb")
            savedImageFile = open("covers/" + self._importedSongName + ".png", "wb")
            savedImageFile.write(importedImageFile.read())
            importedImageFile.close()
            savedImageFile.close()
            self.clearSongImport()
            self.refreshSongLibrary()

            print("Imported", self._importedSongName, "Successfully") # DEBUG
            showinfo("Information", "Song imported successfully")
        else:
            if self._importedAudioFilePath is None:
                showerror("Error", "No audio file selected")
            if self._importedImageFilePath is None:
                showerror("Error", "No valid image file selected")
            if self.isSongInLibrary(self._importedSongName) is True:
                showerror("Error", "Song already exists in library")
            if self._importedSongName == "":
                showerror("Error", "No song name entered")
            elif self.containsIllegals(self._importedSongName) is True:
                showerror("Error", "Song cannot contain the characters \ / : * ? \" < > |")

    def clearSongImport(self):
        self._audioFileSelectionLabel.configure(text="No file selected")
        self._imageFileSelectionLabel.configure(text="No file selected")
        self.changeSongNameEntry("")
        self._importedAudioFilePath = None
        self._importedImageFilePath = None
        self._importedSongName = ""
        if self._songTilePreview is not None:
            self._songTilePreview.destroy()

    def togglePlay(self):
        if self._currentSong is not None:
            if self._isPlaying is False and self._currentSong is not None:
                self.play()
            elif self._isPlaying is True:
                self.pause()

    def toggleLoop(self):
        if self._isLooped is False:
            self._isLooped = True
            self._loopButton.configure(background="#aeaeff")
        elif self._isLooped is True:
            self._isLooped = False
            self._loopButton.configure(background="SystemButtonFace")

    def play(self):
        if self._currentSong is not None:
            self._isPlaying = True
            self.startProgressBar()
            self._player.play()
            self._playButton.configure(image=self._pauseButtonImage)

    def pause(self, event=None):
        self._isPlaying = False
        self._player.pause()
        self._playButton.configure(image=self._playButtonImage)

    def stop(self):
        self.pause()
        self._player.next_source()

    def playSong(self, songData):
        print(songData) # DEBUG
        self._player.next_source()
        self._currentSong = songData
        self._player.queue(songData)
        self.play()

    def backwardButton(self):
        if self._currentSong is not None:
            if 0 == self._songs.index(self._currentSong):
                self.leftSelectSongTile(None, len(self._songs) - 1)
            else:
                self.leftSelectSongTile(None, self._songs.index(self._currentSong) - 1)

    def forwardButton(self):
        if self._currentSong is not None:
            if len(self._songs) - 1 == self._songs.index(self._currentSong):
                self.leftSelectSongTile(None, 0)
            else:
                self.leftSelectSongTile(None, self._songs.index(self._currentSong) + 1)

    def close(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.stop()
            pyglet.app.exit()
            sys.exit()
            self._window.destroy()

    def run(self):
        self._window.protocol("WM_DELETE_WINDOW", self.close)
        self._window.mainloop()
        pyglet.app.run()

if __name__ == "__main__":
    app = BitPlayerApp()
    app.run()
