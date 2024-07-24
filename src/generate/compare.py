import os
import json

def load_jsonl(file_path):
    json_list = []
    with open(file_path, 'r') as file:
        for line in file:
            json_obj = json.loads(line)
            json_list.append(json_obj)
    return json_list

def compare_json_objects(json1, json2):
    try:
        code1 = int(json1.get('code', 0))
        code2 = int(json2.get('code', 0))
        value1 = int(json1.get('value', 0))
        value2 = int(json2.get('value', 0))
        unit1 = str(json1.get('unit', '')).strip()
        unit2 = str(json2.get('unit', '')).strip()
        return (code1 == code2 and value1 == value2)
    except ValueError:
        # Handle cases where conversion to int fails
        return False

def compare_jsonl_files(file1_path, file2_path):
    json_list1 = load_jsonl(file1_path)
    json_list2 = load_jsonl(file2_path)
    
    matches = []
    for obj2 in json_list2:
        for obj1 in json_list1:
            if compare_json_objects(obj1, obj2):
                matches.append((obj1, obj2))
                break
    return matches, len(json_list2)

def iterate_and_compare(dir1, dir2):
    match_file_path = 'matches.jsonl'
    accuracy_file_path = 'accuracy.txt'
    
    with open(match_file_path, 'w') as match_file, open(accuracy_file_path, 'w') as accuracy_file:
        for filename in os.listdir(dir1):
            if filename.endswith(".jsonl"):
                file1_path = os.path.join(dir1, filename)
                file2_path = os.path.join(dir2, filename)
                if os.path.exists(file2_path):
                    matches, total_expected = compare_jsonl_files(file1_path, file2_path)
                    for generated, expected in matches:
                        match_file.write(json.dumps({'filename': filename, 'generated': generated, 'expected': expected}) + '\n')
                    accuracy = len(matches) / total_expected * 100 if total_expected else 0
                    accuracy_file.write(f"{filename}: {accuracy:.2f}%\n")
                else:
                    print(f"File {filename} not found in {dir2}")

dir1 = './data/generated'
dir2 = './data/expected'
iterate_and_compare(dir1, dir2)
