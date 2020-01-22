## Colloscope - Reorganizing a timetable for clarity

A colloscope is a timetable for a class of 45 students
showing when and where each
group of three students (numbered 1 to 15) has a "colle"
(a 1-hour lesson).

The colloscope provided by my teacher (shown below) was a single Excel spreadsheet, 
containing information for every group.

<p align="center"><img src="https://github.com/loic-lescoat/showcase/blob/master/Colloscope/img/screenshot_of_excel_file_colloscope.png"
 height=500 alt="screenshot_of_excel_file_colloscope.png"></img></p>


This format has a few disadvantages.
 As a student, it's hard to find the information you need, as this 
requires searching through the table for the correct group number. 
The Excel spreadsheet contains a lot of unnecessary information about other groups.

The code from the Colloscope project parses the Excel spreadsheet, 
stores the information in a database for later use, then generates a 
personnalized colloscope - one PDF for each group - containing
 only information that is
relevant to the student reading the PDF.

<p align="center"><img src="https://github.com/loic-lescoat/showcase/blob/master/Colloscope/img/screenshot_of_group_15_s_pdf.jpg"
 height=500 alt="screenshot_of_group_15_s_PDF.jpg"></img></p>
 
 A screenshot of a PDF generated automatically.
