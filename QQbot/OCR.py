import easyocr
import json
import requests
import time
import yaml

from QQbot import Score
from PIL import Image

reader = easyocr.Reader(['ch_sim', 'en'])  # this needs to run only once to load the model into memory


# result = reader.readtext(r'images\quehun1.png')
# result_dict = {i[1]:str(i[0]) for i in result}
# with open("../result.json", "w", encoding="utf-8") as f:
#     json.dump(result_dict,f,
#               indent=4,
#               ensure_ascii=False)
def distance(list_2, point_2):
    x = (list_2[0] - point_2[0]) ** 2
    y = (list_2[1] - point_2[1]) ** 2
    return x + y


def decoder(file: str) -> dict:
    result = dict()
    lines = file.split("\n")
    for line in lines:
        line_split = line.split(":")
        line_name = line_split[0]
        line_items = line_split[1].split(",")
        result[line_name] = line_items
        # print(line_name,line_items)
    return result


class Ocr:

    def __init__(self):
        self.height = 0
        self.width = 0
        self.yi_to_luck = {}
        # self.reader = reader

        Yi_man = Score.Yi_man
        DoubleYi_man = Score.DoubleYi_man
        Six_Fan = Score.Six_Fan
        Three_Fan = Score.Three_Fan
        Two_Fan = Score.Two_Fan
        One_Fan = Score.One_Fan

        for item in Yi_man:
            self.yi_to_luck[item] = Score.Yi_man_Score
        for item in DoubleYi_man:
            self.yi_to_luck[item] = Score.DoubleYi_man_Score
        for item in Six_Fan:
            self.yi_to_luck[item] = Score.Six_Fan_Score
        for item in Three_Fan:
            self.yi_to_luck[item] = Score.Three_Fan_Score
        for item in Two_Fan:
            self.yi_to_luck[item] = Score.Two_Fan_Score
        for item in One_Fan:
            self.yi_to_luck[item] = Score.One_Fan_Score

        self.yis = tuple(self.yi_to_luck.keys())

    def get_url(self, url):
        self.url = "https://" + url
        get = requests.get(self.url)
        loca = time.strftime('%Y-%m-%d-%H-%M-%S')
        new_name = str(loca) + ".jpg"
        self.file_name = "roaming_image/" + new_name
        try:
            with open(self.file_name, 'wb') as f:
                f.write(get.content)
        except:
            print('Fail to get the picture')

        img = Image.open(self.file_name)
        self.width = img.size[0]
        self.height = img.size[1]

    def detect(self):

        result = reader.readtext(self.file_name)

        result_search = [[item[1],(item[0][0][0]/self.width,item[0][0][1]/self.height)] for item in result]
        paiming = ["", "", "", "", "", "", "", ""]
        for item in result_search:
            if distance(item[1],(0.504, 0.180)) <= 0.0005:
                paiming[0] = item[0]
            if distance(item[1],(0.554, 0.388)) <= 0.0005:
                paiming[2] = item[0]
            if distance(item[1],(0.606, 0.558)) <= 0.0005:
                paiming[4] = item[0]
            if distance(item[1],(0.655, 0.725)) <= 0.0005:
                paiming[6] = item[0]

            if distance(item[1],(0.518, 0.236)) <= 0.0005:
                paiming[1] = item[0]
            if distance(item[1],(0.565, 0.433)) <= 0.0005:
                paiming[3] = item[0]
            if distance(item[1],(0.616, 0.602)) <= 0.0005:
                paiming[5] = item[0]
            if distance(item[1],(0.668, 0.770)) <= 0.0005:
                paiming[7] = item[0]

        for l in [1, 3, 5, 7]:
            if "一" in paiming[l]:
                paiming[l].replace("一", "-")
        return paiming

    def detect_test(self, path):
        result = reader.readtext(path)
        paiming = ["", "", "", "", "", "", "", ""]

        img = Image.open(path)
        self.width = img.size[0]
        self.height = img.size[1]

        # print(self.width)
        # print(self.height)
        result_search = [[item[1], (item[0][0][0] / self.width, item[0][0][1] / self.height)] for item in result]
        result_dict = {item[1]: str(item[0][0][0] / self.width) + str(item[0][0][1] / self.height) for item in result}
        with open("x.json", "wt", encoding="utf-8") as file:
            file.write(json.dumps(result_dict, indent=4, ensure_ascii=False))

        result_dict = {item[1]: str(item[0]) for item in result}
        with open("y.json", "wt", encoding="utf-8") as file:
            file.write(json.dumps(result_dict, indent=4, ensure_ascii=False))
        # print(result)

        result_search = [[item[1], (item[0][0][0] / self.width, item[0][0][1] / self.height)] for item in result]
        paiming = ["", "", "", "", "", "", "", ""]
        for item in result_search:
            if distance(item[1], (0.504, 0.180)) <= 0.0005:
                paiming[0] = item[0]
            if distance(item[1], (0.655, 0.725)) <= 0.0005:
                paiming[6] = item[0]
            if distance(item[1], (0.554, 0.388)) <= 0.0005:
                paiming[2] = item[0]
            if distance(item[1], (0.606, 0.558)) <= 0.0005:
                paiming[4] = item[0]

            if distance(item[1], (0.518, 0.236)) <= 0.0005:
                paiming[1] = item[0]
            if distance(item[1], (0.565, 0.433)) <= 0.0005:
                paiming[3] = item[0]
            if distance(item[1], (0.616, 0.602)) <= 0.0005:
                paiming[5] = item[0]
            if distance(item[1], (0.668, 0.770)) <= 0.0005:
                paiming[7] = item[0]

        for l in [1, 3, 5, 7]:
            if "一" in paiming[l]:
                paiming[l].replace("一", "-")

        print(paiming)

    def paiyun(self):
        result = reader.readtext(self.file_name)
        # result_dict = {item[1]: str(item[0]) for item in result}
        # with open("x.json", "wt", encoding="utf-8") as file:
        #     file.write(json.dumps(result_dict, indent=4, ensure_ascii=False))
        result_char = [item[1] for item in result if item[1] in self.yis]
        luck = 0
        for yi in result_char:
            luck += self.yi_to_luck[yi]
        # print(luck)
        if ("混一色" in result_char) and not ("门前清自摸和" in result_char):
            luck -= 2
        # print(luck)
        avatar = ""
        for item in result:
            if distance([item[0][0][0]/self.width,item[0][0][1]/self.height], [114/1920, 863/1080]) <= 0.0005:
                avatar = item[1]
                break

        return (avatar, luck)

    def paiyun_test(self, file_name):
        result = reader.readtext(file_name)

        img = Image.open(file_name)
        self.width = img.size[0]
        self.height = img.size[1]

        result_dict = {item[1]: str(item[0]) for item in result}
        with open("x.json", "wt", encoding="utf-8") as file:
            file.write(json.dumps(result_dict, indent=4, ensure_ascii=False))
        result_char = [item[1] for item in result if item[1] in self.yis]

        luck = 0
        for yi in result_char:
            luck += self.yi_to_luck[yi]
        # print(luck)
        if ("混一色" in result_char) and not ("门前清自摸和" in result_char):
            luck -= 2
        # print(luck)
        avatar = ""

        for item in result:
            if distance([item[0][0][0] / self.width, item[0][0][1] / self.height], [114 / 1920, 863 / 1080]) <= 0.0005:
                avatar = item[1]
                break
        print(avatar, luck)
        return (avatar, luck)


if __name__ == "__main__":
    ocr = Ocr()
