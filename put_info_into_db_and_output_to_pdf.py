import os

OUTPUT_VERSION = os.environ.get('OUTPUT_VERSION')
print("version_no = " + OUTPUT_VERSION)



import extract_info
import output_info

# next lines: put colle info into db
extract_info.put_colles_info_into_db()
extract_info.put_group_members_info_into_db()
extract_info.put_week_info_into_db()

output_info.output_all_timetables_to_pdf()
