import json
import requests
import yaml
import time

from datetime import date

with open('config/FeishuSheetToken.yaml', 'r', encoding='utf-8') as f:
    FeishusheetToken = yaml.load(f.read(), Loader=yaml.FullLoader)
SpreadsheetToken = FeishusheetToken["spreadsheetToken"]
sheetID = FeishusheetToken["sheetID"]
appid = FeishusheetToken["appid"]
appsecret = FeishusheetToken["appsecret"]


def decimal_to_base26(decimal):
    """
    十进制转换为二十六进制
    :return:
    """
    base26 = ""
    while decimal > 0:
        remainder = (decimal - 1) % 26 + 1
        base26 = chr(remainder + ord('A') - 1) + base26
        decimal = (decimal - 1) // 26
    return base26


def get_tenant_access_token():
    """
    :return: 返回tenant_access_token
    """
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = json.dumps({
        "app_id": appid,
        "app_secret": appsecret
    })

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return eval(response.text)["tenant_access_token"]


def mapping(content):
    res = {}
    res[content[0]] = "2"
    res[content[2]] = "1"
    res[content[4]] = "-1"
    res[content[6]] = "-2"

    return res


class FeishuAccess:
    def __init__(self):
        self.tenant_access_token = get_tenant_access_token()

    def find_competitor(self, competitor_names: tuple):
        """

        :param competitor_names:
        :return: 一个字典，key为competitor_name,value 为索引
        """
        result = {}
        with open("config/PlayerList", "rt", encoding="utf-8") as f:
            competitor_names_list = f.read().split("\n")
        for index in range(len(competitor_names)):
            if competitor_names[index] not in competitor_names_list:
                competitor_names_list.append(competitor_names[index])
            result[competitor_names[index]] = competitor_names_list.index(competitor_names[index]) + 1
        # print(result)
        with open("config/PlayerList", "wt", encoding="utf-8") as f:
            f.write("\n".join(competitor_names_list))

        headers = {
            'Content-Type': 'application/json',
            'Authorization': "Bearer " + self.tenant_access_token
        }

        url = "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/" + SpreadsheetToken + "/values"

        range_score = sheetID["score"] + "!" + "A2" + ":" + "A50"
        range_strength = sheetID["strength"] + "!" + "A2" + ":" + "A50"
        range_luck = sheetID["luck"] + "!" + "B2" + ":" + "B50"

        payload_score = json.dumps({
            "valueRange": {
                "range": range_score,
                "values": [[item] for item in competitor_names_list]
            }
        })

        payload_strength = json.dumps({
            "valueRange": {
                "range": range_strength,
                "values": [[item] for item in competitor_names_list]
            }
        })

        payload_luck = json.dumps({
            "valueRange": {
                "range": range_luck,
                "values": [[item] for item in competitor_names_list]
            }
        })
        response = requests.request("PUT", url, headers=headers, data=payload_score)
        # print(response.text)
        response = requests.request("PUT", url, headers=headers, data=payload_strength)
        # print(response.text)
        response = requests.request("PUT", url, headers=headers, data=payload_luck)
        # print(response.text)
        return result

    def find_the_latest(self):
        with open("config/ROUND.yaml", "rt") as f:
            ROUND = yaml.load(f.read(), Loader=yaml.FullLoader)
        score_strenth_column = decimal_to_base26(ROUND["SCORE_STRENGTH"] + 2)
        # print(ROUND["SCORE_STRENGTH"],ROUND["LUCK"],score_strenth_column)
        ROUND["SCORE_STRENGTH"] += 1
        with open("config/ROUND.yaml", "wt", encoding="utf-8") as f:
            yaml.dump(data=ROUND, stream=f, allow_unicode=True)
        # print(score_strenth_column)
        return score_strenth_column

    def find_the_latest_luck(self):
        with open("config/ROUND.yaml", "rt") as f:
            ROUND = yaml.load(f.read(), Loader=yaml.FullLoader)
        luck_column = decimal_to_base26(ROUND["LUCK"] + 3)
        ROUND["LUCK"] += 1
        with open("config/ROUND.yaml", "wt", encoding="utf-8") as f:
            yaml.dump(data=ROUND, stream=f, allow_unicode=True)
        return luck_column

    def value_put_score(self, content):

        self.tenant_access_token = get_tenant_access_token()
        name2score = {content[index]: content[index + 1] for index in range(0, 8, 2)}
        competitor_names = tuple(name2score.keys())
        seat = self.find_competitor(competitor_names)

        latest_column = self.find_the_latest()

        url = "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/" + SpreadsheetToken + "/values"

        headers = {
            'Content-Type': 'application/json',
            'Authorization': "Bearer " + self.tenant_access_token
        }

        # 写入积分榜

        for competitor_name in competitor_names:
            cell = latest_column + str(seat[competitor_name] + 1)
            cell_1 = latest_column + str(seat[competitor_name] + 1)
            ranges = sheetID["score"] + "!" + cell + ":" + cell_1
            # print(ranges)
            tobewritten = [[name2score[competitor_name]]]
            payload = json.dumps({
                "valueRange": {
                    "range": ranges,
                    "values": tobewritten
                }
            })
            response = requests.request("PUT", url, headers=headers, data=payload)
            # print(response.text)
        ranges = sheetID["score"] + "!" + latest_column + "1:" + latest_column + "2"
        # print(ranges)
        time.sleep(1)
        tobewritten = [[str(date.today())]]
        payload = json.dumps({
            "valueRange": {
                "range": ranges,
                "values": tobewritten
            }
        })
        response = requests.request("PUT", url, headers=headers, data=payload)
        # print(response.text)

        # 写入实力榜
        # 默认content按照名次排行

        name2streangth = mapping(content)

        for competitor_name in competitor_names:
            cell = latest_column + str(seat[competitor_name] + 1)
            cell_1 = latest_column + str(seat[competitor_name] + 1)
            ranges = sheetID["strength"] + "!" + cell + ":" + cell_1
            # print(ranges)
            tobewritten = [[name2streangth[competitor_name]]]
            payload = json.dumps({
                "valueRange": {
                    "range": ranges,
                    "values": tobewritten
                }
            })
            response = requests.request("PUT", url, headers=headers, data=payload)
            # print(response.text)
        ranges = sheetID["strength"] + "!" + latest_column + "1:" + latest_column + "2"
        # print(ranges)
        time.sleep(1)
        tobewritten = [[str(date.today())]]
        payload = json.dumps({
            "valueRange": {
                "range": ranges,
                "values": tobewritten
            }
        })
        response = requests.request("PUT", url, headers=headers, data=payload)
        # print(response.text)

    def value_put_luck(self, content):
        self.tenant_access_token = get_tenant_access_token()
        seat = self.find_competitor([content[0]])

        latest_column = self.find_the_latest_luck()

        url = "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/" + SpreadsheetToken + "/values"

        headers = {
            'Content-Type': 'application/json',
            'Authorization': "Bearer " + self.tenant_access_token
        }
        # print(seat)
        cell = latest_column + str(seat[content[0]] + 1)
        cell_1 = latest_column + str(seat[content[0]] + 1)
        ranges = sheetID["luck"] + "!" + cell + ":" + cell_1
        # print(ranges)
        tobewritten = [[content[1]]]
        payload = json.dumps({
            "valueRange": {
                "range": ranges,
                "values": tobewritten
            }
        })
        response = requests.request("PUT", url, headers=headers, data=payload)

        ranges = sheetID["luck"] + "!" + latest_column + "1:" + latest_column + "2"
        # print(ranges)
        time.sleep(1)
        tobewritten = [[str(date.today())]]
        payload = json.dumps({
            "valueRange": {
                "range": ranges,
                "values": tobewritten
            }
        })
        response = requests.request("PUT", url, headers=headers, data=payload)



if __name__ == "__main__":
    feishuaccess = FeishuAccess()
    feishuaccess.value_put_luck(["孙晓传",4])
