# Singapore Computer Society (SCS) Cybersecurity Community Telegram Supergroup Admin Bot



## Background
As part of the SCS Cyber Chapter's Cyber Mentoring Programme, a Telegram [Supergroup](https://telegram.org/blog/supergroups) was set up to enable our cyber community to provide continuous support to the one another. This includes budding cyber specialists, esteemed professionals, and industry representatives.



In this Supergroup, we share problems and suggestions. We have active discussions ranging from cyber discussions (such as clarifying or sharing of thoughts and approaches on AI, ZTA, PQC, malware analysis, and security testing) to seeking for cyber career advices (to help budding cyber specialists). This community has also actively shared various online training resources and recommended books to job postings from various companies. You can join this group via the link [here](https://t.me/+0Lm4ikoVV3ViNTc1).



To help ensure that the conversations are posted at the correct forum topics, this project leveraged on *OpenAI's* for natural language processing capability to classify contents, primarily using finetuned models.



>  Note: This Telegram Bot project is my personal project and initiative as a member of the cyber community. Any vulnerabilities identified would be directly attributed to my work, and I will be glad to fix any reported vulnerabilites soonest.



---



## Description

>  As this project is developed to support the cybersecurity community, it is designed with security in mind with the intention to promulgate more defensive coding and deployment practices among the development community.



This is a simple Telegram Bot that is equipped with [OpenAI capabilities](https://openai.com/) to help administrate the Supergroup. It was [trained](https://platform.openai.com/docs/guides/fine-tuning) with closed to approximately *1000 data points* using the  **GPT 3.0 Ada** as our base model. It would classify message into any of the following five classes: *news*, *jobs*, *articles*, *trainings*, *others*. 



As the dataset at present is not uniformly distributed and generally small, the model will be retrained at a later date as the chatgroup receives more messages which can  be used as an input to train the model. For the free text natural language interaction feature, it leverages [GPT 3.5 Turbo](https://platform.openai.com/docs/models/gpt-3-5).



It is currently built with the following functions:

* Permit **only** `Administrators` (including the `mentors` and the `owner`) to send messages in the `General` topic that is reserved for mass communication.
* Permit **only** `Adminstrators` to interact with ChatGPT using the `/gpt` command, e.g. `/gtp tell me more about Singapore`
* Keep  `Job Postings` topic free from career related discussion. Any discussion found within will be forwarded to `Career Discussions` topic.
* Keep  `Training Resources` topic free from cyber discussions. Any discussion found within will be forwarded to `Cyber Discussions` topic.
* Keep  `Cyber News` topic to accept only news and articles, but free from cyber discussions. Any discussion found within will be forwarded to `Cyber Discussions` topic.
* Keep  `Reports and Articles` topic to accept only reports and articles, and free from cyber news and discussions. News and discussions will be forwarded to `Cyber News` and `Cyber Discussions` topics respectively.


This project is also designed to support BOTH **Polling** and **Web Hook** modes. :smiley:  `Polling` mode can be deployed on local PC,  Raspberry Pi, or cloud-based Virtual Machines,  while `Web Hook` mode can be deployed on-cloud containerised deployments.



*Many online examples share how to code and deploy using either Polling or Web Hook modes, but not both within the same application. This project will share how to develop a  Telegram Bot that can support both modes within a single application. This is because `Polling` mode can be useful for quick unit testing and troubleshooting during development and debugging, while `Web Hook` mode can be useful for production deployments. Simply by how the application is run, it will operate in either Polling or WebHook mode without having to change any code or configurations. This could mitigate against errorneous deployment of code or configurations in the production environment that uses Web Hook.*



---



## Table of Contents

1. [How to setup the Prerequistes](#prerequisite)
2. [How to run in Polling Mode](#polling)
3. [How to deploy using Web Hook](#webhook)
4. [Security](#security)
5. [Credits](#credits)
6. [License](#license)



---

<a name="prerequisite"/>

## 1. How to Setup the Prerequisites for Each Deployment Environment

> This section describes the steps to set up the program for each deployment environment. If it is only for testing purposes, only one environment is required. Otherwise, it is important to have **different environment for development and production purposes**.
>
>  
>
> All secrets needs to be securely managed. For example, **do not commit secrets** into your source code repositories, including private ones which may accidentally be exposed. For cloud deployments, it is recommended to use Secret Manager to store these secrets and expose them to the relevant application service via means such as Environment Variables.
>
> 
>
> The **endpoint to the webhook service should only be known to the Telegram API service** during registration of the webhook and should not be easily discovered. With the knowledge of this endpoint, a post request can be sent to the webhook. This may result in attackers potentially controlling your bot.



1. Register a new **Telegram Bot** using [BotFather](https://t.me/botfather), and configure it with privacy disabled so that it can process all messages sent to the Supergroup. Do not use this newly created bot for other purposes to limit the blast radius.

   

2. Setup a **Telegram Supergroup** minimally with the following Topics:

   * *Cyber News*
   * *Jobs*
   * *Reports and Articles*
   * *Training Resources*
   * *Career Discussions*
   * *Cyber Discussions*

   

3. Add the Telegram Bot created to the Telegram Supergroup as a **Group Administrator**.

   

4. Install Python libraries specified in requirements.txt, e.g. `pip install -r requirements.txt`

   

5. Export the following **Environment Variables**:

   - **MODE** : It should take either the value of `"dev"` or `"prod"` to differentiate which set of configuations to load
   - **BOT_TOKEN**: This is a **secret** provided by BotFather
   - **OPENAI_API_KEY**: This is a **secret** API key provided by OpenAI
   - **FINETUNED_MODEL**: This is the **identifier** of a trained model that is used for classifying the messages
   - **HOOK_URL**: (Only required for WebHook) This is the base url of the service
   - **HOOK_TOKEN**: (Only required for WebHook) This is a **secret** as the endpoint of the web hook service is formed as `{HOOK_URL}/{HOOK_TOKEN}`.

   

6. Update `config.json` that stores the **Topic Identifier** which corresponds to Telebot's **`message.message_thread_id`** . This file found in both `config/dev` and `config/prod` folders. 

   

   *The Topic Identifier can be extracted from the browser's address bar when a Telegram Supergroup's Topic is visited using the Web-based Telegram application. For example, when we visit the `Jobs` Topic, the URL revealed in the address bar is as `https://web.telegram.org/z/#-1409853914_114`. The Topic Identifier will be `114` that is appended to the Supergroup Identifier (i.e. `-1409853914`) with an underscore.*



---

<a name="polling"/>

## 2. How to run in Polling Mode

> As this project is designed to support both **Polling** and **Webhook** modes, it has two python files `SCSTelegramBot.py` (for polling mode) and `app.py` (for webhook mode). Even though SCSTelegramBot.py can be used for deployment in polling mode, it describes the class `SCSBotWrapper` which is also used by the Flask service described in `app.py`.



###  Run SCSTelegramBot.py

To run, simple execute the following bash commands. If the program terminates, it could due to the required Environment Variables not exported properly.

```bash
# Assume that the environment variables are stored in the '.env' file
source .env
python3 SCSTelegramBot.py
```



---

<a name="webhook"/>

## 3. Deploy Using WebHook (Using Google Cloud Run example)

> The Web Hook can be hosted on any hosting environments. For illustration purposes, I have used Google Cloud Run service as an example.

1. Set up a new Google Cloud project. 

   *If you are using it for the first time, you will get some free credits to play with. :)*

   

2. Configure GCloud to store secrets using Google's Secret Manager.

   ![1.Create Secrets](https://raw.githubusercontent.com/ronghwa80/SCS-Telegram-Bot/master/images/1.Create%20Secrets.png)

   

3. Clone the repository from the GitHub repository and set working directory the root of the repository.

   

4. Create a new Cloud Run Service either using commandline or console. As this web hook needs to be invoked from the Internet, we need to permit unauthenticated services. This is also why "HOOK_TOKEN" needs to be **updated** and kept **secret**.

   ![2.Create Cloud Run](https://raw.githubusercontent.com/ronghwa80/SCS-Telegram-Bot/master/images/2.Create%20Cloud%20Run.png)

   Alternatively, you can also deploy a gcloud run service via the following commandline.

   ```bash
   #You can set source to either the link to the Docker image or current directory
   gcloud run deploy --source .
   ```

   

5. Ensure that the environment variables are set correctly

   ![3.Set Environment Variables](https://raw.githubusercontent.com/ronghwa80/SCS-Telegram-Bot/master/images/3.Set%20Environment%20Variables.png)

   - If HOOK_URL is unknown during the first run, it can be set with any non-empty string value. We can retrieve the URL provisioned by Google Cloud Run after its first run to update this Environment Variable.

   - The secrets should be exposed as Environment Variable to the container

     

6. Trigger setting of webhook can be invokved through visiting `/setwebhook`.

   ![4. Activate Webhook](https://raw.githubusercontent.com/ronghwa80/SCS-Telegram-Bot/master/images/4.Activate%20WebHook.png)

7. (Optional) Trigger removal of webhook can be invokved through visiting `/removewebhook`.



---

<a name="security"/>

## 4. Security


If you believe you have found a security vulnerability in any of my repositories, please report it to me. I will be more happy to fix it with your help.
**Please do not report security vulnerabilities through public GitHub issues, discussions, or pull requests. **Instead, please send an email to **opensource.report.vulnerability@gmail.com** 

Please include as much of the information listed below as you can to help us better understand and resolve the issue:

  * The type of issue (e.g., IDOR, SQL injection, or cross-site scripting)
  * Full paths of source file(s) related to the manifestation of the issue
  * The location of the affected source code (tag/branch/commit or direct URL)
  * Any special configurations or pre-requisites that are required to reproduce the issue
  * Step-by-step instructions to reproduce the issue
  * Proof-of-concept or exploit code. It will be great if it is available. :)
  * Impact of the issue, including how an attacker might exploit the issue

This information will help me to triage your report more quickly.


---

<a name="credits"/>

## 5. Credits

- Lead Developer - [Mr. Chong Rong Hwa](https://www.linkedin.com/in/ronghwa)
- SCS Cyber community for keeping the Telegram Supergroup very much alive!
- [Telebot](https://pypi.org/project/pyTelegramBotAPI) for enabling me to accelerate the development progress of the bot
- [OpenAI](https://platform.openai.com/docs/api-reference/introduction) for providing foundation for natural language classification



---

<a name="license"/>

## 6. License

The MIT License (MIT)

Copyright 2023 Mr. Chong Rong Hwa

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.