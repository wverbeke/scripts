import json
import os
import sys
from datetime import datetime

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
JSON_DIR = "timestamp_jsons"
BASE_NAME = "timestamps_per_class"

def _encode(ts):
    if ts is None:
        return "None"
    return datetime.strftime(ts, TIME_FORMAT)

def _decode(ts_str):
    if ts_str == "None":
        return None
    return datetime.strptime(ts_str, TIME_FORMAT)
   

class TimeStamp:
    
    def __init__(self, begin=None, end=None):
        self._begin = begin
        self._end = end

    @property
    def begin(self):
        return self._begin

    @property
    def end(self):
        return self._end

    def has_end(self):
        return (self._end is not None)

    def __str__(self):
        return f"{_encode(self.begin)},{_encode(self.end)}"

    @staticmethod
    def from_string(encoded_ts):
        begin_str, end_str = encoded_ts.split(",")
        return TimeStamp(begin=_decode(begin_str), end=_decode(end_str))


class TimeDict:

    def __init__(self, class_dict):
        self._class_dict = class_dict

    @staticmethod
    def from_json(json_path):
        with open(json_path) as f:
            json_dict = json.load(f)
        class_dict = {k: TimeStamp.from_string(s) for k, s in json_dict.items()}
        return TimeDict(class_dict=class_dict)

    def to_json(self, json_path):
        json_dict = {k: str(ts) for k, ts in self._class_dict.items()}
        with open(json_path, "w") as f:
            json.dump(json_dict, f)

    def add_timestamp(self, class_name):
        time = datetime.now()
        if class_name not in self._class_dict:
            self._class_dict[class_name] = TimeStamp(begin=time, end=None)
        else:
            ts = self._class_dict[class_name]

            # A full timestamp already exists for this class.
            if ts.has_end():
                class_key = (class_name + "_")
                self.add_timestamp(class_key)

            ts = TimeStamp(begin=ts.begin, end=time)
            self._class_dict[class_name] = ts


def generate_json_path(base_name, index):
    if base_name.endswith(".json"):
        base_name = os.path.splitext(base_name)[0]
    return os.path.join(JSON_DIR, f"{base_name}_{index}.json")


def get_json_index(path):
    path = os.path.splitext(path)[0]
    path = os.path.basename(path)
    index = int(path.split("_")[-1])
    return index


def latest_json_path():
    jsons = os.listdir(JSON_DIR)
    if not jsons:
        return None
    paths_with_indices = [(p, get_json_index(p)) for p in jsons]
    max_index = 0
    latest_path = None
    for p, i in paths_with_indices:
        if i > max_index:
            latest_path = p
            max_index = i
    return os.path.join(JSON_DIR, latest_path)


def update_time_dict(class_name):
    latest_path = latest_json_path()
    if latest_path is not None:
        new_path = generate_json_path(BASE_NAME, get_json_index(latest_path) + 1)
        current_time_dict = TimeDict.from_json(latest_path)
    else:
        new_path = generate_json_path(BASE_NAME, 1)
        current_time_dict = TimeDict({})
    current_time_dict.add_timestamp(class_name=class_name)
    current_time_dict.to_json(new_path)



if __name__ == "__main__":
    os.makedirs(JSON_DIR, exist_ok=True)
    class_name = sys.argv[1]
    update_time_dict(class_name=class_name)
