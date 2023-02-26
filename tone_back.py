import os
import openai
from dotenv import load_dotenv
import re

load_dotenv()


# Load your API key from an environment variable or secret management service
class AI:
    def __init__(self):
        openai.api_key = os.getenv("API_KEY")
        self.model = "text-davinci-003"
        self.temp = .4
        self.max_token = 200


    def getRating(self, message):
        prompt = "Rate this slack text from 0-20 on professionalism on tone and vocabulary, and only tell me the number, no words!:" + message


        response = openai.Completion.create(model=self.model, max_tokens=self.max_token, prompt=prompt,
                                            temperature=.2)
        for result in response.choices:
            res = result.text.replace('\n','')
            # print('prompts:',message,": results",res)
            
            
            return result.text


    def getSummary(self, allChatText):
        prompt = 'Provide a brief summary for the following chats with people names included.  : \n'
        for chat in allChatText:
            prompt += chat + '\n'
            # print(prompt)

        response = openai.Completion.create(model='text-davinci-003',max_tokens=400,prompt=prompt, temperature=.7)

        # print(response.choices[0].text)
        return response.choices[0].text



class TextAnalysis:
    def __init__(self, listOfMessages,purpose):
        self.purpose = purpose
        self.listOfMessages = self.parseMessage(listOfMessages)
        self.total = 0
        self.engine = AI()
        
        # Model for tone analysis

        self.tone_dict = {"nonchalant": "This type of language and tone in this chat is not appropriate for"
                                        " a professional or academic setting, and could be "
                                        " as personal, sarcastic or even confrontational. ",
                          "very casual": "Conversations in this chat may include personal anecdotes,"
                                         " jokes, and sarcastic comments that are "
                                         "not meant to be taken seriously. May include some offensive "
                                         "language",
                          "casual": "The tone of this chat is often playful and "
                                    "may include jokes, memes, and GIFs. "
                                    "Participants in the chat may use informal language and "
                                    "emojis to express themselves.",
                          "professional": "The tone of this chat is appropriate "
                                          "for a professional or academic setting.",
                          "very professional": "The tone is helpful and informative, "
                                               "without any unnecessary or offensive language."
                                               " Overall, the tone of this chat is appropriate for "
                                               "a professional or customer service setting."}

    def analyzeMessages(self):
        
        for message in self.listOfMessages:
            resp = self.engine.getRating(message)
            try:
                self.total += int(resp)
            except:
                # print('BAD AI')
                splace = 0
                for pos,char in enumerate(resp):
                    if char.isdigit():
                       splace = pos 
                       break
                self.total += int(resp[splace:])
                # print(resp[splace:])

        average = self.total // (len(self.listOfMessages))
        return int(average*.90 )

    def parseMessage(self,oldmessage):
        
        new_slack_message = []
        for array in oldmessage:
            key = array[0]
            value = array[1]
            
            if self.purpose == 'tone':
                if not (key.endswith('has joined the channel') or key.endswith('has been added to the channel')):
                    new_slack_message.append(key)
            else:
                new_slack_message.append(value+':'+key)

        return new_slack_message


    def summaryResponse(self):
        return self.engine.getSummary(self.listOfMessages)
        
    def toneResponse(self):
        tone_average = self.analyzeMessages()
        # print('REAL',tone_average)

        if tone_average in [0, 1, 2]:
            return self.tone_dict["nonchalant"]
        if tone_average in [3,4, 5, 6]:
            return self.tone_dict["very casual"]
        if tone_average in [7, 8, 9, 10]:
            return self.tone_dict["casual"]
        if tone_average in [11, 12, 13, 14, 15]:
            return self.tone_dict["professional"]
        if tone_average in [16, 17, 18, 19, 20]:
            return self.tone_dict["very professional"]
