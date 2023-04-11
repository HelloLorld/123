import json
import codecs
# import re
from datetime import datetime 

def findTeacher(teacher="", day="", time="",schedule={}): 
    lessons = schedule[teacher][day]
    if (len(lessons) == 0):
        return None
    needTime = datetime.strptime(time, "%H:%M").time()
    for lesson in lessons:
        lessonTime = datetime.strptime(lesson["time"], "%H:%M").time()
        if (needTime <= lessonTime):
            return lesson
    return None

def findTeacherOnAllDay(teacher="", day="", schedule={}):
    lessons = schedule[teacher][day]
    if (len(lessons) == 0):
        return None
    return lessons

def lessonToString(lesson={}):
    nameOfLesson = lesson.get("nameOfLesson")
    groups = lesson.get("groups")
    office = lesson.get("office")
    typesOfLesson = lesson.get("type")
    timeOfLesson = lesson.get("time")
    strGroups = ""
    for group in groups:
        strGroups += f"{group}; "
    strGroups = strGroups[0:len(strGroups) - 2]
    strTypeOfLesson = ""
    for lessonType in typesOfLesson:
        strTypeOfLesson += f"{lessonType}\n"
    strTypeOfLesson = strTypeOfLesson[0:len(strTypeOfLesson) - 1]
    return f"{nameOfLesson}\nКабинет: {office}\nВремя: {timeOfLesson}\nГруппы: {strGroups}\nВид занятия:\n{strTypeOfLesson}"
def findGroup(group="", day="", time="", schedule={}):
    teachers = schedule.keys()
    needTime = datetime.strptime(time, "%H:%M").time()
    for teacher in teachers:
        lessons = schedule.get(teacher).get(day)
        if (lessons != None):
            for lesson in lessons:
                groups = lesson["groups"]
                lessonTime = lessonTime = datetime.strptime(lesson["time"], "%H:%M").time()
                # endTime = lessonTime
                # match = re.search("\dч", lesson["type"])
                # # if (match != None):
                if group in groups and needTime <= lessonTime:
                    return lesson
    return None

def getSchedule():
    fileObj = codecs.open( "test.json", "r", "utf_8_sig" )
    schedule: dict = json.load(fileObj)
    return schedule

def main():
    fileObj = codecs.open( "test.json", "r", "utf_8_sig" )
    schedule: dict = getSchedule()
    print(findTeacher('Бухнин Алексей Викторович', "Понедельник", "13:10", schedule))
    print(findGroup('20СБК', 'Понедельник', '10:50', schedule))

if __name__ == "__main__":
    main()