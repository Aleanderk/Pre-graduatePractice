import glob
import tkinter.messagebox
from tkinter import *
from tkinter import filedialog, ttk
import pickle
import pandas as pd
import os
import shutil
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pandastable import Table
import plotly.express as px
import plotly
from html2image import Html2Image
from PIL import ImageTk, Image
import webbrowser

temp_login = ''
data = pd.DataFrame()
whole_information = dict()


class UserInterface:
    def __init__(self):
        self.window = Tk()
        self.window.title('Recommendation system with data visualization. Initial Screen')
        self.window.geometry('500x300')
        self.window.iconbitmap('icon.ico')
        self.ShowLoginVisualizationScreen()
        self.window.resizable(width=False, height=False)
        self.window.mainloop()
    def ShowLoginVisualizationScreen(self):
        global whole_information
        self.lbl1 = Label(self.window, text='Input your login:', font=('Times New Roman', 26))
        self.inpt1 = Entry(self.window, width=75)
        self.lbl2 = Label(self.window, text='Input your password:', font=('Times New Roman', 26))
        self.inpt2 = Entry(self.window, width=75)
        self.btn1 = Button(self.window, text='Log in', font=('Times new Roman', 12), width=25, command=self.Clicked_LogIn)
        self.btn2 = Button(self.window, text='Register', font=('Times new Roman', 12), width=25, command=self.Clicked_Register)
        self.lbl1.place(x=132.5, y=5)
        self.inpt1.place(x=25,y=55)
        self.lbl2.place(x=101.5, y=85)
        self.inpt2.place(x=25, y=135)
        self.btn1.place(x= 132.5, y = 175)
        self.btn2.place(x=132.5, y=225)
    def Clicked_Register(self):
        login = self.inpt1.get()
        password = self.inpt2.get()
        self.persons_dict = StateManagmentSubsystem.LoadLogInInformation(self)
        if len(login) < 3 or len(password) < 8:
            tkinter.messagebox.showerror("Register Error",
                                         "The entered username must be at least 3 characters,\n and the password must be at least 8 characters. Check the correctness.")
        elif login in self.persons_dict:
            tkinter.messagebox.showerror("Register Error",
                                         "This login already exists. Try another one.")
        else:
            global temp_login
            temp_login = login
            self.persons_dict[login] = password
            StateManagmentSubsystem().RegisterSave(self.persons_dict)
            self.window.destroy()
            StateTransitionSubsystem().GoToDataLoadingSubsystem()
    def Clicked_LogIn(self):
        login = self.inpt1.get()
        password = self.inpt2.get()
        self.persons_dict = StateManagmentSubsystem.LoadLogInInformation(self)
        if login not in self.persons_dict or (login in self.persons_dict and password != self.persons_dict[login]):
            tkinter.messagebox.showerror("LogIn Error", "There is no such login or password. Check the correctness of the entered data.")
        else:
            self.window.destroy()
            global temp_login
            temp_login = login
            StateTransitionSubsystem().GoToDataLoadingSubsystem()




class DataLoadingSubsystem:
    def __init__(self):
        self.window = Tk()
        self.window.title('Recommendation system with data visualization. Data Loading Screen')
        self.window.geometry('600x300')
        self.window.iconbitmap('icon.ico')
        self.window.resizable(width=False, height=False)
        self.ShowLoadDataScreen()
        self.window.mainloop()
    def ShowLoadDataScreen(self):
        self.lbl1 = Label(self.window, text='Please upload your dataset in Excel format, where the names of the\n recommendation elements will be in the first column,\n and their parameters in the rest.', font=('Times New Roman', 16))
        self.lbl1.place(x=18.5, y=5)
        self.btn1 = Button(self.window, text='Choose file', font=('Times new Roman', 12), width=25,
                           command=self.Clicked_ChooseFile)
        self.btn1.place(x=180.5, y=150)
        self.btn2 = Button(self.window, text='Go to Initial Screen', font=('Times new Roman', 12), width=20,
                           command=self.Clicked_GoToUserInterface)
        self.btn2.place(x=5, y=240)
        self.btn3 = Button(self.window, text='Go to Recommendation Screen', font=('Times new Roman', 12), width=22,
                           command=self.Clicked_GoToRecommendersSubsystem)
        self.btn3.place(x=196, y=240)
        self.btn4 = Button(self.window, text='Go to Visualization Screen', font=('Times new Roman', 12), width=20,
                           command=self.Clicked_GoToVisualizationSubsystem)
        self.btn4.place(x=405, y=240)
    def Clicked_ChooseFile(self):
        filepath = filedialog.askopenfilename()
        if filepath != "":
            if filepath.endswith(".xlsx") or filepath.endswith(".xlsm") or filepath.endswith(".xlsb") or filepath.endswith(".xltx") or filepath.endswith(".xltm") or filepath.endswith(".xls") or filepath.endswith(".xlt") or filepath.endswith(".xml") or filepath.endswith(".xlam") or filepath.endswith(".xla") or filepath.endswith(".xlw") or filepath.endswith(".xlr"):
                excel_data = pd.read_excel(filepath)
                global data
                global whole_information
                whole_information = dict()
                data = pd.DataFrame(excel_data)
                whole_information['data']=data
                StateManagmentSubsystem().SaveWholeInformation()
                #print("The content of the file is:\n", data.iloc[1,1])
                StateManagmentSubsystem().SaveDataLoadingSubsystemFile(filepath)
            else:
                tkinter.messagebox.showerror("File Error",

                                             "The wrong file format is selected. Try again.")
    def Data_Check(self):
        global data
        global whole_information
        if os.path.isfile('AccountInformation\\'+temp_login+'\\information.bin'):
            whole_information = StateManagmentSubsystem().DownloadDataLoadingSubsystemWholeInformation()
            data = whole_information['data']
            return True
        else:
            return False

    def Clicked_GoToUserInterface(self):
        self.window.destroy()
        StateTransitionSubsystem().GoToUserInterface()
    def Clicked_GoToVisualizationSubsystem(self):
        if data.empty:
            if self.Data_Check():
                self.window.destroy()
                StateTransitionSubsystem().GoToVisualizationSubsystem()
            else:
                tkinter.messagebox.showerror("File Error",
                                             "The file was not found. Try the selection again.")
        else:
            self.window.destroy()
            StateTransitionSubsystem().GoToVisualizationSubsystem()

    def Clicked_GoToRecommendersSubsystem(self):
        if data.empty:
            if self.Data_Check():
                self.window.destroy()
                StateTransitionSubsystem().GoToRecommendersSubsystem()
            else:
                tkinter.messagebox.showerror("File Error",
                                             "The file was not found. Try the selection again.")
        else:
            self.window.destroy()
            StateTransitionSubsystem().GoToRecommendersSubsystem()




