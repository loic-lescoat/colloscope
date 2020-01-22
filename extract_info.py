import sqlite3
import os
import csv
import json
import datetime


OUTPUT_VERSION = os.environ.get('OUTPUT_VERSION')


colloscope_db = "colloscope.db"
infos_dir = './infos/ver%s/' % OUTPUT_VERSION
max_group_number = 16 # left at 16 for simpler handling
max_text_size = str(20) # at marker i; group 16 does not really exist



def extract_colles_info():
    data_file = open(infos_dir + "colles.csv", 'r', encoding="UTF-8")
    
    csv_reader = csv.reader(data_file, delimiter=",")
    csv_reader_list = list(csv_reader)
    
    groups = [[] for x in range(max_group_number + 1)] 

    
    for row in csv_reader_list:
        if content_of_cell_1(row) == "colleur id":
            # only go thru rows with colles in them
            subject = get_subject(csv_reader_list, row)
            day_time = row[2]
            colleur = row[3]
            room = row[1]
            if room == "":
                room = "?"
            # week is defined below
            
            for i in range(4, 17): # group is a group number

                week = csv_reader_list[0][i]
                group = row[i]
                if group == "":
                    group = 0 # group for empty cells
                groups[int(group)].append([subject, week, day_time, colleur, room]) # marker i
    data_file.close()
    return groups

def put_colles_info_into_db(): # replaces existing data
    conn = sqlite3.connect(colloscope_db)
    conn.execute("""DROP TABLE IF EXISTS colles;""")
    
    groups = extract_colles_info()
    
    conn.execute("""CREATE TABLE colles
    (colle_group VARCHAR({max}),
    subject VARCHAR({max}),
    week INTEGER,
    day_time VARCHAR({max}),
    colleur VARCHAR({max}),
    room VARCHAR({max}))""".format(max=max_text_size))
    
    for i in range(1, 16): # add groups 1 to 15 colles
        for j in groups[i]:
            conn.execute("""INSERT INTO colles VALUES
        %s""" % str(tuple([i] + j)))
        

    conn.commit()
    conn.close()


def content_of_cell_1(row):
    """returns content type of cell 1 of row"""
    if row[0] == "":
        return "empty"
    elif 0 < len(row[0]) <= 6 and row[0] != "Chimie":
        return "colleur id"
    elif row[0] != "Semaine":
        return "subject"
    else:
        return "other"

def get_subject(_csv_reader_list, row):
    """Returns subject (in first column) that is closest above line passed as row"""
    index = _csv_reader_list.index(row)# assumes all lines
    while index > 0:                   # are !=
        if content_of_cell_1(_csv_reader_list[index])\
         == 'subject':
            return _csv_reader_list[index][0]
        index -= 1
    
def get_group_number(_csv_reader_list, row):
    """Returns group number (in first column) that is closest above line passed as row"""
    index = _csv_reader_list.index(row) # assumes no two lines are identical
    while index > 0:
        cell_1 = _csv_reader_list[index][0]
        if "Groupe" in cell_1:
            return cell_1.split(" ")[-1]
        index -= 1

def extract_group_members_info():
    """get info about all groups and their members"""
    colles_groups_file = open(infos_dir + 'groupes.csv', \
     'r', encoding="UTF-8")
    csv_reader_list = list(csv.reader(colles_groups_file,\
     delimiter=","))
    
    groups = [[] for i in range(max_group_number + 1)]
    
    for row in csv_reader_list[2:]: # groups start on line 3
        if any(row):
            group_number = int(get_group_number( \
            csv_reader_list, row))
            
            last_name = row[1]
            first_name = row[2]
            LV1 = row[3]
            LV2 = row[4]
            
            groups[group_number].append([last_name, \
            first_name, LV1, LV2])
    colles_groups_file.close()
    return groups
    
def put_group_members_info_into_db():
    groups = extract_group_members_info()
    conn = sqlite3.connect(colloscope_db)
    
    conn.execute("""DROP TABLE IF EXISTS groups""")
    
    conn.execute("""CREATE TABLE groups
    (number INTEGER,
    last_name VARCHAR({max}),
    first_name VARCHAR({max}),
    lv1 VARCHAR({max}),
    lv2 VARCHAR({max}))""".format(max=max_text_size))
    
    for i in range(1, 16): # adds groups 1 to 15's info
        for person in groups[i]:
            conn.execute("""INSERT INTO groups VALUES
            %s;""" % str(tuple([i] + person)))
    
    
    conn.commit()
    conn.close()



def put_week_info_into_db():
    conn = sqlite3.connect("colloscope.db")
    conn.execute("""DROP TABLE IF EXISTS weeks""")
    conn.execute ("""CREATE TABLE weeks
                (week INTEGER,
                monday TEXT,
                friday TEXT)""")
    week_file = open(infos_dir + "calendrier.csv", 'r', encoding="UTF-8")
    csv_reader_list = list(csv.reader(week_file, \
     delimiter=","))
    for row in csv_reader_list:
        if "Semaine" in row[0][:7]:
            week_num = row[0].split(' ')[-1]
            monday = row[1]
            
            date_1 = datetime.datetime.strptime(monday, \
            "%d/%m/%Y")
            end_date = date_1 + datetime.timedelta(days=4)
            day = str(end_date.day)
            if len(day) == 1:
                day = "0" + day
            month = str(end_date.month)
            if len(month) == 1:
                month = "0" + month
            friday = day + '/' + \
                    month + '/' + \
                    str(end_date.year)

            conn.execute("""INSERT INTO weeks VALUES
            %s""" % str((week_num, monday, friday)))
    fill_in_missing_weeks(conn)
    conn.commit()
    conn.close()

def fill_in_missing_weeks(conn):
    """fills in blanks in weeks 0 to 52
    conn is an object returned by sqlite3.connect()"""
    for i in range(53):
        resp = conn.execute("""SELECT week
        FROM weeks WHERE week = %s;""" % str(i))
        if not resp.fetchall():
            conn.execute("""INSERT INTO weeks
            VALUES (%s, NULL, NULL)""" % str(i))
    conn.commit()

def get_week(week_num):
    """returns tuple containing dates (monday, friday) corresponding to week_num"""
    conn = sqlite3.connect("colloscope.db")
    a = conn.execute("""SELECT monday, friday
    FROM weeks
    WHERE week = %s;""" % week_num)
    res = a.fetchone()
    return res
    
    conn.close()

def get_members(group):
    """returns members belonging to group"""
    conn = sqlite3.connect("colloscope.db")
    command = """SELECT first_name, last_name
                FROM groups
                WHERE number = %s;""" % group
    people_raw = conn.execute(command).fetchall()
    people = [p[0] + ' ' + p[1] for p in people_raw]
    conn.close()
    return people
