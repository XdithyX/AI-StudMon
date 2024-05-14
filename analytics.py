# import db_connect
from collections import Counter
from datetime import datetime, timedelta
# connection = db_connect.connect_to_supabase()
# cur = connection[0]
# conn = connection[1]

def derive_analytics(tabname,cur):
    try:
        # Execute SQL query to fetch data from the database within the specified time interval
        query = f"SELECT student_name, emotion FROM {tabname}"
        # query = f"SELECT student_name, emotion FROM {tname} WHERE timestamp BETWEEN %s AND %s"
        cur.execute(query)

        # Fetch all rows from the result set
        rows = cur.fetchall()

        total_students = 0
        student_reports = {}

        if len(rows)==0:
            print("No Emotions Detected , Empty table!!!")
            return()
            
        # Process the fetched data
        for student, emotion in rows:
            if student != 'Unknown' and student != 'unknown':
                if student not in student_reports:
                    total_students += 1
                    student_reports[student] = {'total_emotions': 0, 'emotions_count': Counter(), 'prominent_emotion': '','understanding': 0, 'notunderstanding':0}
                
                # Update emotions count
                student_reports[student]['emotions_count'][emotion] += 1
                student_reports[student]['total_emotions'] += 1
                if emotion in ['Happy', 'Neutral']:
                    student_reports[student]['understanding'] += 1
                else:
                    student_reports[student]['notunderstanding'] += 1

        # Calculate percentages and prominent emotions
        studproemo=Counter()
        count_of_understoods=0
        comp_level_list=[]
        non_comp_level_list=[]
        if not bool(student_reports):
            return()
        for student, report in student_reports.items():
            #calculating comprehention percentage
            report['understanding']=(report['understanding']/report['total_emotions'])*100
            comp_level_list.append(report['understanding'])
            if report['understanding'] >= 60:
                count_of_understoods += 1

            report['notunderstanding']=(report['notunderstanding']/report['total_emotions'])*100
            non_comp_level_list.append(report['notunderstanding'])

            # Calculate emotion percentages for each student
            total_student_emotions = report['total_emotions']
            for emotion, count in report['emotions_count'].items():
                report['emotions_count'][emotion] = (count / total_student_emotions) * 100
            
            # Determine prominent emotion for each student
            prominent_emotion = report['emotions_count'].most_common(1)
            report['prominent_emotion'] = prominent_emotion[0][0]
            if prominent_emotion[0][0] not in studproemo:
                studproemo[prominent_emotion[0][0]] =0

            studproemo[prominent_emotion[0][0]] += 1
        
        # Calculate percentages of each emotion for the entire class
        class_emotions_percentages = {emotion: (count / total_students) * 100 for emotion, count in studproemo.items()}

        # Determine prominent emotion for the entire class
        prominent_class_emotion = studproemo.most_common(1)[0][0]
        comprehenssion_level_of_class = (count_of_understoods/total_students)*100

        avg_comprehenssion_score=sum(comp_level_list)/total_students
        avg_incomprehenssion_score=sum(non_comp_level_list)/total_students

        # Initialize the map to store the data
        data_map = {
            "student_reports": [],
            "class_data": {
                "total_students": total_students,
                "emotions_percentages": class_emotions_percentages,
                "prominent_class_emotion": prominent_class_emotion,
                "comprehension_score": comprehenssion_level_of_class,
                "avg_comprehension_score": avg_comprehenssion_score,
                "avg_incomprehension_score": avg_incomprehenssion_score,

            }
        }

        # Add student reports to the map
        for student, report in student_reports.items():
            student_report = {
                "student": student,
                "emotions_percentage": report['emotions_count'],
                "prominent_emotion": report['prominent_emotion'],
                "understanding": report.get('understanding', ''),
                "not_understanding": report.get('notunderstanding', '')
            }
            data_map["student_reports"].append(student_report)

        return(data_map)

    except Exception as e:
        print("Error fetching data:", e)

