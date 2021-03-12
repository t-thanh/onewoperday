# main.py
import sys
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime, timedelta

if __name__ == "__main__":
	challenge_page = requests.get('https://84race.com/races/getranking/2684/1')
	# Create a BeautifulSoup object
	member_html = BeautifulSoup(challenge_page.text, 'html.parser')
	i = 0
	member_name=[]
	member_profile=[]
	for name in member_html.find_all('small'):
		member_name.append(name.contents[0])
		i=i+1
	j = 0
	for a in member_html.find_all('a', href=True):
		member_profile.append(a['href'])
		j=j+1
	print("Số vận động viên tham gia = ",i)  
	# get the list of tuples from two lists and merge them by using zip().  
	list_of_tuples = list(zip(member_name, member_profile))  

	# Converting lists of tuples into pandas Dataframe.  
	df = pd.DataFrame(list_of_tuples, 
					  columns = ['Name', 'Profile'])  
	# Save the participants list
	#df.to_csv(r'list_participants.cvs',index=False) 
	# load backup file to dataframe
	df_backup = pd.read_csv('https://www.dropbox.com/s/kfxx1yb59qisio5/backup_activity.cvs?dl=1')
	profile = sys.argv[1]
	start_date_str = "2021-03-08"
	min_date_str = sys.argv[2]
	max_date_str = sys.argv[3]
	#print (profile)
	#print (start_date_str)
	# init df
	load_profile = []
	load_activity = []
	activity_category = []
	activity_data = []
	date_time = []
	profile_page=requests.get(profile)
	name = df[df['Profile'] == profile].iloc[0]['Name']
	# Create a BeautifulSoup object
	profile_html = BeautifulSoup(profile_page.text, 'html.parser')
	count = 0
	activities_of_profile =df_backup[df_backup['Profile']==profile]['Activity']
	for a in profile_html.find_all('a', href=re.compile("activity")):
		# check if the activity already in df_backup
		if (a['href'] in activities_of_profile.values) == True:
			pass
		else:
			# check if the activity is later than certain date
			activity_page=requests.get(a['href'])
			activity_html = BeautifulSoup(activity_page.text, 'html.parser')
			for act in activity_html.find_all('time'):
				#print(act.contents[0][1:-8])
				date_time_str=act.contents[0]
				start_date_obj = datetime.strptime(start_date_str, '%Y-%m-%d')
				date_time_obj = datetime.strptime(date_time_str[1:-8], '%d/%m/%Y %H:%M:%S')
				#print (date_time_obj.date())
				#print (start_date_obj.date())
				if date_time_obj.date() >= start_date_obj.date():
					count = count + 1
					load_activity.append(a['href'])
					load_profile.append(profile)
					date_time.append(date_time_str)
					#check activity type
					# ic-shose2 = RUN
					# ic-question = Other
					# ic-bike = Bike
					# ic-swim = Swim
					if "shose2" in str(activity_html.find('i', {"class":"ic"})):
						activity_category.append('run')
					elif "swim" in str(activity_html.find('i', {"class":"ic"})):
						activity_category.append('swim')
					elif "bike" in str(activity_html.find('i', {"class":"ic"})):
						activity_category.append('bike')
					elif "question" in str(activity_html.find('i', {"class":"ic"})):
						activity_category.append('other')
					else: 
						activity_category.append('other')
						print ('New type of workout: ', activity_page)
					# add detail activity
					# date-time, distance, time, speed, HR, cadence, climb 
					value = []
					for af in activity_html.find_all('input'):
						if "value" in str(af) and not("keyword" in str(af)) and not("title" in str(af)) :
							value.append(af.get('value'))
						activity_data.append(value)
	if count > 0:
		print('Vận động viên ' + name + ' có thêm: ' + str(count_activity) + ' hoạt động tính từ lần cuối backup')
	distance = []
	duration = []
	speed = []
	hr = []
	cadence = []
	elevation = []
	for i in range(len(load_profile)):
		distance.append(activity_data[i][0])
		duration.append(activity_data[i][1])
		speed.append(activity_data[i][2])
		hr.append(activity_data[i][3])
		cadence.append(activity_data[i][4])
		elevation.append(activity_data[i][5])
	# get the list of tuples from two lists.  
	# and merge them by using zip().  
	activity_tuples = list(zip(load_profile, load_activity, date_time, activity_category, distance,
							   duration, speed, hr, cadence, elevation))  

	# Converting lists of tuples into  
	# pandas Dataframe.  
	df_new_activity = pd.DataFrame(activity_tuples, 
					  columns = ['Profile', 'Activity', 'Date_Time', 'Category', 'Distance', 'Duration', 'Speed', 
								 'HR', 'Cadence', 'Elevation'])  
	# merge then sort
	df_activity = pd.concat([df_new_activity,df_backup[df_backup['Profile'] == profile]]).drop_duplicates().reset_index(drop=True).sort_values(by=['Profile', 'Date_Time'], ascending=False)
	
	
	min_date_obj = datetime.strptime(min_date_str, '%Y-%m-%d')
	max_date_obj = datetime.strptime(max_date_str, '%Y-%m-%d')
	delta_date=int((max_date_obj.date() - min_date_obj.date()).days)
	name = df[df['Profile'] == 'https://84race.com/member/697538'].iloc[0]['Name']
	print('Vận động viên ' + name + ' có thêm các hoạt động sau tính từ '+ min_date_str + ' đến trước ' + max_date_str)
	#datetime.strptime(str(df_activity['Date_Time'])[1:11], '%d/%m/%Y')
	# list of workout date
	workout_date = []
	no_workout_date = []
	no_workout_days = 0

	for i in range(len(df_activity)):
		df_select = df_activity[:].iloc[i]
		#print (str(df_select['Date_Time'])[1:11])
		#print (str(df_select_str['Date_Time'][0]))
		activity_date_obj = datetime.strptime(str(df_select['Date_Time'])[1:11], '%d/%m/%Y')
		if max_date_obj.date() > activity_date_obj.date() >= min_date_obj.date():
			print (str(df_select['Activity'])+ ' trong ngày ' + str(df_select['Date_Time'])[1:11])
			workout_date.append(activity_date_obj.date())
	for k in range(delta_date):
		if min_date_obj.date()+ timedelta(days=k) in workout_date:
			pass
		else:
			no_workout_days = no_workout_days + 1
			no_workout_date.append(min_date_obj.date()+ timedelta(days=k))
	print ('Vận động viên ' + name + ' có '+ str(no_workout_days) + ' ngày không có hoạt động tính từ '+ min_date_str + ' đến trước ' + max_date_str)
