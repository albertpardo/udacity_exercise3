import logging

import azure.functions as func

import psycopg2
import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def main(msg: func.ServiceBusMessage):

    POSTGRES_USER=os.environ["PostgresUser"]
    POSTGRES_PW=os.environ["PostgresPW"]
    POSTGRES_DB=os.environ["PostgresDB"]
    HOST=os.environ["Host"]
    PORT=os.environ["Port"]


    notification_id = int(msg.get_body().decode('utf-8'))
    logging.info('Python ServiceBus queue trigger processed message: %s',notification_id)

    # TODO: Get connection to database
    connection = psycopg2.connect(user=POSTGRES_USER,
                                  password=POSTGRES_PW,
                                  host=HOST,
                                  port=PORT,
                                  database=POSTGRES_DB)
    
    cursor = connection.cursor()
    logging.info('--> Conected')
    
    try:
        # TODO: Get notification message and subject from database using the notification_id
        notification_message_subject_query = "SELECT subject,message FROM notification WHERE id = (%s)"
        cursor.execute(notification_message_subject_query, (notification_id,))
        logging.info('--> Cursor executed')

        notification = cursor.fetchall()
        logging.info('--> Notification getted : {}'.format(notification))
        
        notification_subject = notification[0][0]
        notification_message = notification[0][1]

        logging.info('--> Notification finished')
        
        # TODO: Get attendees email and name
        attendees_name_mail_query = "SELECT first_name,email FROM attendee"
        cursor.execute(attendees_name_mail_query)
        attendees_name_mail = cursor.fetchall()
        
        logging.info('--> attendee finished')
        
        # TODO: Loop through each attendee and send an email with a personalized subject
        for attendee in attendees_name_mail:
            name = attendee[0]
            mail = attendee[1]
            subject = '{}: {}'.format(name, notification_subject)
            send_email(mail, subject, notification_message)
            
        # TODO: Update the notification table by setting the completed date and updating the status with the total number of attendees notified
        
        total_attendees = len(attendees_name_mail)
        
        completed_date_and_status_update_query = "UPDATE notification SET completed_date = %s, status = %s WHERE id = %s"
        status_message = 'Notified {} attendees'.format(total_attendees)
        cursor.execute(completed_date_and_status_update_query, (datetime.utcnow(), status_message , notification_id))
        connection.commit()
        
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        # TODO: Close connection
        if connection:
            cursor.close()
            connection.close()
        
def send_email(email, subject, body):

    SENDGRID_API_KEY = os.environ["SendgridApiKey"]
    ADMIN_EMAIL_ADDRESS = os.environ["AdminEmailAddress"]

    if SENDGRID_API_KEY:

        message = Mail(
            from_email=ADMIN_EMAIL_ADDRESS,
            to_emails=email,
            subject=subject,
            plain_text_content=body)

        try :
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            sg.send(message)
            
        except :
            logging.error('Error sending')
    else:
        logging.error('NO SENDGRID_API_KEY')