class VisualizationSubsystem:
    def __init__(self):
        self.window = Tk()
        self.window.title('Recommendation system with data visualization. Visualization Screen')
        self.window.geometry('600x300')
        self.window.iconbitmap('icon.ico')
        self.window.resizable(width=False, height=False)
        self.ShowVisualizationScreen()
        self.window.mainloop()
    def ShowVisualizationScreen(self):
        global data
        global temp_login
        global whole_information
        self.information = dict()
        self.list_of_parameters = list(data.columns.values)
        self.list_of_visualizations = ['histogram', 'barchart', 'piechart', 'scatter']
        self.lbl1 = Label(self.window,
                          text='Select the type of vizualization:',
                          font=('Times New Roman', 16))
        self.lbl1.place(x=25, y=25)
        self.combobox1 = ttk.Combobox(values=self.list_of_visualizations, state="readonly")
        self.combobox1.place(x=25, y=75)
        self.combobox1.bind('<<ComboboxSelected>>', self.UpdateVisualizationScreen)


        self.btn2 = Button(self.window, text='Go to Initial Screen', font=('Times new Roman', 12), width=20,
                           command=self.Clicked_GoToUserInterface)
        self.btn2.place(x=5, y=250)
        self.btn3 = Button(self.window, text='Go to Data Loading Screen', font=('Times new Roman', 12), width=20,
                           command=self.Clicked_GoToDataLoadingSubsystem)
        self.btn3.place(x=195, y=250)
        self.btn4 = Button(self.window, text='Go to Recommendation Screen', font=('Times new Roman', 12), width=22,
                           command=self.Clicked_GoToRecommendersSubsystem)
        self.btn4.place(x=385, y=250)
        if 'data_recommenders' in whole_information:
            self.btn6 = Button(self.window, text='Show recommendations', font=('Times new Roman', 12), width=20, command=self.Clicked_ShowRecommendations)
            self.btn6.place(x=195, y = 175)
        try:
            self.combobox1.set(whole_information['visualization']['type_visualization'])
            self.combobox1.event_generate('<<ComboboxSelected>>')
        except:
            None


    def dismiss1(self):
        self.window2.grab_release()
        self.window2.destroy()

    def Clicked_ShowRecommendations(self):
        self.window2 = Toplevel()
        self.window2.title('Recommendation system with data visualization. Recommendations')
        self.window2.geometry('600x300')
        self.window2.iconbitmap('icon.ico')
        self.window2.protocol("WM_DELETE_WINDOW", lambda: self.dismiss1())
        self.window2.grab_set()
        # self.frame1 = ttk.Frame(self.window1)
        self.table2 = Table(self.window2, dataframe=whole_information['data_recommenders'],
                            showtoolbar=False, showstatusbar=False)
        self.table2.show()
        self.table2.redraw()

    def UpdateVisualizationScreen(self, event):
        try:
            self.lbl2.destroy()
            self.lbl3.destroy()
            self.combobox2.destroy()
            self.combobox3.destroy()
            self.btn5.destroy()
        except:
            None
        if self.combobox1.get() == 'histogram':
            try:
                if whole_information['visualization']['type_visualization'] == 'histogram':
                    self.lbl2 = Label(self.window,
                              text='Select the x-axis option:',
                              font=('Times New Roman', 16))
                    self.lbl2.place(x=25, y=110)
                    self.lbl3 = Label(self.window,
                              text='Select the y-axis option:',
                              font=('Times New Roman', 16))
                    self.lbl3.place(x=325, y=110)
                    self.combobox2 = ttk.Combobox(values=self.list_of_parameters, state="readonly")
                    self.combobox2.set(whole_information['visualization']['x_axis'])
                    self.combobox2.place(x=35, y=150)
                    self.combobox3 = ttk.Combobox(values=self.list_of_parameters, state="readonly")
                    self.combobox3.set(whole_information['visualization']['y_axis'])
                    self.combobox3.place(x=335, y=150)
                    self.btn5 = Button(self.window, text='Get visualization', font=('Times new Roman', 12), width=20,
                               command=self.Clicked_GetVisualization)
                    self.btn5.place(x=195, y=210)
                else:
                    self.lbl2 = Label(self.window,
                                      text='Select the x-axis option:',
                                      font=('Times New Roman', 16))
                    self.lbl2.place(x=25, y=110)
                    self.lbl3 = Label(self.window,
                                      text='Select the y-axis option:',
                                      font=('Times New Roman', 16))
                    self.lbl3.place(x=325, y=110)
                    self.combobox2 = ttk.Combobox(values=self.list_of_parameters, state="readonly")
                    self.combobox2.place(x=35, y=150)
                    self.combobox3 = ttk.Combobox(values=self.list_of_parameters, state="readonly")
                    self.combobox3.place(x=335, y=150)
                    self.btn5 = Button(self.window, text='Get visualization', font=('Times new Roman', 12), width=20,
                                       command=self.Clicked_GetVisualization)
                    self.btn5.place(x=195, y=210)
            except:
                self.lbl2 = Label(self.window,
                                  text='Select the x-axis option:',
                                  font=('Times New Roman', 16))
                self.lbl2.place(x=25, y=110)
                self.lbl3 = Label(self.window,
                                  text='Select the y-axis option:',
                                  font=('Times New Roman', 16))
                self.lbl3.place(x=325, y=110)
                self.combobox2 = ttk.Combobox(values=self.list_of_parameters, state="readonly")
                self.combobox2.place(x=35, y=150)
                self.combobox3 = ttk.Combobox(values=self.list_of_parameters, state="readonly")
                self.combobox3.place(x=335, y=150)
                self.btn5 = Button(self.window, text='Get visualization', font=('Times new Roman', 12), width=20,
                                   command=self.Clicked_GetVisualization)
                self.btn5.place(x=195, y=210)

        elif self.combobox1.get() == 'barchart':
            try:
                if whole_information['visualization']['type_visualization'] == 'barchart':
                    self.lbl2 = Label(self.window,
                              text='Select the x-axis option:',
                              font=('Times New Roman', 16))
                    self.lbl2.place(x=25, y=110)
                    self.lbl3 = Label(self.window,
                              text='Select the y-axis option:',
                              font=('Times New Roman', 16))
                    self.lbl3.place(x=325, y=110)
                    self.combobox2 = ttk.Combobox(values=self.list_of_parameters, state="readonly")
                    self.combobox2.set(whole_information['visualization']['x_axis'])
                    self.combobox2.place(x=35, y=150)
                    self.combobox3 = ttk.Combobox(values=self.list_of_parameters, state="readonly")
                    self.combobox3.set(whole_information['visualization']['y_axis'])
                    self.combobox3.place(x=335, y=150)
                    self.btn5 = Button(self.window, text='Get visualization', font=('Times new Roman', 12), width=20,
                               command=self.Clicked_GetVisualization)
                    self.btn5.place(x=195, y=210)
                else:
                    self.lbl2 = Label(self.window,
                                      text='Select the x-axis option:',
                                      font=('Times New Roman', 16))
                    self.lbl2.place(x=25, y=110)
                    self.lbl3 = Label(self.window,
                                      text='Select the y-axis option:',
                                      font=('Times New Roman', 16))
                    self.lbl3.place(x=325, y=110)
                    self.combobox2 = ttk.Combobox(values=self.list_of_parameters, state="readonly")
                    self.combobox2.place(x=35, y=150)
                    self.combobox3 = ttk.Combobox(values=self.list_of_parameters, state="readonly")
                    self.combobox3.place(x=335, y=150)
                    self.btn5 = Button(self.window, text='Get visualization', font=('Times new Roman', 12), width=20,
                                       command=self.Clicked_GetVisualization)
                    self.btn5.place(x=195, y=210)
            except:
                self.lbl2 = Label(self.window,
                                  text='Select the x-axis option:',
                                  font=('Times New Roman', 16))
                self.lbl2.place(x=25, y=110)
                self.lbl3 = Label(self.window,
                                  text='Select the y-axis option:',
                                  font=('Times New Roman', 16))
                self.lbl3.place(x=325, y=110)
                self.combobox2 = ttk.Combobox(values=self.list_of_parameters, state="readonly")
                self.combobox2.place(x=35, y=150)
                self.combobox3 = ttk.Combobox(values=self.list_of_parameters, state="readonly")
                self.combobox3.place(x=335, y=150)
                self.btn5 = Button(self.window, text='Get visualization', font=('Times new Roman', 12), width=20,
                                   command=self.Clicked_GetVisualization)
                self.btn5.place(x=195, y=210)

        elif self.combobox1.get() == 'piechart':
            try:
                if whole_information['visualization']['type_visualization'] == 'piechart':
                    self.lbl2 = Label(self.window,
                              text='Select the names option:',
                              font=('Times New Roman', 16))
                    self.lbl2.place(x=25, y=110)
                    self.lbl3 = Label(self.window,
                              text='Select the values option:',
                              font=('Times New Roman', 16))
                    self.lbl3.place(x=325, y=110)
                    self.combobox2 = ttk.Combobox(values=self.list_of_parameters, state="readonly")
                    self.combobox2.set(whole_information['visualization']['names'])
                    self.combobox2.place(x=35, y=150)
                    self.combobox3 = ttk.Combobox(values=self.list_of_parameters, state="readonly")
                    self.combobox3.set(whole_information['visualization']['values'])
                    self.combobox3.place(x=335, y=150)
                    self.btn5 = Button(self.window, text='Get visualization', font=('Times new Roman', 12), width=20,
                               command=self.Clicked_GetVisualization)
                    self.btn5.place(x=195, y=210)
                else:
                    self.lbl2 = Label(self.window,
                                      text='Select the names option:',
                                      font=('Times New Roman', 16))
                    self.lbl2.place(x=25, y=110)
                    self.lbl3 = Label(self.window,
                                      text='Select the values option:',
                                      font=('Times New Roman', 16))
                    self.lbl3.place(x=325, y=110)
                    self.combobox2 = ttk.Combobox(values=self.list_of_parameters, state="readonly")
                    self.combobox2.place(x=35, y=150)
                    self.combobox3 = ttk.Combobox(values=self.list_of_parameters, state="readonly")
                    self.combobox3.place(x=335, y=150)
                    self.btn5 = Button(self.window, text='Get visualization', font=('Times new Roman', 12), width=20,
                                       command=self.Clicked_GetVisualization)
                    self.btn5.place(x=195, y=210)
            except:
                self.lbl2 = Label(self.window,
                                  text='Select the names option:',
                                  font=('Times New Roman', 16))
                self.lbl2.place(x=25, y=110)
                self.lbl3 = Label(self.window,
                                  text='Select the values option:',
                                  font=('Times New Roman', 16))
                self.lbl3.place(x=325, y=110)
                self.combobox2 = ttk.Combobox(values=self.list_of_parameters, state="readonly")
                self.combobox2.place(x=35, y=150)
                self.combobox3 = ttk.Combobox(values=self.list_of_parameters, state="readonly")
                self.combobox3.place(x=335, y=150)
                self.btn5 = Button(self.window, text='Get visualization', font=('Times new Roman', 12), width=20,
                                   command=self.Clicked_GetVisualization)
                self.btn5.place(x=195, y=210)

        elif self.combobox1.get() == 'scatter':
            try:
                if whole_information['visualization']['type_visualization'] == 'scatter':
                    self.lbl2 = Label(self.window,
                              text='Select the x-axis option:',
                              font=('Times New Roman', 16))
                    self.lbl2.place(x=25, y=110)
                    self.lbl3 = Label(self.window,
                              text='Select the y-axis option:',
                              font=('Times New Roman', 16))
                    self.lbl3.place(x=325, y=110)
                    self.combobox2 = ttk.Combobox(values=self.list_of_parameters, state="readonly")
                    self.combobox2.set(whole_information['visualization']['x_axis'])
                    self.combobox2.place(x=35, y=150)
                    self.combobox3 = ttk.Combobox(values=self.list_of_parameters, state="readonly")
                    self.combobox3.set(whole_information['visualization']['y_axis'])
                    self.combobox3.place(x=335, y=150)
                    self.btn5 = Button(self.window, text='Get visualization', font=('Times new Roman', 12), width=20,
                               command=self.Clicked_GetVisualization)
                    self.btn5.place(x=195, y=210)
                else:
                    self.lbl2 = Label(self.window,
                                      text='Select the x-axis option:',
                                      font=('Times New Roman', 16))
                    self.lbl2.place(x=25, y=110)
                    self.lbl3 = Label(self.window,
                                      text='Select the y-axis option:',
                                      font=('Times New Roman', 16))
                    self.lbl3.place(x=325, y=110)
                    self.combobox2 = ttk.Combobox(values=self.list_of_parameters, state="readonly")
                    self.combobox2.place(x=35, y=150)
                    self.combobox3 = ttk.Combobox(values=self.list_of_parameters, state="readonly")
                    self.combobox3.place(x=335, y=150)
                    self.btn5 = Button(self.window, text='Get visualization', font=('Times new Roman', 12), width=20,
                                       command=self.Clicked_GetVisualization)
                    self.btn5.place(x=195, y=210)
            except:
                self.lbl2 = Label(self.window,
                                  text='Select the x-axis option:',
                                  font=('Times New Roman', 16))
                self.lbl2.place(x=25, y=110)
                self.lbl3 = Label(self.window,
                                  text='Select the y-axis option:',
                                  font=('Times New Roman', 16))
                self.lbl3.place(x=325, y=110)
                self.combobox2 = ttk.Combobox(values=self.list_of_parameters, state="readonly")
                self.combobox2.place(x=35, y=150)
                self.combobox3 = ttk.Combobox(values=self.list_of_parameters, state="readonly")
                self.combobox3.place(x=335, y=150)
                self.btn5 = Button(self.window, text='Get visualization', font=('Times new Roman', 12), width=20,
                                   command=self.Clicked_GetVisualization)
                self.btn5.place(x=195, y=210)

    def dismiss(self):
        self.window1.grab_release()
        self.window1.destroy()


    def Clicked_GetVisualization(self):
        if self.combobox2.get() == '' or self.combobox3.get() == '':
            tkinter.messagebox.showerror("Input Error",
                                         "Not selected parameters. Try again.")
        else:
            self.window1 = Toplevel()
            self.window1.title('Recommendation system with data visualization. Visualization Screen')
            self.window1.geometry('600x350')
            self.window1.resizable(width=False, height=False)
            self.window1.iconbitmap('icon.ico')
            self.window1.protocol("WM_DELETE_WINDOW", lambda: self.dismiss())
            self.window1.grab_set()

            if self.combobox1.get() == 'histogram':
                try:
                    if whole_information['visualization']['type_visualization'] == 'histogram' and \
                            whole_information['visualization']['x_axis'] == self.combobox2.get() and \
                            whole_information['visualization']['y_axis'] == self.combobox3.get():
                        self.image = Image.open(whole_information['visualization']['image'])
                        self.image = self.image.resize((600, 300), Image.ANTIALIAS)
                        self.image = ImageTk.PhotoImage(self.image)
                        self.file_path_img = whole_information['visualization']['image']
                        self.file_path_html = whole_information['visualization']['html']
                    else:
                        try:
                            fig = px.histogram(whole_information['data_recommenders'], x=self.combobox2.get(),
                                               y=self.combobox3.get())
                        except:
                            fig = px.histogram(data, x=self.combobox2.get(),
                                               y=self.combobox3.get())
                        self.file_path_img, self.file_path_html = StateManagmentSubsystem().SaveVisualizationSubsystemImj(fig)
                        self.image = Image.open(self.file_path_img)
                        self.image = self.image.resize((600, 300), Image.ANTIALIAS)
                        self.image = ImageTk.PhotoImage(self.image)
                except:
                    try:
                        fig = px.histogram(whole_information['data_recommenders'], x=self.combobox2.get(),
                                           y=self.combobox3.get())
                    except:
                        fig = px.histogram(data, x=self.combobox2.get(), y=self.combobox3.get())
                    self.file_path_img, self.file_path_html = StateManagmentSubsystem().SaveVisualizationSubsystemImj(fig)
                    self.image = Image.open(self.file_path_img)
                    self.image = self.image.resize((600, 300), Image.ANTIALIAS)
                    self.image = ImageTk.PhotoImage(self.image)

                self.information['type_visualization'] = 'histogram'
                self.information['x_axis'] = self.combobox2.get()
                self.information['y_axis'] = self.combobox3.get()
                self.information['image'] = self.file_path_img
                self.information['html'] = self.file_path_html
                whole_information['visualization'] = self.information
                self.panel = Label(self.window1, image=self.image)
                self.panel.place(x=0, y=0)
                self.btn6 = Button(self.window1, text='Get interactive visualization', font=('Times new Roman', 12),
                               width=20,
                               command=self.Clicked_GetInteractiveVisualization)
                self.btn6.place(x=205, y=310)
                StateManagmentSubsystem.SaveWholeInformation(self)

            elif self.combobox1.get() == 'barchart':
                try:
                    if whole_information['visualization']['type_visualization'] == 'barchart' and \
                            whole_information['visualization']['x_axis'] == self.combobox2.get() and \
                            whole_information['visualization']['y_axis'] == self.combobox3.get():
                        self.image = Image.open(whole_information['visualization']['image'])
                        self.image = self.image.resize((600, 300), Image.ANTIALIAS)
                        self.image = ImageTk.PhotoImage(self.image)
                        self.file_path_img = whole_information['visualization']['image']
                        self.file_path_html = whole_information['visualization']['html']
                    else:
                        try:
                            fig = px.bar(whole_information['data_recommenders'], x=self.combobox2.get(),
                                               y=self.combobox3.get())
                        except:
                            fig = px.bar(data, x=self.combobox2.get(),
                                               y=self.combobox3.get())
                        self.file_path_img, self.file_path_html = StateManagmentSubsystem().SaveVisualizationSubsystemImj(fig)
                        self.image = Image.open(self.file_path_img)
                        self.image = self.image.resize((600, 300), Image.ANTIALIAS)
                        self.image = ImageTk.PhotoImage(self.image)
                except:
                    try:
                        fig = px.bar(whole_information['data_recommenders'], x=self.combobox2.get(),
                                           y=self.combobox3.get())
                    except:
                        fig = px.bar(data, x=self.combobox2.get(), y=self.combobox3.get())
                    self.file_path_imj, self.file_path_html = StateManagmentSubsystem().SaveVisualizationSubsystemImj(fig)
                    self.image = Image.open(self.file_path_img)
                    self.image = self.image.resize((600, 300), Image.ANTIALIAS)
                    self.image = ImageTk.PhotoImage(self.image)

                self.information['type_visualization'] = 'barchart'
                self.information['x_axis'] = self.combobox2.get()
                self.information['y_axis'] = self.combobox3.get()
                self.information['image'] = self.file_path_img
                self.information['html'] = self.file_path_html
                whole_information['visualization'] = self.information
                self.panel = Label(self.window1, image=self.image)
                self.panel.place(x=0, y=0)
                self.btn6 = Button(self.window1, text='Get interactive visualization', font=('Times new Roman', 12),
                               width=20,
                               command=self.Clicked_GetInteractiveVisualization)
                self.btn6.place(x=205, y=310)
                StateManagmentSubsystem().SaveWholeInformation()


            elif self.combobox1.get() == 'piechart':
                try:
                    if whole_information['visualization']['type_visualization'] == 'piechart' and \
                            whole_information['visualization']['names'] == self.combobox2.get() and \
                            whole_information['visualization']['values'] == self.combobox3.get():
                        self.image = Image.open(whole_information['visualization']['image'])
                        self.image = self.image.resize((600, 300), Image.ANTIALIAS)
                        self.image = ImageTk.PhotoImage(self.image)
                        self.file_path_img = whole_information['visualization']['image']
                        self.file_path_html = whole_information['visualization']['html']
                    else:
                        try:
                            fig = px.pie(whole_information['data_recommenders'], names=self.combobox2.get(),
                                               values=self.combobox3.get())
                        except:
                            fig = px.pie(data, names=self.combobox2.get(),
                                               values=self.combobox3.get())
                        self.file_path_img, self.file_path_html = StateManagmentSubsystem().SaveVisualizationSubsystemImj(fig)
                        self.image = Image.open(self.file_path_img)
                        self.image = self.image.resize((600, 300), Image.ANTIALIAS)
                        self.image = ImageTk.PhotoImage(self.image)
                except:
                    try:
                        fig = px.pie(whole_information['data_recommenders'], names=self.combobox2.get(),
                                           values=self.combobox3.get())
                    except:
                        fig = px.pie(data, names=self.combobox2.get(), values=self.combobox3.get())
                    self.file_path_img, self.file_path_html = StateManagmentSubsystem().SaveVisualizationSubsystemImj(fig)
                    self.image = Image.open(self.file_path_img)
                    self.image = self.image.resize((600, 300), Image.ANTIALIAS)
                    self.image = ImageTk.PhotoImage(self.image)

                self.information['type_visualization'] = 'piechart'
                self.information['names'] = self.combobox2.get()
                self.information['values'] = self.combobox3.get()
                self.information['image'] = self.file_path_img
                self.information['html'] = self.file_path_html
                whole_information['visualization'] = self.information
                self.panel = Label(self.window1, image=self.image)
                self.panel.place(x=0, y=0)
                self.btn6 = Button(self.window1, text='Get interactive visualization', font=('Times new Roman', 12),
                               width=20,
                               command=self.Clicked_GetInteractiveVisualization)
                self.btn6.place(x=205, y=310)
                StateManagmentSubsystem.SaveWholeInformation(self)

            elif self.combobox1.get() == 'scatter':
                try:
                    if whole_information['visualization']['type_visualization'] == 'scatter' and \
                            whole_information['visualization']['x_axis'] == self.combobox2.get() and \
                            whole_information['visualization']['y_axis'] == self.combobox3.get():
                        self.image = Image.open(whole_information['visualization']['image'])
                        self.image = self.image.resize((600, 350), Image.ANTIALIAS)
                        self.image = ImageTk.PhotoImage(self.image)
                        self.file_path_img = whole_information['visualization']['image']
                        self.file_path_html = whole_information['visualization']['html']
                    else:
                        try:
                            fig = px.scatter(whole_information['data_recommenders'], x=self.combobox2.get(),
                                               y=self.combobox3.get())
                        except:
                            fig = px.scatter(data, x=self.combobox2.get(),
                                               y=self.combobox3.get())
                        self.file_path_img, self.file_path_html = StateManagmentSubsystem().SaveVisualizationSubsystemImj(fig)
                        self.image = Image.open(self.file_path_img)
                        self.image = self.image.resize((600, 300), Image.ANTIALIAS)
                        self.image = ImageTk.PhotoImage(self.image)
                except:
                    try:
                        fig = px.scatter(whole_information['data_recommenders'], x=self.combobox2.get(),
                                           y=self.combobox3.get())
                    except:
                        fig = px.scatter(data[:10], x=self.combobox2.get(), y=self.combobox3.get())
                    self.file_path_img, self.file_path_html = StateManagmentSubsystem().SaveVisualizationSubsystemImj(fig)
                    self.image = Image.open(self.file_path_img)
                    self.image = self.image.resize((600, 300), Image.ANTIALIAS)
                    self.image = ImageTk.PhotoImage(self.image)

                self.information['type_visualization'] = 'scatter'
                self.information['x_axis'] = self.combobox2.get()
                self.information['y_axis'] = self.combobox3.get()
                self.information['image'] = self.file_path_img
                self.information['html'] = self.file_path_html
                whole_information['visualization'] = self.information
                self.panel = Label(self.window1, image=self.image)
                self.panel.place(x=0, y=0)
                self.btn6 = Button(self.window1, text='Get interactive visualization', font=('Times new Roman', 12),
                               width=20,
                               command=self.Clicked_GetInteractiveVisualization)
                self.btn6.place(x=205, y=310)

                StateManagmentSubsystem.SaveWholeInformation(self)

    def Clicked_GetInteractiveVisualization(self):
            webbrowser.open(self.file_path_html)

    def Clicked_GoToUserInterface(self):
        self.window.destroy()
        StateTransitionSubsystem().GoToUserInterface()
    def Clicked_GoToDataLoadingSubsystem(self):
        self.window.destroy()
        StateTransitionSubsystem().GoToDataLoadingSubsystem()
    def Clicked_GoToRecommendersSubsystem(self):
        self.window.destroy()
        StateTransitionSubsystem().GoToRecommendersSubsystem()





