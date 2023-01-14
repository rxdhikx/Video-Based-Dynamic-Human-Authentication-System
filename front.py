from tkinter import *
import tkinter as tk
from tkinter.font import Font
import cv2
from PIL import Image, ImageTk
import face_recognition
import back as fc
import os
from pymongo import MongoClient

client=MongoClient()
db=client.vbdhas
known_encodings_coll=db.KnownEncodings
unknown_encodings_coll=db.UnknownEncodings


width, height=800 , 600
cam=cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, height)


root=tk.Tk()
text_font=("Courier", 16, "bold")

face_names=[]
last_seen=[]

root.bind('<Escape>', lambda e: root.quit())

lmain=tk.Label(root)
lmain.pack()

screen_height=root.winfo_screenheight()
screen_width=root.winfo_screenwidth()
root_width=1000
root_height=750
root_top=int((screen_height/2)-(root_height/2))
root_left=int((screen_width/2)-(root_width/2))

root.geometry(f"{root_width}x{root_height}+{root_left}+{root_top}")
root.configure(background='gray20')


def flash():
    root.configure(background='red2')
    root.after(500, lambda:root.configure(background='gray20'))

def show_frame():
    
    _, frame=cam.read()
    frame = cv2.flip(frame, 1)
    #Recognition function
    global face_names
    global last_seen
    new_frame, face_names, last_seen =fc.frame_process(frame, root)

    if "Unknown" in face_names:
        flash()


    print(face_names)
    print(last_seen)
    user_data()
    
    cv2image = cv2.cvtColor(new_frame, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    lmain.after(10, show_frame)
    

def user_data():
    def view_log():
        log_screen=Toplevel()
        log_screen.title("Log of ")
        log_screen.geometry("550x750")
        
        known_encodings_coll_dict=known_encodings_coll.find()
        unknown_encodings_coll_dict=unknown_encodings_coll.find()

        for i in known_encodings_coll_dict:
            known_face_time=i["time"]
            known_face_name=i["names"]

        for i in unknown_encodings_coll_dict:
            unknown_face_time=i["time"]
            unknown_face_name=i["names"]

        
        if name in known_face_time:
            ind=known_face_name[name]
            lst=[]
            for i in range(len(known_face_time[ind])):
                lst.append((i+1, known_face_time[ind][i]))
                for j in range(2):
                    
                    e = Entry(log_screen, width=20, fg='blue',font=('Arial',16,'bold'))
                    e.grid(row=i, column=j)
                    e.insert(END, lst[i][j])
            print(lst)
        else:

            lst=[]
            for i in range(len(unknown_face_time)):
                lst.append((i+1, unknown_face_time[i]))
                for j in range(2):
                    e = Entry(log_screen, width=20, fg='blue',font=('Arial',16,'bold'))
                    e.grid(row=i, column=j)
                    e.insert(END, lst[i][j])
        


    for name, time in zip(face_names, last_seen):
        text_to_display=f'Name: {name} \n \nLast Seen: {time}'
        """
        curr_dir=os.path.dirname(__file__)
        image_dir=os.path.join(curr_dir, name)
        image_name=f"{name}{time}.jpg"
        image=ImageTk.PhotoImage(Image.open(os.path.join(image_dir, image_name)))

        canvas=Canvas(root, width=80, height=80)
        canvas.create_image(20,20, image=image)

        canvas.pack()
        canvas.after(3000, lambda:name_message.destroy())
        """
        name_message=Message(root, text=text_to_display, font=text_font, width=600, borderwidth=5, justify=LEFT, background='light blue', relief=RIDGE)
        name_message.pack()

        log_button=Button(root, text="View Log", command=view_log)
        log_button.configure(relief=GROOVE, bg='gray3', padx=5, pady=2, fg='ghost white')
        log_button.after(2000, lambda:log_button.destroy())
        log_button.pack()

        name_message.after(3000, lambda:name_message.destroy())


show_frame()
#user_data()


root.mainloop()
