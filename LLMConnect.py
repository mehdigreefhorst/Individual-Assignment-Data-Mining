
import helpers

import langchain
import dotenv
dotenv.load_dotenv()
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, SystemMessage, HumanMessage
from langchain.prompts import PromptTemplate
import langchain
import dotenv
import os
dotenv.load_dotenv()
from langchain import hub
from langchain_openai import ChatOpenAI
import json
from typing import List, Dict, Optional, Any
from langchain_core.prompts import ChatPromptTemplate



class ChatModel:
    def __init__(self, model_name='gpt-3.5-turbo',
                 temperature=0.7,
                 max_tokens=1000,
                 response_format=('type', 'text')):

        dotenv.load_dotenv(dotenv.find_dotenv())
        self.model = ChatOpenAI(model_name=model_name,
                                temperature=temperature,
                                max_tokens=max_tokens,
                                response_format={response_format[0]: response_format[1]})
        self.save_location = "data/chat_model_data_last.csv"

    def get_prompt_hub(self, prompt_name):
        """
        gets the prompt from the hub, you must use correct pathing
        :param prompt_name:
        :return:
        """
        return hub.pull(prompt_name)

    def get_response(self, messages):
        """
        gets the response from the model
        :param messages: can be a prompt or a list of interactions between the user and the system
        :return: response object
        :return: messages, list of messages, response is added to messages
        """
        print("I am sending a request to an LLM now")
        response = self.model.invoke(messages)
        messages.append(response)
        return response, messages

    @staticmethod
    def custom_formatting(prompt, **kwargs):
        for key, value in kwargs.items():
            if isinstance(value, list):
                value = json.dumps(value, ensure_ascii=False)
            else:
                value = value
            # prompt = prompt.replace(f'{{{key}}}', value)
            prompt = prompt.replace('{{key}}'.replace("key", key), value)
        return prompt

    def format_prompt_json(self, prompt, **kwargs):
        """
        formats the prompt with the kwargs
        :param prompt: prompt template to format
        :param kwargs:
        :return: formatted prompt
        """
        """for i in range(25):
            try:
                prompt[i].prompt.template = self.custom_formatting(
                    prompt[i].prompt.template, **kwargs)

            except IndexError:
                break"""

        prompt_messages = []

        for i in range(25):
            try:
                output = self.custom_formatting(
                    prompt[i].prompt.template, **kwargs)

                if i == 0:
                    prompt_messages.append(SystemMessage(content=output))
                elif i % 2 == 0:
                    prompt_messages.append(AIMessage(content=output))
                else:
                    prompt_messages.append(HumanMessage(content=output))

            except IndexError:
                break


        return prompt_messages#ChatPromptTemplate.format_messages(prompt_messages)#prompt #prompt.format_messages(**kwargs)

    def get_json_dict_from_response(self, response):
        """
        gets the json output from the response
        Only possible if the response is a json object
        :param response:
        """
        try:

            return json.loads(response.model_dump()['content'])
        except Exception as e:
            assert False, f"response is not a json object, \n error = {e} \nresponse = \n{response}"

class DetectFoodIngredients(ChatModel):
    def __init__(self, model_name='gpt-4o-mini',
                 max_tokens=8000,
                 temperature=0.7,
                 response_format=('type', 'json_object')):
        super().__init__(model_name=model_name,
                         temperature=temperature,
                         max_tokens=max_tokens,
                         response_format=response_format)

    def get_food_detection_prompt(self):
        """
        Creates a custom food detection prompt template
        :return: formatted prompt
        """
        system_message = """
                You are a food detecting agent that responds only in JSON mode.
                Analyze the following list of JSON objects representing food meals and their ingredients.
                """
        user_task = """
        You are a food detecting agent that responds only in JSON mode.
        Analyze the following list of JSON objects representing food meals and their ingredients:
        {{input_json}}
        ---

        For each ingredient in each meal, determine if it contains any of the following categories, you are allowed to 
        label multiple ingredients as 1:
        - poultry
        - red meat
        - fish
        - shellfish
        - dairy products
        - other animal products

        Return the result as a JSON array of objects with the structure:
        "meals": [
            {
                "ingredient_list": "list of food ingredients",
                "meal_number: unique_id
                "poultry": 1 or 0,
                "red_meat": 1 or 0,
                "fish": 1 or 0,
                "shellfish": 1 or 0,
                "dairy_products": 1 or 0,
                "other_animal_products": 1 or 0,
                "none": 1 or 0
            }
        ]
        Only return the array of jsons in dict formats, nothing else.
        
        """
        return ChatPromptTemplate([
            ("system", system_message),
            ("user", user_task)
        ], template_format="mustache")

    def detect_food_ingredients(self, input_json: dict):
        """
        Detect food ingredients categories using the LLM
        :param input_json: JSON input as a string
        :return: categorized JSON output
        """
        # Create the formatted prompt
        prompt_template = self.get_food_detection_prompt()
        formatted_prompt = self.format_prompt_json(prompt=prompt_template,
                                                   input_json=input_json)

        # Send prompt to the model and get a response
        response, messages = self.get_response(formatted_prompt)

        # Parse the JSON response
        detected_food_json = self.get_json_dict_from_response(response)
        helpers.save_json_data(json_data=detected_food_json, relative_path="json/data.json")

        return detected_food_json