import sqlite3
import datetime
import shutil
import os

import extract_info
import pdfkit

OUTPUT_VERSION = os.environ.get('OUTPUT_VERSION')


def generate_timetable(group): # divide into steps!
    """generates_timetable from [current week] onward"""
    with open("colloscope template.html", 'r', encoding="UTF-8") as template:
        res = template.read()
    inner_html = "" # html to insert into template
    # see "insert inner_html_here" in template
    conn = sqlite3.connect("colloscope.db")
    current_week = get_current_week()
    max_week = get_max_week(conn, group)
    # timetable will be made from current week
    # to max_week (inclusive)
    for week in range(current_week, max_week + 1):
        command = """SELECT *
                    FROM colles
                    WHERE colle_group = %s
                    AND week = %s;""" % (group, week)
        colles_unsorted = conn.execute(command).fetchall()
        colles = sort_by_time(colles_unsorted)
        inner_html = inner_html + generate_row(colles)

    res = res.replace("<!-- insert names here -->", generate_html_code_for_names(group))
    res = res.replace('<!-- insert inner_html_here -->', \
    inner_html)

    res = res.replace("{number}", str(group))
    return res

    conn.close()

def generate_row(colles):
    """returns html code to insert into timetable for given group and week"""
    res = "<tr>\n" + generate_row_header(colles) \
    + generate_all_lines(colles) + "\n</tr>"
    return res

def generate_all_lines(colles):
    """returns all lines for given week"""
    res = ""
    for i in range(len(colles)):
        res = res + generate_line_for_colle(colles, i)
    return res

def generate_row_header(colles):
    """returns td which serves as header"""
    # fetch info we need
    num_colles = len(colles)
    week = colles[0][2]
    w = extract_info.get_week(week)
    monday = w[0]
    friday = w[1]
    # fill in skeleton with info
    skeleton = """<td rowspan="{}">
        <p class="week_number">{}</p>
        du {}</br>
        au {}
      </td>"""
    res = skeleton.format(num_colles, week, \
                        monday, friday)
    return res

def generate_line_for_colle(colles, index):
    """return html code for line corresponding to colle (without row header), as identified by index (0-indexed: 0 is 1st colle of week, etc))"""
    # fetch necessary info
    colle = colles[index]
    day_time = colle[3]
    subject = colle[1]
    colleur = colle[4]
    room = colle[5]

    # put it in skeleton
    skeleton = """<td>
        <i>{}</i>
      </td>
      <td>
        <i>{}</i>
      </td>
      <td>
        <i>{}</i>
      </td>
      <td>
        <i>{}</i>
      </td>
      </tr>
    """
    if index > 0:
        skeleton = "<tr>\n" + skeleton

    res = skeleton.format(day_time, subject, \
                        colleur, room)
    return res

def generate_html_code_for_names(group):
    """returns html code used to represent names, in top right corner of pdf"""
    people = extract_info.get_members(group)
    skeleton = """<div id="wrapper">
    {inner_html}
    </div>"""
    inner_html = ""
    for p in people:
        inner_html = inner_html + \
        '<p class="name">%s</p>\n' % p
    res = skeleton.replace("{inner_html}", inner_html)
    return res

def week_is_over(week_num):
    """returns True iff Friday of the week week_num is (strictly) before today or week_num is not one of weeks on which we have colles"""
    if not extract_info.get_week(week_num)[1]:
        return True
    today = datetime.date.today()
    friday_of_week_num = datetime.datetime.strptime(extract_info.get_week(week_num)[1], \
    '%d/%m/%Y').date()
    return friday_of_week_num < today


def get_current_week():
    """returns current week number; more specifically,
    returns number of week of first Friday after now; number returned refers to a week during which we have colles"""
    # res = min([week_num for week_num in range(53) if not week_is_over(week_num)]) # for use before June 2018
    res = 16 # hardcoded for use after June 2018
    return res

def get_max_week(conn, group):
    """returns max week where group has colles"""
    res = 0
    for week in range(52):
        command = """SELECT *
                    FROM colles
                    WHERE colle_group = {}
                    AND week = {};""".format(group, week)
        colles = conn.execute(command).fetchall()
        if len(colles) > 0:
            res = week
    return res

def day_to_num(day):
    """returns string of index of day in week
    lundi --> 0, mardi --> 1, etc..."""
    day = day.lower()
    days = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi']
    return str(days.index(day))


def sort_by_time(lc):
    """Pass list of colles of a given week as input
    returns list of colles sorted by time
    eg: [colle on Wed at 2pm, colle on Tue at 6pm]
    becomes [colle on Tue at 6pm, colle on Wed at 2pm]"""
    lm = [x for x in lc]
    # lm = [('2', 'Physique', 18, 'Mercredi 16h30', 'Mme Daumont', 'P4 (L109)'), ('2', 'Anglais', 18, 'Mercredi 14h30', 'M. Dewa\xeble', '?'), ('2', 'Fran\xe7ais', 18, 'Jeudi 17h30', 'M. Robert', '?')] # for testing
    for i in range(len(lm)): # lm[i] is each colle
        day_time = lm[i][3].split(' ')
        lm[i] = lm[i] + (day_to_num(day_time[0]),) # (i)
        lm[i] = lm[i] + (day_time[1],)
    lm.sort(key=lambda x: (x[-2], x[-1])) # sort by day, then by time

    for i in range(len(lm)):
        lm[i] = lm[i][:-2] # removes added items (i)
    return lm


def prepare_output_dir():
    dirname = './out/ver%s/' % OUTPUT_VERSION
    if os.path.exists(dirname):
        shutil.rmtree(dirname)
    os.mkdir(dirname)
    os.mkdir(dirname + 'html')
    os.mkdir(dirname + 'pdf')

def output_all_timetables_to_pdf():
    prepare_output_dir()
    print("Generating html files...")
    for i in range(1, 16):
        a=generate_timetable(i)
        print(a, file=open('out/ver{}/html/Groupe {}.html'.format(OUTPUT_VERSION, str(i)), 'w', encoding='utf-8'))

    print("Converting html files to pdf format...")
    for i in range(1, 16):
        pdfkit.from_file('out/ver{}/html/Groupe {}.html'.format(OUTPUT_VERSION, str(i)), 'out/ver{}/pdf/Groupe {}.pdf'.format(OUTPUT_VERSION, str(i)))
