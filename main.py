from crypt import methods
from types import TracebackType
from flask import Flask, jsonify, request
import csv
import json

app = Flask(__name__)

@app.route("/")
def main():
    return "<p>Hello World!</p>"

@app.route("/handle_lines")
def lines_to_json(csvFilePath="data/lines.csv", jsonFilePath="data/lines.json"):
    try:
        res = {}
        with open(csvFilePath, encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)

            for row in csv_reader:
                tmp_row = row["geometry"].replace("LINESTRING (", "").split(", ")
                for i in range(0,1):
                    tmp_row2 = tmp_row[i+1].replace(")", "")+" "+tmp_row[i].replace(")", "")
                    tmp_row2 = tmp_row2.split(" ")
                    tmp_row2=[[float(tmp_row2[1]),float(tmp_row2[0])],[float(tmp_row2[3]),float(tmp_row2[2])]] #
                if row["name"] != "":
                    street = row["name"]
                    if street not in res:
                        res[street] = [(tmp_row2)]
                    else:
                        res[street].append((tmp_row2))
                elif row["ref"] != "":
                    street = row["ref"]
                    if street not in res:
                        res[street] = [(tmp_row2)]
                    else:
                        res[street].append((tmp_row2))
                else:
                    street = "unknown"
                    if street not in res:
                        res[street] = [(tmp_row2)]
                    else:
                        res[street].append((tmp_row2))

        with open(jsonFilePath, 'w', encoding='utf-8') as json_file:
            json_string = json.dumps(res, indent=4)
            json_file.write(json_string)
        return {"v" : True}
    except:
        return {"v" : False}

@app.route("/handle_p15")
def p15_to_json(csv_file="data/data_p15.csv", json_file="data/data_p15.json"):
    try:
        res = []
        with open(csv_file, encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)

            for row in csv_reader:
                res.append({"lat" : float(row["lat"]), "long" : float(row["long"]), "bitrate" : float(row["bitrate_p15"]), "jitter": float(row["jitter_p15"]), "lost": float(row["lost_p15"])})
        file.close()

        with open(json_file, 'w', encoding='utf-8') as file:
            json_string = json.dumps(res, indent=4)
            file.write(json_string)
        file.close()
        return {"v" : True}
    except:
        return {"v" : False}

@app.route("/handle_p19")
def p19_to_json(csv_file="data/data_p19.csv", json_file="data/data_p19.json"):
    try:
        res = []
        with open(csv_file, encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                res.append({"lat" : float(row["lat"]), "long" : float(row["long"]), "bitrate" : float(row["bitrate_p19"]), "jitter": float(row["jitter_p19"]), "lost": float(row["lost_p19"])})
        file.close()

        with open(json_file, 'w', encoding='utf-8') as file:
            json_string = json.dumps(res, indent=4)
            file.write(json_string)
        file.close()
        return {"v" : True}
    except:
        return {"v" : False}

@app.route("/handle_cell")
def cell_to_json(csv_file="data/data_cell.csv", json_file="data/data_cell.json"):
    try:
        res = []
        tmp = []
        with open(csv_file, encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)

            for row in csv_reader:
                tmp.append({"lat" : float(row["lat"]), "long" : float(row["long"]), "bitrate" : float(row["bitrate_cell"]), "jitter": float(row["jitter_cell"]), "lost": float(row["lost_cell"])})
                if len(tmp) >= 5:
                    res.append(
                        {
                            "lat": sum([x["lat"] for x in tmp])/len(tmp),
                            "long": sum([x["long"] for x in tmp])/len(tmp),
                            "bitrate": sum([x["bitrate"] for x in tmp])/len(tmp),
                            "jitter": sum([x["jitter"] for x in tmp])/len(tmp),
                            "lost": sum([x["lost"] for x in tmp])/len(tmp)
                        }
                    )
                    tmp = []

        file.close()

        with open(json_file, 'w', encoding='utf-8') as file:
            json_string = json.dumps(res, indent=4)
            file.write(json_string)
        file.close()
        return {"v": True}
    except:
        return {"v": False}

@app.route("/get_json/", methods=["POST"])
def get_json():
    filename = "data_" + request.get_json()["post"] + ".json"
    try:
        f = open("data/" + filename, 'r')
        data = json.load(f)
        f.close()
        return jsonify(data), 201
    except:
        print(f"File {filename} does not exists")
        return 500

@app.route("/get_lines", methods=['GET'])
def get_lines():
    try:
        f = open("data/lines.json", 'r')
        data = json.load(f)
        f.close()
        return jsonify(data), 201
    except:
        print("An error ocurred while trying to load lines.json")
        return 500

'''
    get all segments from lines
    get all points that are inside one segment
    average between all points inside the segment
'''

@app.route("/handle_segments", methods=["POST"])
def handle_segments():
    f_lines = open("data/lines.json", "r")
    lines_data = json.load(f_lines)
    post_name = "data_" + request.get_json()["post"] + ".json"
    f_post = open("data/"+post_name)
    post_data = json.load(f_post)
    res = {}
    for street in lines_data:
        for segment in lines_data[street]:
            max_seg_lat = max([segment[0][0], segment[1][0]])
            max_seg_long = max([segment[0][1], segment[1][1]])
            min_seg_lat = min([segment[0][0], segment[1][0]])
            min_seg_long = min([segment[0][1], segment[1][1]])
            res[str(segment)] = []
            for element in post_data:
                if (min_seg_lat <= element["lat"] and max_seg_lat >= element["lat"]) and (min_seg_long <= element["long"] and max_seg_long >= element["long"]):
                    res[str(segment)].append(element)
    res = average_post_data(res)

    # print(json.dumps(res, indent=4))
    res = jsonify(res)
    return res

def average_post_data(data):
    res = {}
    for segment in data:
        if len(data[segment]) > 0:
            bitrate = sum([float(x["bitrate"]) for x in data[segment]]) / len(data[segment])
            jitter = sum([float(x["jitter"]) for x in data[segment]]) / len(data[segment])
            lost = sum([float(x["lost"]) for x in data[segment]]) / len(data[segment])
        else:
            bitrate = 0
            jitter = 0
            lost = 0
        res[segment] = {"bitrate": bitrate, "jitter": jitter, "lost": lost}
    return res    
