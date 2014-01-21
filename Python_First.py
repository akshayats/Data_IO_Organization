import json
from pprint import pprint
import os

import xml.etree.ElementTree as ET


print 'Hello, world!'
#name = raw_input('What is your name?\n')
#print 'Hi, %s.' % name

with open("bham_office_desk_500.json") as in_file:
           scenes = json.load(in_file)
           print(scenes[0]["orientation"]["monitor"][3])

print len(scenes)
print scenes[0]['scene_id']

tree = ET.parse('Akshaya_Table_2110_Mor_seg.xml')
root = tree.getroot()

print root.tag 
print root.attrib
for child in root:
	print(child.tag, child.attrib)

num_string   = root[3][1][4].text
print  root[1].text

pathoffile   = root[1].text

print pathoffile

withoutext   = os.path.splitext(pathoffile)[0]
print withoutext

withoutext   = os.path.splitext(withoutext)[0]
print withoutext

k = withoutext.split("/",200)
m = k[-1]
print m

n = m.split("_seg",200)
n = n[0]
print n

numbers = list()
numbers.append([1,2,3])
numbers.append([11,22,33])

print numbers

# print pathoffile[::-1]
# q   = pathoffile[pathoffile.index("lmx.")+len("lmx."):pathoffile.index("thisout")+len("thisout")]

# s   = "asdf23rlkasdfidsiwanttocutthisoutsadlkljasdfhvaildufhblkajsdhf"
# q   = s[s.index("iwant"):s.index("thisout")+len("thisout")]

# print q


#########

nums = []
count = 0
for indx in num_string.split():
	# print int(indx)
	nums.append(int(indx))
	count += 1

# print float(root[3][1][4].text) + 5

# for child in root.iter('dimensions'):
# 	print(dimensions.attrib)

#with open("trial.json",'w') as out_file:
   # out_file.write(json.dumps(scenes, out_file, indent=2))

# data["maps"][0]["id"]
# data["masks"]["id"]
# data["om_points"]