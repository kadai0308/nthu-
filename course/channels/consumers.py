from channels import Group
from channels.sessions import channel_session

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
    group_name = "chat-{}".format(message.channel_session['room'])
    if data['task'] == 'import_course_score_range':
        ACIXSTORE = data.get('acixstore', '')
        url = 'https://www.ccxp.nthu.edu.tw/ccxp/INQUIRE/JH/8/R/6.3/JH8R63002.php?ACIXSTORE={}'.format(ACIXSTORE)
        html = requests.get(url).text
        if html == 'session is interrupted! <br>':
            # acixstore invalid
            Group(group_name).send({
                'text': json.dumps({
                                    'status': 'fail'
                                }),
            })
        else:
            soup = BeautifulSoup(html, 'html.parser')
            main_sheet = soup.find_all('table')[1]
            # 4 is the amount of other tr tags
            course_amount = len(main_sheet.find_all('tr')) - 4 
            send_data_initial = json.dumps({
                    'status': 'initial progress bar',
                    'course_amount': course_amount
                })

            Group(group_name).send({
                'text': send_data
            })
            for index, course in enumerate(main_sheet.find_all('tr')[1:]):
                if index % 10 == 0:
                    send_data_update = json.dumps({
                                    'status': 'update',
                                    'progress': (index / course_amounte)*100
                                })
                if index == course_amount - 1:
                    send_data_update = json.dumps({
                                    'status': 'update',
                                    'progress': 100
                                })
                Group(group_name).send({
                    'text': send_data_update
                 })


            
            

            


# Connected to websocket.disconnect
@channel_session
def ws_disconnect(message):
    Group("chat-%s" % message.channel_session['room']).discard(message.reply_channel)
