# TechConf Registration Website

## Project Overview
The TechConf website allows attendees to register for an upcoming conference. Administrators can also view the list of attendees and notify all attendees via a personalized email message.

The application is currently working but the following pain points have triggered the need for migration to Azure:
 - The web application is not scalable to handle user load at peak
 - When the admin sends out notifications, it's currently taking a long time because it's looping through all attendees, resulting in some HTTP timeout exceptions
 - The current architecture is not cost-effective 

In this project, you are tasked to do the following:
- Migrate and deploy the pre-existing web app to an Azure App Service
- Migrate a PostgreSQL database backup to an Azure Postgres database instance
- Refactor the notification logic to an Azure Function via a service bus queue message

## Dependencies

You will need to install the following locally:
- [Postgres](https://www.postgresql.org/download/)
- [Visual Studio Code](https://code.visualstudio.com/download)
- [Azure Function tools V3](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=windows%2Ccsharp%2Cbash#install-the-azure-functions-core-tools)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)
- [Azure Tools for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=ms-vscode.vscode-node-azure-pack)

## Project Instructions

### Part 1: Create Azure Resources and Deploy Web App
1. Create a Resource group
2. Create an Azure Postgres Database single server
   - Add a new database `techconfdb`
   - Allow all IPs to connect to database server
   - Restore the database with the backup located in the data folder
3. Create a Service Bus resource with a `notificationqueue` that will be used to communicate between the web and the function
   - Open the web folder and update the following in the `config.py` file
      - `POSTGRES_URL`
      - `POSTGRES_USER`
      - `POSTGRES_PW`
      - `POSTGRES_DB`
      - `SERVICE_BUS_CONNECTION_STRING`
4. Create App Service plan
5. Create a storage account
6. Deploy the web app

### Part 2: Create and Publish Azure Function
1. Create an Azure Function in the `function` folder that is triggered by the service bus queue created in Part 1.

      **Note**: Skeleton code has been provided in the **README** file located in the `function` folder. You will need to copy/paste this code into the `__init.py__` file in the `function` folder.
      - The Azure Function should do the following:
         - Process the message which is the `notification_id`
         - Query the database using `psycopg2` library for the given notification to retrieve the subject and message
         - Query the database to retrieve a list of attendees (**email** and **first name**)
         - Loop through each attendee and send a personalized subject message
         - After the notification, update the notification status with the total number of attendees notified
2. Publish the Azure Function

### Part 3: Refactor `routes.py`
1. Refactor the post logic in `web/app/routes.py -> notification()` using servicebus `queue_client`:
   - The notification method on POST should save the notification object and queue the notification id for the function to pick it up
2. Re-deploy the web app to publish changes

## Monthly Cost Analysis
Complete a month cost analysis of each Azure resource to give an estimate total cost using the table below:

| Azure Resource | Service Tier | Monthly Cost |
| :------------ | :------------: | ------------: |
| *Azure Postgres Database* |  BASIC with Compute (Gen 5, 2 vCore) and storage of 5GB   |  $50.14  |
| *Azure Service Bus*       | BASIC   | (per million operation) $0.0500  |
| *APP Service*             | BASIC (B1: 1 Core , 1.75GB Ram, 10GB storage) |   $12.4100 |
| *Azure Functions*         | Consumption (The first 400,000 GB/s of execution and 1,000,000 executions are free.) | $ 0.0000    |
| *Storage Account : QUEUE*     |  General Purpose v1 Storage Capacity LRS | per GB  $0.045    |
| *Storage Account : QUEUE*     |  General Purpose v1 Queue Class 1(1) operations (in 10,000) |   $0.0004    |
| *Storage Account : QUEUE*     |  General Purpose v1 Queue Class 2(2) operations (in 10,000) |   $0.0004    |
| *Send grid* (3)         |  Essential  40K (limit 50,000 emails/month)  |  $14.9500  |

Notes:
* (1) The following Queue operations are counted as Class 1: CreateQueue, ListQueues, PutMessage, SetQueueMetadata, UpdateMessage, ClearMessages, DeleteMessage, DeleteQueue, GetMessageWrite, GetMessagesWrite
* (2) The following Queue operations are counted as Class 2: GetMessage, GetMessages, GetQueueMetadata, GetQueueServiceProperties, GetQueueAcl, PeekMessage, PeekMessages, GetMessageRead, GetMessagesRead
* (3) [Send grid Pricing](https://sendgrid.com/pricing/)

## Architecture Explanation
This is a placeholder section where you can provide an explanation and reasoning for your architecture selection for both the Azure Web App and Azure Function.

### My Explanation / Reasoning

This migration helps to solve the main problems : 
1. No scalability for the actual web app
1. Some HTTP timeout exceptions when a new notification is added. Because the actual web app serve HTTP requests at the same time it sends a lot of mails.
1. Cost problems.


#### Solutions:

1. Scalability: Azure lets scale the web app in function of the HTTP requests. 
1. Better Performance. Azure function lets create a decoupled application. Send emails can be done in a independent way to the Web app.
1. Cost Management. Azure Web App and Azure Function lets easily control the hardware needs in function of the demand and let us only pay per use. In addition, Azure lets save time for hardware and software maintenance.