class RecommendersSubsystem:
    def __init__(self):
        self.window = Tk()
        self.window.title('Recommendation system with data visualization. Recommendation Screen')
        self.window.geometry('600x400')
        self.window.iconbitmap('icon.ico')
        self.window.resizable(width=False, height=False)
        self.ShowRecommendersScreen()
        self.window.mainloop()
    def ShowRecommendersScreen(self):
        global data
        self.param_rdbtn = StringVar()
        self.param_rdbtn.set('max')
        self.list_of_parameters = list(data.columns.values)
        self.lbl1 = Label(self.window,
                          text='Select the parameter by which you can judge the advantage\n of one element over others:',
                          font=('Times New Roman', 16))
        self.lbl1.place(x=25, y = 5)
        self.combobox1 = ttk.Combobox(values =self.list_of_parameters, state="readonly")
        self.combobox1.place(x=25, y=65)
        self.lbl2 = Label(self.window,
                          text=f'Enter the number of recommendations (max = {data.shape[0]}):',
                          font=('Times New Roman', 16))
        self.lbl2.place(x=25, y=175)
        self.spinbox1 = ttk.Spinbox(from_=1, to= data.shape[0])
        self.spinbox1.place(x=25, y = 215)
        self.lbl3 = Label(self.window, text='Select the behavior of the key parameter:', font=('Times New Roman', 16))
        self.lbl3.place(x=25, y=105)
        self.rdbtn1 = Radiobutton(self.window, text='min', variable=self.param_rdbtn, value='min')
        self.rdbtn1.place(x=75, y=145)
        self.rdbtn2 = Radiobutton(self.window, text='max', variable=self.param_rdbtn, value='max')
        self.rdbtn2.place(x=25, y=145)
        self.btn1 = Button(self.window, text='Get recommendations', font=('Times new Roman', 12), width=20,
                           command=self.Clicked_GetRecommendations)
        self.btn1.place(x=205, y = 300)
        self.btn2 = Button(self.window, text='Go to Initial Screen', font=('Times new Roman', 12), width=20,
                           command=self.Clicked_GoToUserInterface)
        self.btn2.place(x=5, y=340)
        self.btn3 = Button(self.window, text='Go to Data Loading Screen', font=('Times new Roman', 12), width=20,
                           command=self.Clicked_GoToDataLoadingSubsystem)
        self.btn3.place(x=205, y=340)
        self.btn4 = Button(self.window, text='Go to Visualization Screen', font=('Times new Roman', 12), width=20,
                           command=self.Clicked_GoToVisualizationSubsystem)
        self.btn4.place(x=405, y=340)
        try:
            self.combobox1.set(whole_information['main_parameter'])
            self.spinbox1.set(whole_information['count'])
            self.param_rdbtn.set(whole_information['param_rdbtn'])
        except:
            None

    def Check_Float(self):
        try:
            float(self.spinbox1.get())
        except:
            return True
        return False

    def Check_Int(self):
        try:
            int(self.spinbox1.get())
        except:
            return True
        return False
    def Combine_Features(self, row):
        temp = ''
        for element in self.list_of_parameters:
            temp += str(row[element]) + ' '
        return temp

    def dismiss(self):
        self.window1.grab_release()
        self.window1.destroy()

    def Check_Type(self, data_temp):
        global data
        try:
            if self.param_rdbtn.get() == 'max':
                data = data_temp.sort_values(by=self.combobox1.get())
            else:
                data = data_temp.sort_values(by=self.combobox1.get(), ascending=False)
            return True
        except:
            return False

    def Clicked_GetRecommendations(self):
        global data
        global whole_information
        if self.combobox1.get() == '':
            tkinter.messagebox.showerror("Input Error",
                                         "No parameter was selected. Try again.")
        elif self.Check_Float():
            tkinter.messagebox.showerror("Input Error",
                                         "The entered string is not a number. Try again.")
        elif self.Check_Int():
            tkinter.messagebox.showerror("Input Error",
                                         "The entered number is not an integer. Try again.")
        elif int(self.spinbox1.get()) < 1 or int(self.spinbox1.get()) > data.shape[0]:
            tkinter.messagebox.showerror("Input Error",
                                         "The entered number is not included in the row range. Try again.")
        else:
            if self.Check_Type(data):
                data_recommenders = pd.DataFrame()
                try:
                    if whole_information['main_parameter'] == self.combobox1.get() and whole_information['count'] == int(self.spinbox1.get()) and whole_information['param_rdbtn']==self.param_rdbtn.get():
                        data_recommenders = whole_information['data_recommenders']
                    else:
                        features = self.list_of_parameters
                        for feature in features:
                            data[feature] = data[feature].fillna('')
                        data['combined_features'] = data.apply(self.Combine_Features,
                                                       axis=1)  # applying combined_features() method over each rows of dataframe and storing the combined string in “combined_features” column
                        cv = CountVectorizer()  # creating new CountVectorizer() object
                        count_matrix = cv.fit_transform(
                    data['combined_features'])  # feeding combined strings(movie contents) to CountVectorizer() object
                        cosine_sim = cosine_similarity(count_matrix)
                        index = 1
                        like = list(enumerate(cosine_sim[index]))
                        sorted_like = sorted(like, key=lambda x: x[1], reverse=True)[1:]

                        i = 0
                        indexes = []
                        indexes.append(index)
                        for element in sorted_like:
                           indexes.append(element[0])
                           i += 1
                           if i == int(self.spinbox1.get()):
                                break
                           data_recommenders = data.iloc[indexes]
                           whole_information['main_parameter'] = self.combobox1.get()
                           whole_information['count'] = int(self.spinbox1.get())
                           whole_information['data_recommenders'] = data_recommenders
                           whole_information['param_rdbtn']=self.param_rdbtn.get()
                           StateManagmentSubsystem.SaveWholeInformation()
                except:
                    features = self.list_of_parameters
                    for feature in features:
                        data[feature] = data[feature].fillna('')
                    data['combined_features'] = data.apply(self.Combine_Features,
                                                           axis=1)  # applying combined_features() method over each rows of dataframe and storing the combined string in “combined_features” column
                    cv = CountVectorizer()  # creating new CountVectorizer() object
                    count_matrix = cv.fit_transform(
                        data[
                            'combined_features'])  # feeding combined strings(movie contents) to CountVectorizer() object
                    cosine_sim = cosine_similarity(count_matrix)
                    index = 1
                    like = list(enumerate(cosine_sim[index]))
                    sorted_like = sorted(like, key=lambda x: x[1], reverse=True)[1:]
                    # data_recommenders = pd.DataFrame()
                    i = 0
                    indexes = []
                    indexes.append(index)
                    for element in sorted_like:
                        indexes.append(element[0])
                        i += 1
                        if i == int(self.spinbox1.get()):
                            break
                        data_recommenders = data.iloc[indexes]
                        whole_information['main_parameter'] = self.combobox1.get()
                        whole_information['count'] = int(self.spinbox1.get())
                        whole_information['data_recommenders'] = data_recommenders
                        whole_information['param_rdbtn'] = self.param_rdbtn.get()
                        StateManagmentSubsystem.SaveWholeInformation(self)
                try:
                    whole_information['visualization'] = dict()
                except:
                    None

                self.window1 = Toplevel()
                self.window1.title('Recommendation system with data visualization. Recommendation Screen')
                self.window1.geometry('600x300')
                self.window1.iconbitmap('icon.ico')
                self.window1.protocol("WM_DELETE_WINDOW", lambda: self.dismiss())
                self.window1.grab_set()
                # self.frame1 = ttk.Frame(self.window1)
                self.table1 = Table(self.window1, dataframe=data_recommenders,
                                    showtoolbar=False, showstatusbar=False)
                self.table1.show()
                self.table1.redraw()
            else:
                tkinter.messagebox.showerror("Input Error",
                                             "The difference is in the type of data in the key column. It needs to be fixed.")

    def Clicked_GoToUserInterface(self):
        self.window.destroy()
        StateTransitionSubsystem().GoToUserInterface()

    def Clicked_GoToDataLoadingSubsystem(self):
        self.window.destroy()
        StateTransitionSubsystem().GoToDataLoadingSubsystem()

    def Clicked_GoToVisualizationSubsystem(self):
        self.window.destroy()
        StateTransitionSubsystem().GoToVisualizationSubsystem()




