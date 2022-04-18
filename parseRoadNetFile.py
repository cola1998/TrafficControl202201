import json

def jsonTo():  # 反序列化
    jsonFileName = ''
    with open(jsonFileName) as fp:
        data = json.load(fp)

    xml_content = '<?xml version="1.0" encoding="UTF-8"?>'
    '''
    里面有多个intersections
    '''

    for intersection in data['intersections']:
        # 字典类型
        pass
    "<net>"
    "<loction />"
    "<edge>"
    "</edge>"
    "<tlLogic id={0} type='static' programID='0' offset='0'>"
    "<phase duration={0} state={1}>"
    "</tlLogic>"

    "<junction>"
    "</junction>"
    "<connection />"

    "</net>"
    for road in data['roads']:
        pass
