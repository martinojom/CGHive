import maya.cmds as cmds

# index color values
# blue = 6
# red = 13
# green = 14
# darker green = 23
# yellow = 17
# ligter green = 25
colour_index = 25

skin = "l_rear_arm_ribbonShape"
objList = []
num = 0
# create controllers on top of the joint and group
for obj in cmds.ls(selection=True):
    objTranslation = cmds.xform(obj, query=True, translation=True)
    name = obj.replace("_ctrljnt", "_ctrl")
    jntController = cmds.circle(name=name, sweep=360, radius=4, degree=3, 
    sections=8, normal=(0,1,0), constructionHistory=True)
    # cmds.xform(jntController, translation=objTranslation)
    objList.append(obj)
    
    # Create a group for the controllers
    ctrlJntOffset = cmds.group(name=name.replace("_ctrl", "_ctrl_offset"), empty=True, world=False)
    
    # Match transforms the controller and offset to joint
    cmds.matchTransform(jntController, ctrlJntOffset, obj, position=True, rotation=True, 
                        scale=True, rotatePivot=True)
    
    # parant controller to offset
    cmds.parent(jntController, ctrlJntOffset)
    
     
    cmds.makeIdentity(jntController, apply=True, translate=True, rotate=True, scale=True)
    print(f"{name} --> {num}: DONE")

    # parent constraint the joint to the controllers
    cmds.parentConstraint(jntController, obj, weight=1, maintainOffset=False)
    
    for shape in cmds.listRelatives(jntController, allDescendents=True,):
        cmds.setAttr(shape + '.overrideEnabled', True)
        cmds.setAttr(shape + '.overrideRGBColors', False)
        cmds.setAttr(shape + '.overrideColor', colour_index)
        print(f"{shape} --> {num}: DONE")
    num += 1
print("ALL CONTRLLERS COLORS DONE")
# bind the joints to the skin
# cmds.skinCluster(objList, skin, name="l_rear_ribbon_skinCluster")