class StateTransitionSubsystem:
    def GoToDataLoadingSubsystem(self):
        DataLoadingSubsystem()
    def GoToUserInterface(self):
        UserInterface()
    def GoToVisualizationSubsystem(self):
        VisualizationSubsystem()
    def GoToRecommendersSubsystem(self):
        RecommendersSubsystem()



class StateManagmentSubsystem:
    def RegisterSave(self, persons_dict):
        global temp_login
        login = temp_login
        fout = open('Persons_information.bin', 'wb')
        pickle.dump(persons_dict, fout)
        fout.close()
        if not os.path.isdir('AccountInformation\\' + login):
            os.mkdir('AccountInformation\\' + login)
        if not os.path.isdir('AccountInformation\\' + login + '\\Datasets'):
            os.mkdir('AccountInformation\\' + login + '\\Datasets')
        if not os.path.isdir('AccountInformation\\' + login + '\\Models'):
            os.mkdir('AccountInformation\\' + login + '\\Models')
        if not os.path.isdir('AccountInformation\\' + login + '\\Visualizations'):
            os.mkdir('AccountInformation\\' + login + '\\Visualizations')

    def LoadLogInInformation(self):
        fin = open('Persons_information.bin', 'rb')
        persons_dict = pickle.load(fin)
        fin.close()
        return persons_dict

    def SaveWholeInformation(self):
        global temp_login
        global whole_information
        fout = open('AccountInformation\\' + temp_login + '\\information.bin', 'wb')
        pickle.dump(whole_information, fout)
        fout.close()


    def SaveDataLoadingSubsystemFile(self, filepath):
        global temp_login
        index = 1
        k = 0
        while True:
            if filepath[len(filepath) - k - 1:-k] == '.':
                break
            k += 1
        if os.path.isfile(
                'AccountInformation\\' + temp_login + '\\Datasets' + '\\data' + filepath[len(filepath) - k - 1:]):
            while True:
                if not os.path.isfile(
                        'AccountInformation\\' + temp_login + '\\Datasets' + '\\data' + str(index) + filepath[
                                                                                                     len(filepath) - k - 1:]):
                    shutil.copyfile(filepath, 'AccountInformation\\' + temp_login + '\\Datasets' + '\\data' + str(
                        index) + filepath[len(filepath) - k - 1:])
                    break
                index += 1
        else:
            shutil.copyfile(filepath, 'AccountInformation\\' + temp_login + '\\Datasets' + '\\data' + filepath[
                                                                                                      len(filepath) - k - 1:])

    def DownloadDataLoadingSubsystemWholeInformation(self):
        global temp_login
        fin = open('AccountInformation\\' + temp_login + '\\information.bin', 'rb')
        whole_information = pickle.load(fin)
        fin.close()
        return whole_information

    def SaveVisualizationSubsystemImj(self, fig):
        global temp_login
        index = 1
        file_path_img = ''
        file_path_html = ''
        if os.path.isfile(
                'AccountInformation\\' + temp_login + '\\Visualizations' + '\\Visualization.html'):
            while True:
                if not os.path.isfile(
                        'AccountInformation\\' + temp_login + '\\Visualizations' + '\\Visualization' + str(
                            index) + ".html"):
                    fig.write_html(
                        'AccountInformation\\' + temp_login + '\\Visualizations' + '\\Visualization' + str(
                            index) + ".html")
                    hti = Html2Image(
                        output_path='AccountInformation\\' + temp_login + '\\Visualizations')
                    hti.screenshot(
                        html_file='AccountInformation\\' + temp_login + '\\Visualizations' + '\\Visualization' + str(
                            index) + ".html",
                        save_as='Visualization' + str(index) + ".jpg")
                    file_path_img = 'AccountInformation\\' + temp_login + '\\Visualizations' + '\\Visualization' + str(
                        index) + ".jpg"
                    file_path_html = 'AccountInformation\\' + temp_login + '\\Visualizations' + '\\Visualization' + str(
                        index) + ".html"
                    break
                index += 1
        else:
            fig.write_html(
                'AccountInformation\\' + temp_login + '\\Visualizations' + '\\Visualization.html')
            hti = Html2Image(output_path='AccountInformation\\' + temp_login + '\\Visualizations')
            hti.screenshot(
                html_file='AccountInformation\\' + temp_login + '\\Visualizations' + '\\Visualization.html',
                save_as='Visualization.jpg')
            file_path_img = 'AccountInformation\\' + temp_login + '\\Visualizations' + '\\Visualization' + ".jpg"
            file_path_html = 'AccountInformation\\' + temp_login + '\\Visualizations' + '\\Visualization' + ".html"

        return file_path_img, file_path_html



