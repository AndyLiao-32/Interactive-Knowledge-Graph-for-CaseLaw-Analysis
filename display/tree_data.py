import json
import sys

new_set = {"name": "Topics", "children": []}
index = []
#from collections import defaultdict 
# print(sys.version)

with open("/Users/graceyhchen/GT_Fall2020/CSE6242_viz/02_project/04_visualization/knowledge_graph_for_law_case/display/file_topic_pruning.json") as file:
	data = json.load(file)
	'''
	for k, v in data.items():
		if v[0] not in index:
			index.append(v[0])
	'''
	index=[1,2,3]

	for i in index:
		if str(i) not in new_set["children"]:
			new_set["children"].append({"name": str(i), "children": []})

 
	topic_prefix_order={}#defaultdict(dict)
	for i in index:
		topic_prefix_order[i]={}

	for k, v in data.items():
		keylist= k.split(' ')
		if "v." in keylist[:5]:
			prefix=' '.join(keylist[:keylist[:5].index("v.")+2])
		else:
			prefix=' '.join(keylist[:4])
 
		if prefix not in topic_prefix_order[v[0]]:
			topic_prefix_order[v[0]][prefix]=len(topic_prefix_order[v[0]])

			new_set["children"][v[0]-1]["children"].append({"name": prefix, "children": [{"name":k,"size":v[1]}]})

		else:
			new_set["children"][v[0]-1]["children"][topic_prefix_order[v[0]][prefix]]["children"].append({"name":k,"size":v[1]})

 
# print(len(new_set["children"]))

with open("/Users/graceyhchen/GT_Fall2020/CSE6242_viz/02_project/04_visualization/knowledge_graph_for_law_case/display/file_topic_1120_reverse4.json", "w") as outfile:
    json.dump(new_set, outfile, indent=4, sort_keys=True)