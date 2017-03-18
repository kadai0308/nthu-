from channels import Group
from channels.sessions import channel_session

from django.contrib.auth.models import User
from course.models import Course, CourseByYear, ScoreRange

from bs4 import BeautifulSoup
import requests
import json

@channel_session
def ws_connect(message):
    # Accept connection
    message.reply_channel.send({"accept": True})
    # Work out room name from path (ignore slashes)
    room = message.content['path'].strip("/")
    # Save room in session and add us to the group
    message.channel_session['room'] = room
    Group("chat-%s" % room).add(message.reply_channel)

# Connected to websocket.receive
@channel_session
def ws_message(message):
    data = json.loads(message['text'])
    user_id = int(message.channel_session['room'])
    user = User.objects.get(id = user_id)

    group_name = "chat-{}".format(message.channel_session['room'])
    if data['task'] == 'import_course_score_range':
        ACIXSTORE = data.get('acixstore', '')
        url = 'https://www.ccxp.nthu.edu.tw/ccxp/INQUIRE/JH/8/R/6.3/JH8R63002.php?ACIXSTORE={}'.format(ACIXSTORE)
        html = requests.get(url)

        if html.text == 'session is interrupted! <br>':
            # acixstore invalid
            Group(group_name).send({ 'text': json.dumps({ 'status': 'fail' }) })
        else:
            soup = BeautifulSoup(html.content, 'html.parser')
            main_sheet = soup.find_all('table')[1]
            # 4 is the amount of unnecessary tr tags
            course_amount = len(main_sheet.find_all('tr')) - 4
            # send initial progress bar message
            Group(group_name).send({
                'text': json.dumps({
                    'status': 'initial progress bar',
                    'course_amount': course_amount
                })
            }, immediately = True)
            # iter the course
            for index, i in enumerate(main_sheet.find_all('tr')[1:]):
                if index % 10 == 0:
                    Group(group_name).send({
                        'text': json.dumps({
                                    'status': 'update',
                                    'progress': (index / course_amount)*100
                                })
                    }, immediately = True)
                if index == course_amount - 1:
                    Group(group_name).send({
                        'text': json.dumps({
                                    'status': 'complete',
                                    'progress': 100
                                })
                    }, immediately = True)
                try:
                    if '成績未到' in i.find_all('td')[5].text:
                        continue

                    year = i.find_all('td')[0].text
                    semester = i.find_all('td')[1].text
                    course_no = i.find_all('td')[2].text.replace('\xa0', '').replace(' ','%20')

                    c_key = year+semester+course_no

                    score_range_url = ('https://www.ccxp.nthu.edu.tw/ccxp/INQUIRE/JH/8/8.3/8.3.3/JH83302.php?'
                        'ACIXSTORE={}&'
                        'c_key={}').format(ACIXSTORE, c_key)
                    
                    score_range_html = requests.get(score_range_url).content

                    score_range_soup = BeautifulSoup(score_range_html, 'html.parser')

                    score_range_data = score_range_soup.find_all('tr')[2].text
                    score_range_data_list = score_range_data.replace('\xa0', '').replace(' ','').replace('%', '').split('\n')[2:]

                    course_data_col = i.find_all('td')
                    course_no = course_data_col[0].text + course_data_col[1].text + course_data_col[2].text.replace('\xa0', '')

                    course_by_year = CourseByYear.objects.get(course_no = course_no)
                    ScoreRange.objects.update_or_create(
                            course = course_by_year,
                            defaults = {
                                "user": user,
                                "course": course_by_year,
                                "score_data": score_range_data_list,
                            } 
                        )
                    print (course_by_year.course.title_tw)
                    print (score_range_data_list)
                    # print ('-'*100)
                except  Exception as e:
                    print (str(e))
                    continue


# Connected to websocket.disconnect
@channel_session
def ws_disconnect(message):
    Group("chat-%s" % message.channel_session['room']).discard(message.reply_channel)