if __name__ == '__main__':
    if not os.path.isfile('Persons_information.bin'):
        tempf = open('Persons_information.bin', 'wb')
        tempf.close()
    if os.stat('Persons_information.bin').st_size == 0:
        fout = open('Persons_information.bin', 'wb')
        persons_dict = dict()
        persons_dict['admin'] = 'admin'
        pickle.dump(persons_dict, fout)
        fout.close()
    if not os.path.isdir('AccountInformation'):
        os.mkdir('AccountInformation')
    UserInterface()






'''
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
def combine_features(row):
    return str(row['id'])+ ' ' +str(row['prices.amountMax'])+' '+str(row['prices.amountMin'])+' '+str(row['prices.availability'])+' '+str(row['prices.condition'])+' '+str(row['prices.currency'])+' '+str(row['prices.dateSeen'])+' '+str(row['prices.isSale'])+' '+str(row['prices.merchant'])+' '+str(row['prices.shipping'])+' '+str(row['prices.sourceURLs'])+' '+str(row['asins'])+' '+str(row['brand'])+' '+str(row['categories'])+' '+str(row['dateAdded'])+' '+str(row['dateUpdated'])+' '+str(row['ean'])+' '+str(row['imageURLs'])+' '+str(row['keys'])+' '+str(row['manufacturer'])+' '+str(row['manufacturerNumber'])+' '+str(row['name'])+' '+str(row['primaryCategories'])+' '+str(row['sourceURLs'])+' '+str(row['upc'])+' '+str(row['weight'])
text = ['Лондон, Париж, Лондон', 'Париж, Париж, Лондон']
cv = CountVectorizer()
count_matrix = cv.fit_transform(text)
print(cv.get_feature_names_out())
print(count_matrix.toarray())
similarity_scores = cosine_similarity(count_matrix)
print(similarity_scores)
df = pd.read_csv('D:\\4 курс БГУ ФПМИ 2 семестр\\Диплом\\DatafinitiElectronicsProductsPricingData.csv')
features = ['id','prices.amountMax','prices.amountMin','prices.availability','prices.condition','prices.currency','prices.dateSeen','prices.isSale','prices.merchant','prices.shipping','prices.sourceURLs','asins','brand','categories','dateAdded','dateUpdated','ean','imageURLs','keys','manufacturer','manufacturerNumber','name','primaryCategories','sourceURLs','upc','weight']
for feature in features:
    df[feature] = df[feature].fillna('')
df['combined_features'] = df.apply(combine_features,axis=1) #applying combined_features() method over each rows of dataframe and storing the combined string in “combined_features” column
cv = CountVectorizer() #creating new CountVectorizer() object
count_matrix = cv.fit_transform(df['combined_features']) #feeding combined strings(movie contents) to CountVectorizer() object
cosine_sim = cosine_similarity(count_matrix)
index = 1
like = list(enumerate(cosine_sim[index]))
sorted_like = sorted(like,key=lambda x:x[1],reverse=True)[1:]
i=0
print('Top 5 like '+ str(index) + ' are:\n')
for element in sorted_like:
    print(element[0])
    i=i+1
    if i>5:
        break
'''



'''import numpy as np
import pandas as pd
if not os.path.exists("D:\\4 курс БГУ ФПМИ 2 семестр\\Диплом\\Картинки"):
    os.mkdir("D:\\4 курс БГУ ФПМИ 2 семестр\\Диплом\\Картинки")
df = pd.read_excel('D:\\4 курс БГУ ФПМИ 2 семестр\\Диплом\\Книга1.xlsx')
import plotly.express as px
import plotly
df1 = df[:100]
fig = px.pie(df1, names="id", values='prices.amountMax')
#fig.write_html("D:\\4 курс БГУ ФПМИ 2 семестр\\Диплом\\Картники\\file.html")
from html2image import Html2Image
hti = Html2Image(output_path='D:\\4 курс БГУ ФПМИ 2 семестр\\Диплом\\Картники')

hti.screenshot(html_file='D:\\4 курс БГУ ФПМИ 2 семестр\\Диплом\\Картники\\file.html', save_as='file_new.png')
'''






'''
fig = px.histogram(df1, x="id", y='prices.amountMax')
fig.to_image(format="jpg", engine="kaleido")
'''



#root.withdraw()