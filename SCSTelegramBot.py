import os
import telebot
import json
import openai
import logging
import time
import traceback
import re


# SCSBotWrapper is designed to support both polling and webhook modes of deployment
# Baseline environment variables required are: BOT_TOKEN, OPENAI_API_KEY, FINETUNED_MODEL, MODE
# Sensitive information are loaded from the environment variables.
# * BOT_TOKEN is the token that is issued by Telegram BotFather
# * OPENAI_API_KEY is the API key that is obtained from openai.com
# FINETUNED_MODEL is the model trained based on ada
# MODE is to indicate the environment - 'prod' or 'dev' - to retrieve the config file

class SCSBotWrapper:

    #Initialise and turn on appropriate logging level
    def __init__(self):
        #load environment variables
        #assume dev if not configured
        self.mode = os.environ.get('MODE') 
        
        self.BOT_TOKEN = os.environ.get('BOT_TOKEN')      
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.finetuned_model =  os.environ.get('FINETUNED_MODEL')
        
        #exit if critical environment variables are not available
        if self.mode is None: 
            logging.error ("MODE is not available.")
            exit(-1)
        elif self.BOT_TOKEN is None: 
            logging.error ("BOT_TOKEN is not available.")
            exit(-1)
        elif openai.api_key is None: 
            logging.error ("OPENAI_API_KEY is not available.")
            exit(-1)
        elif self.finetuned_model is None: 
            logging.error ("FINETUNED_MODEL is not available.")
            exit(-1)
        
        #config.json stores the SCS's forum topic id
        config_path = "{}/config/{}/config.json".format(os.getcwd(),self.mode)
        logging.debug (config_path)
        self.config = json.load(open(config_path,'r'))
        self.replytxt = "\U0001F446Forwarded from ***{source_topic}*** Topic. Apologise if wrongly classifed."

        #instantiate the bot with the token
        self.bot = telebot.TeleBot(self.BOT_TOKEN, parse_mode="MARKDOWN")
        self.bot.set_update_listener(self.handle_messages)
    
        if self.mode == 'prod':
            logging.basicConfig(level=logging.INFO)
            logging.info('App is running in production environment')
        else:
            logging.basicConfig(level=logging.DEBUG)
            logging.info('App is running in debug')

    # This function sends a welcome message to the chatgroup
    # The content of the message shares the rules of the chatgroup
    def send_houserules(self,message):
        from telebot import util

        welcome_message = open("{}/config/welcome.md".format(os.getcwd()), "r").read()
        splitted_text = util.smart_split(welcome_message, chars_per_string=3000)
        #welcome user at the General
        for text in splitted_text:
            self.bot.send_message(message.chat.id, text.encode("utf-8"), message_thread_id=None)

    # This function turns on webhook
    # *Remember to change the HOOK_TOKEN
    # app.py will invoke this when https://{BASE_URL}/setupwebhook is triggered
    def set_webhook(self, endpoint):
        print (endpoint)
        self.bot.remove_webhook()
        time.sleep(0.1)
        return self.bot.set_webhook(url=endpoint)
    
    # This function turns on webhook
    # app.py will invoke this when https://{BASE_URL}/setupwebhook is triggered
    def remove_webhook(self):
        return self.bot.remove_webhook()

    # This function checks if the user in the chat is an admin
    def isAdmin (self, chat_id, user_id):
        return self.bot.get_chat_member(chat_id,user_id).status in ['administrator','creator']
    
    # This function checks if the user is owner
    def isOwner (self, chat_id, user_id):
        return self.bot.get_chat_member(chat_id,user_id).status == 'creator'
    
    # This function queries for general chat completion prompt
    # *This function is a rare situation where we use the "free" text directly from the user
    # *This is a feature by design, not an injection vulnerability
    def query_ai_gpt35 (self, user_prompt):
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            return completion.choices[0].message["content"]
        
        except openai.OpenAIError as e:
            logging.error ("Caught OpenAIError. Unable to process: \"{prompt}\"".format(prompt = re.escape(user_prompt)))
            raise e

    # This function queries for classification
    def query_ai_classification (self, user_prompt):

        user_prompt = user_prompt + "\n\n###\n\n"
        try:
            response = openai.Completion.create(
                model=self.finetuned_model,
                prompt=user_prompt,
                temperature=0,
                max_tokens=10,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=["###"]
            )

            return response.choices[0].text
        
        except openai.OpenAIError as e:
            logging.error ("Caught OpenAIError. Unable to process: \"{prompt}\"".format(prompt = re.escape(user_prompt)))
            raise e

    # This function checks if the message is job post
    # If it is not a job post, it is forwarded to Career Discussions topic
    def processJobPostingTopic(self,message):
        logging.debug ("processJobPostingTopic")
        
        try:
            return_tokens = self.query_ai_classification(message.text.strip())

            #if it is an job related
            for t in ['jobs', 'career', 'roles']:
                if t in return_tokens:
                    return

            #loosely check if any of the return token is related to jobs
            #move the message to career discussion based on the general observation
            if 'jobs' not in return_tokens: 
                self.bot.forward_message(message.chat.id, message.chat.id, message.id, message_thread_id=self.config['FORUMS']['CAREER_DISCUSSIONS'])
                self.bot.delete_message (message.chat.id, message.id)
                self.bot.send_message(message.chat.id, self.replytxt.format(source_topic="Jobs") , message_thread_id=self.config['FORUMS']['CAREER_DISCUSSIONS'])
                logging.debug("Process moving out {} from the Job Posting to Career discussion topic.".format(message.text.strip()))
        except: 
            traceback.print_exc()
    
    # This function checks if the message supports training
    # If it is not a training post, it is forwarded to Cyber Discussions topic
    def processTrainingPostingTopic(self,message):
        logging.debug ("processTrainingPostingTopic")
        
        try:
            return_tokens = self.query_ai_classification(message.text.strip())

            #if it is a training related, stop processing
            for t in ['training', 'cert', 'resource','learn', 'book', 'reference']:
                if t in return_tokens:
                    return

            #Check if it is news or articles
            #move it to the right place

            #Bot try to keep slient in news and article channels.
            if 'articles' in return_tokens:
                self.bot.forward_message(message.chat.id, message.chat.id, message.id, message_thread_id=self.config['FORUMS']['REPORTS_ARTICLES'])
                self.bot.delete_message (message.chat.id, message.id)    
                logging.debug("Process moving out {} from the Training to Reports and Article topic.".format(message.text.strip()))
            elif 'news' in return_tokens:
                self.bot.forward_message(message.chat.id, message.chat.id, message.id, message_thread_id=self.config['FORUMS']['CYBER_NEWS'])
                self.bot.delete_message (message.chat.id, message.id)
                logging.debug("Process moving out {} from the Training to News topic.".format(message.text.strip()))
            
            #Move to cyber discussion if otherwise
            else:
                self.bot.forward_message(message.chat.id, message.chat.id, message.id, message_thread_id=self.config['FORUMS']['CYBER_DISCUSSIONS'])
                self.bot.delete_message (message.chat.id, message.id)
                self.bot.send_message(message.chat.id, self.replytxt.format(source_topic="Training") , message_thread_id=self.config['FORUMS']['CYBER_DISCUSSIONS'])
                logging.debug("Process moving out {} from the Training to Cyber Discussions topic.".format(message.text.strip()))
        except: 
            traceback.print_exc()
    
    # This function checks if the message is an article
    # If it is a news post, forward it to Cyber News topic
    # If it is not a news post, it is forwarded to Cyber Discussion topic
    def processArticlesPostingTopic(self,message):
        logging.debug ("processArticlePostingTopic")

        try:
            return_tokens = self.query_ai_classification(message.text.strip())

            #if it is an article, we will keep it there.
            if 'articles' in return_tokens:
                return

            #check if it is a news article, make move if looks like a news
            if 'news' in return_tokens: 
                self.bot.forward_message(message.chat.id, message.chat.id, message.id, message_thread_id=self.config['FORUMS']['CYBER_NEWS'])
                self.bot.delete_message (message.chat.id, message.id)
                logging.debug("Process moving out {} from the Articles to News topic.".format(message.text.strip()))
            
            #loosely check if could be an article
            #move the message to cyber discussion group based on general observation
            elif 'others' in return_tokens: 
                self.bot.forward_message(message.chat.id, message.chat.id, message.id, message_thread_id=self.config['FORUMS']['CYBER_DISCUSSIONS'])
                self.bot.delete_message (message.chat.id, message.id)
                self.bot.send_message(message.chat.id, self.replytxt.format(source_topic="Reports and Articles") , message_thread_id=self.config['FORUMS']['CYBER_DISCUSSIONS'])
                logging.debug("Process moving out {} from the Articles to Cyber Discussions topic.".format(message.text.strip()))
        except:
            traceback.print_exc()

    # This function checks if the message is an news
    # If it is a article post, forward it to Reports and Articles topic
    # If it is neither news nor article posts, it is forwarded to Cyber Discussion topic
    def processNewsPostingTopic(self,message):
        logging.debug ("processNewsPostingTopic")

        try:
            return_tokens = self.query_ai_classification(message.text.strip())

            #check if it is either news or article we just keep it there
            for t in ['news','articles']:
                if t in return_tokens:
                    return
            
            #Move conversations to discussions
            if 'others' in return_tokens: 
                self.bot.forward_message(message.chat.id, message.chat.id, message.id, message_thread_id=self.config['FORUMS']['CYBER_DISCUSSIONS'])
                self.bot.delete_message (message.chat.id, message.id)
                self.bot.send_message(message.chat.id, self.replytxt.format(source_topic="News"), message_thread_id=self.config['FORUMS']['CYBER_DISCUSSIONS'])
                logging.debug("Process moving out {} from the News to Cyber Discussions topic.".format(message.text.strip()))
        except:
            traceback.print_exc()

    # This function is invoked when /gpt command is triggered
    def processGPTCommand(self,message):
        logging.debug ("processGPTCommand")

        try:
            all_words = message.text.split()
            if self.isAdmin (message.chat.id,message.from_user.id):
                if len(all_words) == 1:
                    self.bot.reply_to(message,"Usage: /gpt {prompt}")
                else:
                    response = self.query_ai_gpt35(message.text[4:])
                    self.bot.reply_to(message,response)
            else:
                self.bot.reply_to(message,"At present, the /gpt command is reserved for administrators and mentors.\U0001F64F")
        except:
            traceback.print_exc()

    # This function process and dispatch message to the right handler
    # It can be triggered by both polling or web hook triggers
    def processMessage (self,message):
        logging.debug ("processMessage")
        
        #only process text
        if message.content_type != 'text': return

        # Members are not permitted to speak in the General topic
        if message.message_thread_id is None:
            if self.isAdmin(message.chat.id,message.from_user.id) == False:
                self.bot.delete_message (message.chat.id, message.id)
                return

        # Use open ai free text
        # This is only reserved for mentors
        
        if message.text.startswith("/gpt"):
            self.processGPTCommand(message)
            return
        elif message.text.startswith("/rules"):
            self.send_houserules(message)
            return

        # Only owner is permitted to speak in any topic
        # This is the creator's special privilege ;)
        # No futher processing is needed
        if self.mode == 'prod' and self.isOwner(message.chat.id,message.from_user.id):
            return

        #Dispatch processing
        if message.message_thread_id == self.config['FORUMS']['JOB_POSTINGS']:
            self.processJobPostingTopic(message)
        elif message.message_thread_id == self.config['FORUMS']['TRAINING_RESOURCES']:
            self.processTrainingPostingTopic(message)
        elif message.message_thread_id == self.config['FORUMS']['CYBER_NEWS']:
            self.processNewsPostingTopic(message)
        elif message.message_thread_id == self.config['FORUMS']['REPORTS_ARTICLES']:
            self.processArticlesPostingTopic(message)

    # This function is registered to be triggered when configured in polling mode
    # It dispatches message to the processMessage handler
    def handle_messages(self,messages):
        for message in messages:
            self.processMessage (message)
    
    # This function is run when the webhook is triggered
    def process_webhook(self,json_string):
        update = telebot.types.Update.de_json(json_string)        
        self.bot.process_new_updates([update])
    
    # This turns on the polling mode
    # It is useful for testing the features locally
    def poll(self):
        self.bot.infinity_polling()

# Run the main as follows
if __name__ == "__main__":
    scsbot = SCSBotWrapper()
    scsbot.poll()