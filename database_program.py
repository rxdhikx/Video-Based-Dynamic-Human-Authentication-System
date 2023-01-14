from pymongo import MongoClient
import face_recognition


def initialize_colection(known_encodings_coll, unknown_encodings_coll):
    if known_encodings_coll.count()==0:
        known_coll={
            "id":1,
            "encodings":[],
            "names": [], 
            "count" :[],
            "time" :[]
        }


        known_encodings_coll.insert_one(known_coll)

    if unknown_encodings_coll.count()==0:
        unknown_coll={
            "id":1,
            "encodings":[],
            "names":[],
            "count": [], 
            "time":[]
        }
        unknown_encodings_coll.insert_one(unknown_coll)




    