from sys import argv
import json
import os
import datetime

scheduleFilePath = '{}/.schedule'.format(os.environ['HOME'])
yesArray = ['y', 'Y']

def SecondsToTime(sec):
	return '%02d:%02d' % (sec/3600, (sec%3600)/60)

def JSONDump(obj):
	jsonString = json.dumps(obj, default=lambda o: o.__dict__, indent = 4)
	
	with open(scheduleFilePath, 'w+') as file:
		file.write(jsonString)

class Day(object):
	def __init__(self, name):
		self.name = name
		self.classes = []

CLASS_FLAG_MAKEUP = 'M'
CLASS_FLAG_LAB = 'L'
class Class(object):
	def __init__(self, name, time, classroom, isLab, isMakeup):
		self.name = name

		sod = (8*3600) + (40*60)
		time = sod + ((time - 1) * 3600)

		self.time = '{}'.format(SecondsToTime(time))
		self.classroom = '({})'.format(classroom)
		self.isLab = True if isLab in yesArray else False
		self.isMakeup = True if isMakeup in yesArray else False
		self.flags = '[' + (CLASS_FLAG_LAB if isLab else '') + (CLASS_FLAG_MAKEUP if isMakeup else '') + ']'

	def UpdateClass(self, name, classroom, isLab, isMakeup):
		self.name = name
		self.classroom = '({})'.format(classroom)
		self.isLab = True if isLab in yesArray else False
		self.isMakeup = True if isMakeup in yesArray else False
		self.flags = '[' + (CLASS_FLAG_LAB if isLab else '') + (CLASS_FLAG_MAKEUP if isMakeup else '') + ']'

def ClassInfo(day):
	print('{}: '.format(day.name))
	for i in range(1, 12):
		response = input('Class {}?[y/N]'.format(i))
		if not response in yesArray:
			day.classes.append(None)
			continue

		day.classes.append(Class( \
			input('\tName: '), \
			i, \
			input('\tClassroom: '), \
			input('\tLab ?[y/N]') in yesArray, \
			input('\tMake-Up?[y/N]') in yesArray \
		))

	return day

def NewSchedule():
	if os.path.isfile(scheduleFilePath):
		response = input('A schedule is already exists. Do you really want to create new one?[y/N]')
		if response not in ['y', 'Y']:
			exit(0)
	
	mon = Day('Monday')
	tue = Day('Tuesday')
	wed = Day('Wednesday')
	thu = Day('Thursday')
	fri = Day('Friday')

	mon = ClassInfo(mon)
	print('')
	tue = ClassInfo(tue)
	print('')
	wed = ClassInfo(wed)
	print('')
	thu = ClassInfo(thu)
	print('')
	fri = ClassInfo(fri)
	print('')

	jsonObject = {
		'days': [mon, tue, wed, thu, fri]
	}

	jsonString = json.dumps(jsonObject, default = lambda o: o.__dict__, indent = 4)

	with open(scheduleFilePath, 'w+') as file:
		file.write(jsonString)

def DayStringToDayIndex(dayString):
	dayString = dayString.lower()

	if dayString in ['mon', 'monday']:
		return 0
	elif dayString in ['tue', 'tuesday']:
		return 1
	elif dayString in ['wed', 'wednesday']:
		return 2
	elif dayString in ['thu', 'thursday']:
		return 3
	elif dayString in ['fri', 'friday']:
		return 4
	elif dayString in ['sat', 'saturday']:
		return 5
	elif dayString in ['sun', 'sunday']:
		return 6
	else:
		return datetime.date.today().weekday()

def UpdateClass(schedule):
	day = DayStringToDayIndex(input('Day: '))
	if day not in range(5):
		print( \
			'Can not update {}\'s schedule.'.format( \
				'Saturday' if day == 5 else 'Sunday' \
			) \
		)
		exit(0)

	time = int(input('Time: '))

	schedule['days'][day]['classes'][time - 1] = Class( \
		input('Name: '), \
		time, \
		input('Classroom: '), \
		True if input('Lab ?[y/N]') in yesArray else False, \
		True if input('Make-Up ?[y/N]') in yesArray else False, \
	)

	JSONDump(schedule)

def DeleteClass(schedule):
	day = DayStringToDayIndex(input('Day: '))
	if day not in range(5):
		print( \
			'Can not update {}\'s schedule.'.format( \
				'Saturday' if day == 5 else 'Sunday' \
			) \
		)
		exit(0)

	time = int(input('Time: '))

	schedule['days'][day]['classes'][time - 1] = None

	JSONDump(schedule)

def FromExisting():
	schedule = None

	if not os.path.isfile(scheduleFilePath):
		print('You need to create a schedule first.')
		return None

	with open('{}/.schedule'.format(os.environ['HOME']), 'r') as file:
		schedule = json.loads(file.read())

	return schedule

def WriteDayInfo(day, fill):
	print('{}'.format(day['name']))
	currentTime = (8*3600) + (40*60)
	for c in day['classes']:
		info = ''
		if c is not None:
			time = c['time']
			name = c['name']
			flags = c['flags']
			classroom = c['classroom']

			info += '\t{} - {}\t'.format(time, SecondsToTime(currentTime + 3000))
			info += '{}{}'.format(name, '\t' * (2 if len(name) < 8 else 1))
			info += '{}\t'.format(flags)
			info += '{}{}'.format(classroom, '  ' if len(classroom) < 8 else ' ')
		else:
			if fill:
				info += '\t%02d:%02d' % (currentTime/3600, (currentTime%3600)/60)

		currentTime += 3600
		if info != '':
			print(info)

def WriteAllWeek(schedule, fill):
	WriteDayInfo(schedule['days'][0], fill)
	WriteDayInfo(schedule['days'][1], fill)
	WriteDayInfo(schedule['days'][2], fill)
	WriteDayInfo(schedule['days'][3], fill)
	WriteDayInfo(schedule['days'][4], fill)

def WriteDayInfoFromString(day, fill):
	day = DayStringToDayIndex(day)

	if day in range(5):
		WriteDayInfo(schedule['days'][day], fill)
	else:
		print('Today is {}'.format('Saturday' if day == 5 else 'Sunday'))

if __name__ == '__main__':
	day = ''
	week = False
	new = False
	fill = False
	update = False
	delete = False

	for arg in argv:
		arg = arg.split('=')

		if arg[0] == '--day':
			if len(arg) >= 2:
				day = arg[1].lower()
		elif arg[0] == '--week':
			week = True
			day = ''
		elif arg[0] == 'new':
			new = True
		elif arg[0] == '--fill':
			fill = True
		elif arg[0] == 'update':
			update = True
			delete = False
		elif arg[0] == 'delete':
			delete = True
			update = False

	if new:
		NewSchedule()
		exit(0)

	schedule = FromExisting()
	if schedule is None:
		exit(0)

	if update:
		UpdateClass(schedule)
		exit(0)

	if delete:
		DeleteClass(schedule)
		exit(0)

	if week:
		WriteAllWeek(schedule, fill)
		exit(0)
	else:
		WriteDayInfoFromString(day, fill)
		exit(0)
