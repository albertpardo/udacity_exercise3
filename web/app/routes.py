from app import app, db, queue_client
from datetime import datetime
from app.models import Attendee, Conference, Notification
from flask import render_template, session, request, redirect, url_for, flash, make_response, session
from azure.servicebus import Message
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import logging


import psycopg2
from datetime import datetime


logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/Registration', methods=['POST', 'GET'])
def registration():
    if request.method == 'POST':
        attendee = Attendee()
        attendee.first_name = request.form['first_name']
        attendee.last_name = request.form['last_name']
        attendee.email = request.form['email']
        attendee.job_position = request.form['job_position']
        attendee.company = request.form['company']
        attendee.city = request.form['city']
        attendee.state = request.form['state']
        attendee.interests = request.form['interest']
        attendee.comments = request.form['message']
        attendee.conference_id = app.config.get('CONFERENCE_ID')

        try:
            db.session.add(attendee)
            db.session.commit()
            session['message'] = 'Thank you, {} {}, for registering!'.format(attendee.first_name, attendee.last_name)
            return redirect('/Registration')
        except:
            logging.error('Error occured while saving your information')

    else:
        if 'message' in session:
            message = session['message']
            session.pop('message', None)
            return render_template('registration.html', message=message)
        else:
             return render_template('registration.html')

@app.route('/Attendees')
def attendees():
    attendees = Attendee.query.order_by(Attendee.submitted_date).all()
    return render_template('attendees.html', attendees=attendees)


@app.route('/Notifications')
def notifications():
    notifications = Notification.query.order_by(Notification.id).all()
    return render_template('notifications.html', notifications=notifications)

@app.route('/Notification', methods=['POST', 'GET'])
def notification():
    if request.method == 'POST':
        notification = Notification()
        notification.message = request.form['message']
        notification.subject = request.form['subject']
        notification.status = 'Notifications submitted'
      
        notification.submitted_date = datetime.utcnow()
        
        logging.debug('--> Notification created ')

        try:
            db.session.autoflush = True
            db.session.add(notification)
            
            db.session.flush()
            notification_id = notification.id
            db.session.commit()
            
            logging.debug('--> Notification in DB ')
            
            ##################################################
            ## TODO: Refactor This logic into an Azure Function
            ## Code below will be replaced by a message queue
            #################################################
            # attendees = Attendee.query.all()

            # for attendee in attendees:
            #     subject = '{}: {}'.format(attendee.first_name, notification.subject)
            #     send_email(attendee.email, subject, notification.message)

            # notification.completed_date = datetime.utcnow()
            # notification.status = 'Notified {} attendees'.format(len(attendees))
            # db.session.commit()

            #################################################
            ## END of TODO
            #################################################
            
            # # # TODO Call servicebus queue_client to enqueue notification ID
            # logging.debug(' ---> queue_client : {}'. format(queue_client))
            # logging.debug('--> Creting MSG . ID = {}'. format(notification_id))
            # msg = Message('{}'.format(notification_id))
            # logging.debug('--> Sendindg MSG')
            # queue_client.send(msg)

            # logging.debug('--> Notification QUEUED')
            
            my_test_func(notification_id)


            return redirect('/Notifications')
        except :
            logging.error('log unable to save notification')

    else:
        return render_template('notification.html')

def my_test_func(notification_id):

    print('my_test_func -> notification_id={}'.format(notification_id))
    try:
        connection = psycopg2.connect(user=app.config.get('POSTGRES_USER'),
                                    password=app.config.get('POSTGRES_PW'),
                                    host=app.config.get('HOST'),
                                    port=app.config.get('PORT'),
                                    database=app.config.get('POSTGRES_DB'))
        
        cursor = connection.cursor()
        print('--> Conected')

        # TODO: Get notification message and subject from database using the notification_id

        notification_message_subject_query = "SELECT subject,message FROM notification WHERE id = (%s)"
        cursor.execute(notification_message_subject_query, (notification_id,))
        print('--> Cursor executed')
        notification = cursor.fetchall()
        print('--> Notification getted : {}'.format(notification))
        notification_subject = notification[0][0]
        notification_message = notification[0][1]

        print('--> Notification finished')

        attendees_name_mail_query = "SELECT first_name,email FROM attendee"
        cursor.execute(attendees_name_mail_query)
        attendees_name_mail = cursor.fetchall()

        print('--> attendee finished')


        # TODO: Loop through each attendee and send an email with a personalized subject
        for attendee in attendees_name_mail:
            name = attendee[0]
            mail = attendee[1]
            subject = '{}: {}'.format(name, notification_subject)
            send_email(mail, subject, notification_message)


        #
        # Update notification time & Status
        #
        
     
        total_attendees = len(attendees_name_mail)
            
        # Update time
        completed_date_and_status_update_query = "UPDATE notification SET completed_date = %s, status = %s WHERE id = %s"
        status_message = 'Notified {} attendees'.format(total_attendees)
        cursor.execute(completed_date_and_status_update_query, (datetime.utcnow(), status_message , notification_id))
        connection.commit()
  

    except (Exception, psycopg2.Error) as error:
        print("Error fetching data from PostgreSQL table", error)

    finally:
        # closing database connection
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed \n")

def send_email(email, subject, body):

    if app.config.get('SENDGRID_API_KEY'):

        message = Mail(
            from_email=app.config.get('ADMIN_EMAIL_ADDRESS'),
            to_emails=email,
            subject=subject,
            plain_text_content=body)

        try :
            sg = SendGridAPIClient(app.config.get('SENDGRID_API_KEY'))
            sg.send(message)
            
        except :
            logging.error('Error sending')
    else:
        logging.error('NO SENDGRID_API_KEY')