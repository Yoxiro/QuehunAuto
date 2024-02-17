import json
import requests
import time
import yaml

from QQbot import Score
from PIL import Image
from paddleocr import PaddleOCR

reader = PaddleOCR(use_angle_cls=True, lang="ch")  # this needs to run only once to load the model into memory

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

        self.img = Image.open(self.file_name)
        self.width = self.img.size[0]
        self.height = self.img.size[1]

    def detect(self):

        result = reader.ocr(self.file_name)
        result = result[0]
        result_search = [[item[1][0],(item[0][0][0]/self.width,item[0][0][1]/self.height)] for item in result]

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


    def paiyun(self):
        result = reader.ocr(self.file_name)
        result = result[0]
        # result_dict = {item[1]: str(item[0]) for item in result}
        # with open("x.json", "wt", encoding="utf-8") as file:
        #     file.write(json.dumps(result_dict, indent=4, ensure_ascii=False))

        avatar = ""
        for item in result:
            if distance([item[0][0][0] / self.width, item[0][0][1] / self.height], [114 / 1920, 863 / 1080]) <= 0.0005:
                avatar = item[1][0]
                break

        result_char = [item[1][0] for item in result if item[1][0] in self.yis]
        luck = 0
        m=0

        AlarmFlag = False

        for yi in result_char:
            if yi in Score.Alarm1 or yi in Score.Alarm2:
                AlarmFlag = True
            luck += self.yi_to_luck[yi]
        if AlarmFlag:
            m=self.paiyun_fulou()
        return (avatar, luck+m)

    def paiyun_fulou(self):

        box_ori = (870/1920,320/1080,1860/1920,760/1080)
        box_after = (box_ori[0] * self.width,
                     box_ori[1] * self.height,
                     box_ori[2] * self.width,
                     box_ori[3] * self.height)
        region = self.img.crop(box_after)
        region.save('roaming_image/cropped.png')
        result = reader.ocr('roaming_image/cropped.png',cls=False)
        result = result[0]
        print(result)
        result_dict = {item[1][0]: item[0] for item in result}
        # result_dict = {item[1][0]: str(item[0]) for item in result}
        # with open("1.json", "wt", encoding="utf-8") as file:
        #     file.write(json.dumps(result_dict, indent=4, ensure_ascii=False))
        # print(result)

        result_char = [item[1][0] for item in result if item[1][0] in self.yis]

        Alarm1char = [item for item in result_char if item in Score.Alarm1]
        Alarm2char = [item for item in result_char if item in Score.Alarm2]
        minus = 0
        for item in Alarm1char:
            after_position = [result_dict[item][0][0] + 180, result_dict[item][0][1] - 30]
            shortest = 1000
            shortest_index = -1
            for item_in_result_index in range(len(result)):
                examined_postion = result[item_in_result_index][0][0]
                distance1 = (examined_postion[0] - after_position[0]) ** 2 + (
                            examined_postion[1] - after_position[1]) ** 2
                if distance1 <= shortest:
                    shortest_index = item_in_result_index
            if result[shortest_index][1][0] != Score.Minus[item]:
                minus -= 1
            # print(result[shortest_index][1][0])
        # print(minus)
        for item in Alarm2char:
            after_position = [result_dict[item][0][0] + 180, result_dict[item][0][1] - 30]
            shortest = 1000
            shortest_index = -1
            for item_in_result_index in range(len(result)):
                examined_postion = result[item_in_result_index][0][0]
                distance1 = (examined_postion[0] - after_position[0]) ** 2 + (
                            examined_postion[1] - after_position[1]) ** 2
                if distance1 <= shortest:
                    shortest_index = item_in_result_index
            if result[shortest_index][1][0] != Score.Minus[item]:
                minus -= 2
            # print(result[shortest_index][1][0])
        # print(minus)
        return minus


    def paiyun_test(self,path):
        result = reader.ocr(path,cls = False)
        result = result[0]
        # result_dict = {item[1]: str(item[0]) for item in result}
        # with open("x.json", "wt", encoding="utf-8") as file:
        #     file.write(json.dumps(result_dict, indent=4, ensure_ascii=False))

        avatar = ""
        img = Image.open(path)
        width = img.size[0]
        height = img.size[1]

        for item in result:
            if distance([item[0][0][0] / width, item[0][0][1] /height], [114 / 1920, 863 / 1080]) <= 0.0005:
                avatar = item[1][0]
                break

        result_char = [item[1][0] for item in result if item[1][0] in self.yis]
        luck = 0
        minus = 0
        AlarmFlag = False

        for yi in result_char:
            print(yi)
            if yi in Score.Alarm1 or yi in Score.Alarm2:
                AlarmFlag = True
            luck += self.yi_to_luck[yi]
        if AlarmFlag:
            minus = self.paiyun_fulou_test(path)
        luck = luck + minus
        print(avatar,luck)
        return (avatar, luck)

    def paiyun_fulou_test(self,path):

        box_ori = (870/1920,320/1080,1860/1920,760/1080)
        img = Image.open(path)
        width = img.size[0]
        height = img.size[1]

        box_after = (box_ori[0] * width,
                     box_ori[1] * height,
                     box_ori[2] * width,
                     box_ori[3] * height)
        region = img.crop(box_after)
        region.save('roaming_image/cropped.png')
        result = reader.ocr('roaming_image/cropped.png',cls=False)
        result = result[0]
        result_dict = {item[1][0]: item[0] for item in result}
        #result_dict = {item[1][0]: str(item[0]) for item in result}
        # with open("1.json", "wt", encoding="utf-8") as file:
        #     file.write(json.dumps(result_dict, indent=4, ensure_ascii=False))
        # print(result)

        result_char = [item[1][0] for item in result if item[1][0] in self.yis]

        Alarm1char = [item for item in result_char if item in Score.Alarm1]
        Alarm2char = [item for item in result_char if item in Score.Alarm2]
        minus = 0
        for item in Alarm1char:
            after_position = [result_dict[item][0][0]+180 , result_dict[item][0][1]-30]
            shortest = 1000
            shortest_index = -1
            for item_in_result_index in range(len(result)):
                examined_postion = result[item_in_result_index][0][0]
                distance1 = (examined_postion[0] -  after_position[0])**2+(examined_postion[1] -  after_position[1])**2
                if distance1 <= shortest:
                    shortest_index = item_in_result_index
            if result[shortest_index][1][0] != Score.Minus[item]:
                minus-=1
            # print(result[shortest_index][1][0])
        # print(minus)
        for item in Alarm2char:
            after_position = [result_dict[item][0][0]+180 , result_dict[item][0][1]-30]
            shortest = 1000
            shortest_index = -1
            for item_in_result_index in range(len(result)):
                examined_postion = result[item_in_result_index][0][0]
                distance1 = (examined_postion[0] -  after_position[0])**2+(examined_postion[1] -  after_position[1])**2
                if distance1 <= shortest:
                    shortest_index = item_in_result_index
            if result[shortest_index][1][0] != Score.Minus[item]:
                minus-=2
            # print(result[shortest_index][1][0])
        # print(minus)
        return minus
if __name__ == "__main__":
    ocr = Ocr()
