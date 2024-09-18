# OCR Function App

## Table of Contents

- [OCR Function App](#ocr-function-app)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
    - [Setup](#setup)
      - [Prerequisites](#prerequisites)
    - [Email Communication Service](#email-communication-service)
  - [Resources](#resources)

## Overview

This function app is apart of the Doorbell hack

This serves as the optical character recognition
and email notification service when a message is received in a queue. The expected message
that this function app receives contains data about a shipping label and device id and extracts
this information to automatically email an employee when a package has been received.

### Setup

#### Prerequisites

There are a few Azure services that need to be created for this function app to work end to end.

- Azure Communication Service
- Azure Email Communication Service
  - Note: These are two different resources and both are required
- Azure Storage Account
- Azure Document Intelligence

Once these are deployed, you will have to configure some of the services.

1. Azure Email Communication Service
   - You will have to provision a domain (see [this documentation](https://learn.microsoft.com/en-us/azure/communication-services/quickstarts/email/connect-email-communication-resource?pivots=azure-portal) for more information)
2. Azure Storage Account
   - You will have to create a container that houses the JSON configuration [file](employees.jsonc).
   - This file contains the "source of truth" of employees and is what is used to compare against the OCR. 

| Variable Name                                   | Description                                      |
|------------------------------------------------|--------------------------------------------------|
| `DOCUMENT_INTELLIGENCE_ENDPOINT`               | The endpoint URL for the document intelligence service within Azure. |
| `DOCUMENT_INTELLIGENCE_API_KEY`                | The API key used for authenticating requests to the document intelligence service. |
| `STORAGE_ACCOUNT_CONNECTION_STRING`            | The connection string used to connect to the storage account (e.g., Azure Blob Storage). |
| `STORAGE_CONTAINER_NAME`                       | The name of the container in the storage account where the Employee JSON configuration file is stored. |
| `EMAIL_COMMUNICATION_CONNECTION_STRING`        | The connection string used to connect to the email communication service. |
| `COMMUNICATION_SENDER_ADDRESS`                 | The email address from which communications will be sent. |
| `GROUP_EMAIL_ALIAS`                            | An alias for a group email address that can be used for sending emails to multiple recipients. |

### Email Communication Service

This function app uses the Communication and Email Communication Azure service.

Useful links:

<https://learn.microsoft.com/en-us/azure/communication-services/quickstarts/email/connect-email-communication-resource?pivots=azure-portal>
<https://learn.microsoft.com/en-us/azure/communication-services/quickstarts/email/send-email?tabs=linux%2Cconnection-string%2Csend-email-and-get-status-async%2Csync-client&pivots=platform-azportal>

## Resources

