import cv2
import face_recognition
from pymongo import MongoClient
import time
import numpy as np
import tkinter as tk
from tkinter import *
import database_program
import datetime
import os

client=MongoClient()
db=client.vbdhas
known_encodings_coll=db.KnownEncodings
unknown_encodings_coll=db.UnknownEncodings

database_program.initialize_colection(known_encodings_coll, unknown_encodings_coll)

known_face_encodings_dict=known_encodings_coll.find()
for i in known_face_encodings_dict:
    known_face_encodings=i["encodings"]
    known_face_names=i["names"]
    known_face_count=i["count"]
    known_face_time=i["time"]
    break

unknown_face_encodings_dict=unknown_encodings_coll.find()
for i in unknown_face_encodings_dict:
    unknown_face_encodings=i["encodings"]
    unknown_face_names=i["names"]
    unknown_face_count=i["count"]
    unknown_face_time=i["time"]
    break

def save_frame(current_face_name, frame, time):
    curr_dir=os.path.dirname(__file__)
    image_dir=os.path.join(curr_dir, current_face_name)
    if current_face_name not in os.listdir(curr_dir):
        os.mkdir(image_dir)
    img_name=f"{current_face_name}{time}.jpg"
    #img_name="1,2.jpg"
    cv2.imwrite(os.path.join(image_dir, img_name), frame)
    print("Image Saved")


def person_name_popup(root):
    text_font=("Courier", 16, "bold")
    name_of_person="Blank"
    def submit():
        nonlocal name_of_person
        name_of_person=name_entry.get()

        pop.destroy()
        
    pop=Toplevel()
    pop.title("Person Name")
    root_height=root.winfo_height()
    root_width=root.winfo_width()
    left_pos=int((root_width/2)-(350/2))
    top_pos=int((root_height/2)-250)
    pop.geometry(f"350x250+{left_pos}+{top_pos}")
    pop.configure(background='gray72')

    name_label=Label(pop, text="Enter name of person")
    name_label.configure(background='gray72', font=text_font, fg='ghost white')
    name_label.pack()
    name_entry=StringVar()


    Entry(pop, textvariable=name_entry).pack()

    b=Button(pop, text="DONE", command=submit)
    b.configure(relief=GROOVE, bg='gray3', padx=5, pady=2, fg='ghost white')
    b.pack()
    
    root.wait_window(pop)
    print(name_of_person)
    return name_of_person

def draw_rectangle(frame, left, top, right, bottom, name_of_person):
    cv2.rectangle(frame, (left, top), (right, bottom), (0,0,255), 1)
    cv2.rectangle(frame, (left, bottom-15), (right, bottom), (0,0,255), cv2.FILLED)
    font=cv2.FONT_HERSHEY_DUPLEX
    cv2.putText(frame, name_of_person, (left+10, bottom-5), font, 0.5, (255,255,255), 1 )

def frame_process(frame, root):
   
    process_this_frame=True
    face_names=[]
    last_seen=[]

    #while True:
                
    small_frame=cv2.resize(frame, (0,0), fx=0.10, fy=0.10)
    rgb_frame=small_frame[:, :, ::-1]

    if process_this_frame==True:
        all_face_location=face_recognition.face_locations(img=rgb_frame, number_of_times_to_upsample=5, model="hog")
        print(f"face Locations: {all_face_location}")
        all_face_encodings=face_recognition.face_encodings(rgb_frame, all_face_location)
        t=datetime.datetime.now().replace(microsecond=0).strftime("%d %b %Y, %H-%M-%S")
        for current_encoding in all_face_encodings: 

            name_of_person="Unknown"

            all_matches=face_recognition.compare_faces(known_face_encodings, current_encoding)

            all_unknown_matches=face_recognition.compare_faces(unknown_face_encodings, current_encoding)


            if True in all_matches:
                first_face=all_matches.index(True)
                name_of_person=known_face_names[first_face]
                known_face_count[first_face]+=1

                last_seen.append(known_face_time[first_face][-1])

                known_face_time[first_face].append(t)
                known_encodings_coll.update_one({"id":1}, {"$set" :{"count" : known_face_count}})
                known_encodings_coll.update_one({"id":1}, {"$set" :{"time" : known_face_time}})
                #last_seen[first_face]=t
                
                
                    
            elif True in all_unknown_matches:
                first_face=all_unknown_matches.index(True)
                if unknown_face_count[first_face]>=4:
                   
                    name_of_person=person_name_popup(root)
                    
                    known_face_encodings.append(current_encoding.tolist())
                    known_face_names.append(name_of_person)
                    known_face_count.append(1)
                    last_seen.append(unknown_face_time[first_face][-1])
                    known_face_time.append(unknown_face_time[first_face])

                    known_encodings_coll.update_one({"id":1}, {"$set" :{"encodings":known_face_encodings}})                
                    known_encodings_coll.update_one({"id":1}, {"$set" :{"names":known_face_names}}) 
                    known_encodings_coll.update_one({"id":1}, {"$set" :{"count" : known_face_count}})
                    known_encodings_coll.update_one({"id":1}, {"$set" :{"time" : known_face_time}})
            
                    
                    unknown_face_encodings.pop(first_face)
                    unknown_face_count.pop(first_face)
                    unknown_face_time.pop(first_face)
                    unknown_encodings_coll.update_one({"id":1}, {"$set" :{"encodings":unknown_face_encodings}})
                    unknown_encodings_coll.update_one({"id":1}, {"$set" :{"count":unknown_face_count}})
                    unknown_encodings_coll.update_one({"id":1}, {"$set" :{"time":unknown_face_time}})   
                    #last_seen[first_face]=t
                    #last_seen.append(t)
                    
                else:
                    unknown_face_count[first_face]+=1
                    last_seen.append(unknown_face_time[first_face][-1])
                    unknown_face_time[first_face].append(t)
                    unknown_encodings_coll.update_one({"id":1}, {"$set" :{"count":unknown_face_count}})
                    unknown_encodings_coll.update_one({"id":1}, {"$set" :{"time":unknown_face_time}})
                    print(f"In unknown else block: {unknown_face_count}")
                    print(f"In unknown else block: {unknown_face_time}")
                    #last_seen.append(t)
                    #last_seen[first_face]=t

            else:
                unknown_face_encodings.append(current_encoding.tolist())
                unknown_face_count.append(1)
                unknown_face_time.append([t])
                last_seen.append("NO Last visits")
                
                
                print("encodings appended")
                
                unknown_encodings_coll.update_one({"id":1}, {"$set" :{"encodings":unknown_face_encodings}})
                unknown_encodings_coll.update_one({"id":1}, {"$set" :{"count":unknown_face_count}})
                unknown_encodings_coll.update_one({"id":1}, {"$set" :{"time":unknown_face_time}})
                print(f"FIrst Step: {unknown_face_count}")
                print(f"FIrst Step: {unknown_face_time}")
                last_seen.append(t)
            face_names.append(name_of_person)
            
            
            
            
    process_this_frame=not process_this_frame

    for current_face, current_face_name, time in zip(all_face_location, face_names, last_seen):
        top, right, bottom, left=current_face
        top=top*10
        right=right*10
        bottom=bottom*10
        left=left*10
        draw_rectangle(frame, left, top, right, bottom, current_face_name)
        save_frame(current_face_name, frame, time)

    return frame, face_names, last_seen
