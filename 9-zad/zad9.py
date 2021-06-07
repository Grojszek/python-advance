import requests

URL = 'https://support.oneskyapp.com/hc/en-us/article_attachments/202761727/example_2.json'

json_data = requests.get(URL).json()

question_list = []
for quiz in json_data:
    for element in json_data[quiz]:
        for i in json_data[quiz][element]:
            question_list.append(json_data[quiz][element][i]['question'])

print(question_list)