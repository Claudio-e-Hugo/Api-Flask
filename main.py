from flask import Flask, jsonify, request
import csv
import json
import os
from math import sqrt, pow

app = Flask(__name__)

p1=[40.6464534,-8.649256]
p2=[ 40.646065, -8.639436 ]  
p3=[ 40.630050, -8.653478 ]
p4=[40.643101,-8.6599]

@app.route("/")
def main():
    return "<p>Hello World!</p>"

@app.route("/handle_lines")
def lines_to_json(csvFilePath="data/csv/lines.csv", jsonFilePath="data/json/lines.json"):
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

@app.route("/handle_csv", methods=["POST", "GET"])
@app.before_first_request
def handle_csv():
    csv_files = []
    if request.get_data().decode("utf-8") != "":
        

        csv_files =[ "data_" + request.get_json()["post"] + ".csv"]
    else:
        csv_files = [pos_csv for pos_csv in os.listdir("data/csv/") if pos_csv.endswith('.csv') and pos_csv != "lines.csv"]
    
    # only executes if the that are missing csv files
    missing_files = list(set(csv_files) - set([str(pos_csv).replace(".json", ".csv") for pos_csv in os.listdir("data/") if pos_csv.endswith('.json') and pos_csv != "lines.json"]))

    print(f"Parsing missing files: {missing_files}\n")

    try:
        for cf in missing_files:
            res = []
            with open('data/csv/' + cf, encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                if cf == "data_cell.csv":
                        for row in csv_reader:
                            if(float(row["lat"])<=p1[0] and float(row["lat"])>=p3[0] and float(row["long"])>=p4[1] and float(row["long"])<=p2[1]):
                                if 'hour' not in row.keys():
                                        res.append({"post":"cell","lat" : float(row["lat"]), "long" : float(row["long"]), "hour" : None, "bitrate" : float(row["bitrate"]), "jitter": float(row["jitter"]), "lost": float(row["lost"])})
                                else:
                                    res.append({"post":"cell","lat" : float(row["lat"]), "long" : float(row["long"]), "hour" : int(row["hour"]), "bitrate" : float(row["bitrate"]), "jitter": float(row["jitter"]), "lost": float(row["lost"])})
                else:
                    for row in csv_reader:
                            if 'hour' not in row.keys():
                                    res.append({"post":cf.replace("data_", "").replace(".csv", "") ,"lat" : float(row["lat"]), "long" : float(row["long"]), "hour" : None, "bitrate" : float(row["bitrate"]), "jitter": float(row["jitter"]), "lost": float(row["lost"])})
                            else:
                                res.append({"post":cf.replace("data_", "").replace(".csv", "") ,"lat" : float(row["lat"]), "long" : float(row["long"]), "hour" : int(row["hour"]), "bitrate" : float(row["bitrate"]), "jitter": float(row["jitter"]), "lost": float(row["lost"])})
            file.close()

            with open('data/json/' + cf.replace("csv", "json"), 'w', encoding='utf-8') as file:
                json_string = json.dumps(res, indent=4)
                file.write(json_string)
            file.close()
        return {"v" : True}
    except Exception as e:
        print("Error: " + str(e))
        return {"v" : False}

# @app.route("/handle_p15")
# def p15_to_json(csv_file="data/data_p15.csv", json_file="data/data_p15.json"):
#     try:
#         res = []
#         with open(csv_file, encoding='utf-8') as file:
#             csv_reader = csv.DictReader(file)

#             for row in csv_reader:
#                 res.append({"lat" : float(row["lat"]), "long" : float(row["long"]), "bitrate" : float(row["bitrate_p15"]), "jitter": float(row["jitter_p15"]), "lost": float(row["lost_p15"])})
#         file.close()

#         with open(json_file, 'w', encoding='utf-8') as file:
#             json_string = json.dumps(res, indent=4)
#             file.write(json_string)
#         file.close()
#         return {"v" : True}
#     except:
#         return {"v" : False}

# @app.route("/handle_p19")
# def p19_to_json(csv_file="data/data_p19.csv", json_file="data/data_p19.json"):
    # try:
    #     res = []
    #     with open(csv_file, encoding='utf-8') as file:
    #         csv_reader = csv.DictReader(file)
    #         for row in csv_reader:
    #             res.append({"lat" : float(row["lat"]), "long" : float(row["long"]), "bitrate" : float(row["bitrate_p19"]), "jitter": float(row["jitter_p19"]), "lost": float(row["lost_p19"])})
    #     file.close()

    #     with open(json_file, 'w', encoding='utf-8') as file:
    #         json_string = json.dumps(res, indent=4)
    #         file.write(json_string)
    #     file.close()
    #     return {"v" : True}
    # except:
    #     return {"v" : False}

# @app.route("/handle_cell")
# def cell_to_json(csv_file="data/data_cell.csv", json_file="data/data_cell.json"):
    # try:
    #     res = []
    #     tmp = []
    #     with open(csv_file, encoding='utf-8') as file:
    #         csv_reader = csv.DictReader(file)

    #         for row in csv_reader:
    #             tmp.append({"lat" : float(row["lat"]), "long" : float(row["long"]), "bitrate" : float(row["bitrate_cell"]), "jitter": float(row["jitter_cell"]), "lost": float(row["lost_cell"])})
    #             if len(tmp) >= 5:
    #                 res.append(
    #                     {
    #                         "lat": sum([x["lat"] for x in tmp])/len(tmp),
    #                         "long": sum([x["long"] for x in tmp])/len(tmp),
    #                         "bitrate": sum([x["bitrate"] for x in tmp])/len(tmp),
    #                         "jitter": sum([x["jitter"] for x in tmp])/len(tmp),
    #                         "lost": sum([x["lost"] for x in tmp])/len(tmp)
    #                     }
    #                 )
    #                 tmp = []

    #     file.close()

    #     with open(json_file, 'w', encoding='utf-8') as file:
    #         json_string = json.dumps(res, indent=4)
    #         file.write(json_string)
    #     file.close()
    #     return {"v": True}
    # except:
    #     return {"v": False}

@app.route("/get_json/", methods=["POST", "GET"])
def get_json():
    json_files = []
    if request.get_data().decode("utf-8") != "":
        json_files = ["data_" + request.get_json()["post"] + ".json"]
    else:
        json_files = [pos_json for pos_json in os.listdir("data/json/") if pos_json.endswith('.json') and pos_json != "lines.json"]
    res = {}
    for jf in json_files:
        try:
            f = open("data/json/" + jf, 'r')
            post_data = json.load(f)
            f.close()
            res[jf.replace("data_", "").replace(".json", "")] = post_data
        except:
            print(f"File {jf} does not exists")
            return 500
    return jsonify(res)


@app.route("/get_lines", methods=['GET'])
def get_lines():
    try:
        f = open("data/json/lines.json", 'r')
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
@app.route("/handle_segments", methods=["POST", "GET"])
def handle_segments():
    f_lines = open("data/json/lines.json", "r")
    lines_data = json.load(f_lines)
    json_files = []
    if request.get_data().decode("utf-8") != "":
        json_files =[ "data_" + request.get_json()["post"] + ".json"]
    else:
        json_files = [pos_json for pos_json in os.listdir("data/json/") if pos_json.endswith('.json') and pos_json != "lines.json"]
    
    already_segmented = [pos_json for pos_json in os.listdir("data/json/segmented/") if pos_json.endswith('.json') and pos_json != "lines.json"]
    
    res = {}
    res2 = {}

    if len(already_segmented) != 2:
        for jf in json_files:
            print(f"Handling segments for {jf}\n")
            f_post = open("data/json/" + jf)
            post_data = json.load(f_post)
            aux = {}
            aux2 = {}
            for street in lines_data:
                for segment in lines_data[street]:
                    max_seg_lat = max([segment[0][0], segment[1][0]])
                    max_seg_long = max([segment[0][1], segment[1][1]])
                    min_seg_lat = min([segment[0][0], segment[1][0]])
                    min_seg_long = min([segment[0][1], segment[1][1]])
                    aux[str(segment)] = []
                    aux2[str(segment)] = []
                    for element in post_data:
                        if (min_seg_lat <= element["lat"] and max_seg_lat >= element["lat"]) and (min_seg_long <= element["long"] and max_seg_long >= element["long"]):
                            aux[str(segment)].append(element)
                            aux2[str(segment)].append(element)

            res[jf.replace("data_", "").replace(".json", "")] = average_post_data(aux)
            res2[jf.replace("data_", "").replace(".json", "")] = aux2

        with open('data/json/segmented/segmented_data.json', 'w', encoding='utf-8') as file:
            json_string = json.dumps(res, indent=4)
            file.write(json_string)
        file.close()

        with open('data/json/segmented/best_segmented_data.json', 'w', encoding='utf-8') as file:
            json_string = json.dumps(get_best_values(res2), indent=4)
            file.write(json_string)
        file.close()

    print("Finished handling segments")

    f = open('data/json/segmented/segmented_data.json', 'r')
    segmented = json.load(f)
    f.close()

    f = open('data/json/segmented/best_segmented_data.json', 'r')
    best_segmented = json.load(f)
    f.close()

    return jsonify([segmented, best_segmented])

def average_post_data(data):
    res = {}
    for segment in data:
        if len(data[segment]) > 0:
            bitrate = sum([float(x["bitrate"]) for x in data[segment]]) / len(data[segment])
            jitter = sum([float(x["jitter"]) for x in data[segment]]) / len(data[segment])
            lost = sum([float(x["lost"]) for x in data[segment]]) / len(data[segment])
        # else:
        #     bitrate = 0
        #     jitter = 0
        #     lost = 0
            res[segment] = {"bitrate": bitrate, "jitter": jitter, "lost": lost}
    return res                  

def get_best_values(data):
    res = {}
    
    for post in data:
        for segment in data[post]:
            if len(data[post][segment]) > 0:
                for values in data[post][segment]:
                    if segment not in res.keys():
                        res[segment] = values
                        res[segment]["best_post_bitrate"] = post
                        res[segment]["lat_bitrate"] = values["lat"]
                        res[segment]["long_bitrate"] = values["long"]
                        res[segment]["best_post_jitter"] = post
                        res[segment]["lat_jitter"] = values["lat"]
                        res[segment]["long_jitter"] = values["long"]
                        res[segment]["best_post_lost"] = post
                        res[segment]["lat_lost"] = values["lat"]
                        res[segment]["long_lost"] = values["long"]
                    else:
                        if (float(values["bitrate"]) >= float(res[segment]["bitrate"])) and (distance_points(post, [values["lat"], values["long"]]) < distance_points(post, [res[segment]["lat_bitrate"], res[segment]["long_bitrate"]])):
                            res[segment]["bitrate"] = values["bitrate"]
                            res[segment]["best_post_bitrate"] = post
                            res[segment]["lat_bitrate"] = values["lat"]
                            res[segment]["long_bitrate"] = values["long"]
                        if float(values["jitter"]) <= float(res[segment]["jitter"]) and (distance_points(post, [values["lat"], values["long"]]) < distance_points(post, [res[segment]["lat_jitter"], res[segment]["long_jitter"]])):
                            res[segment]["jitter"] = values["jitter"]
                            res[segment]["best_post_jitter"] = post
                            res[segment]["lat_jitter"] = values["lat"]
                            res[segment]["long_jitter"] = values["long"]
                        if float(values["lost"]) <= float(res[segment]["lost"]) and (distance_points(post, [values["lat"], values["long"]]) < distance_points(post, [res[segment]["lat_lost"], res[segment]["long_lost"]])):
                            res[segment]["lost"] = values["lost"]
                            res[segment]["best_post_lost"] = post
                            res[segment]["lat_lost"] = values["lat"]
                            res[segment]["long_lost"] = values["long"]
                            

    return res

def distance_points(post, point2):
    post_coords = {
        'p15': [40.64416, -8.65616],
        'p19' : [40.64339, -8.65847],
        'p3' : [40.64074, -8.65705],
        'p5' : [40.64088, -8.65397],
        'p35':[40.63028, -8.65423],
        'p26':[40.63848, -8.65147]
    }
    if post != 'cell':
        return sqrt(pow(point2[0]-post_coords[post][0], 2) + pow(point2[1]-post_coords[post][1], 2))
    return 0

def subset_cells(data,p1,p2,p3,p4):
    res = []
    for element in data:
        #if element lat and long are between the points of the polygon then add to the list
        if(element["lat"]<=p1[0] and element["lat"]>=p3[0] and element["long"]>=p4[1] and element["long"]<=p2[1]):
            res.append(element)
        
    return res


# def order_hours(data):
#     res = []
#     for element in data:
#         if data["hour"] not in res.keys():
#             res[data["hour"]]=element
#         else:
#             res[data["hour"]].append(element)


#     return res