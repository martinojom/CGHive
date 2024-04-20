import maya.cmds as cmds

"""
Add Temperary Distance Node
"""

def getTempDistance(startPos, endPos):
    
    # create the distance node
    cmds.shadingNode ("distanceBetween", au=1, n=(startPos + "_distnode"))
    
    # connect attributes
    diss = cmds.connectAttr ((startPos + ".worldMatrix"), (startPos + "_distnode.inMatrix1"))
    cmds.connectAttr ((endPos + ".worldMatrix"), (startPos + "_distnode.inMatrix2"))
    cmds.connectAttr ((startPos + ".rotatePivotTranslate"), (startPos + "_distnode.point1"))
    cmds.connectAttr ((endPos + ".rotatePivotTranslate"), (startPos + "_distnode.point2"))

    return cmds.getAttr((startPos + "_distnode.distance"))


#-------------------------------------------------------------------------------------------------------------------------------------    
"""
Get the list of Nodes by providing the nodeType
"""

def listObjectByNodeType(nodeTypes, deleteObject=False):
    
    # List throght all the node Types
    if len(nodeTypes) < 1:
        cmds.error("provide a node type")
        
    # Check if the nodetype exists in all maya nodes  
    if not nodeTypes in cmds.allNodeTypes():
        cmds.error(f"{nodeTypes} is not a maya Node types, please provide a valid nodeType")
    
    # list nodes in the scene with the nodeType           
    nodes = cmds.ls(type=nodeTypes)
    if not nodes:
        cmds.warning("Nodes do not exist in the scene")
        return None 
    
    # Check if we are deleting the nodes 
    if deleteObject:
        cmds.delete(nodes)
        print(f"{nodes}: deleted!!!!")
        return nodes
    else:
        return nodes






objectNumber = 10
paramerterV = 0.9

#-------------------------------------------------------------------------------------------------------------------------------------    
# Add Temperary Distance Node

def getTempDistance(startPos, endPos):
    cmds.shadingNode ("distanceBetween", au=1, n=(startPos + "_distnode"))

    cmds.connectAttr ((startPos + ".worldMatrix"), (startPos + "_distnode.inMatrix1"))
    cmds.connectAttr ((endPos + ".worldMatrix"), (startPos + "_distnode.inMatrix2"))
    cmds.connectAttr ((startPos + ".rotatePivotTranslate"), (startPos + "_distnode.point1"))
    cmds.connectAttr ((endPos + ".rotatePivotTranslate"), (startPos + "_distnode.point2"))

    return cmds.getAttr((startPos + "_distnode.distance"))

    cmds.delete((startPos + "_distnode"))

  
#-------------------------------------------------------------------------------------------------------------------------------------
""" 
Build Icon
"""

def buildIcon(iconName, scale, *args):

    # jointOrient = cmds.optionMenu("jointOrientMenu", q=1, v=1) 
    
    # Get thet point position list
    pointsList = ([0.49949352081828996, -0.49965646741954789, 0.00011386882060004933],
            [-0.50050383972379531, -0.49965777484916379, 0.00025944578385106443],
            [-0.50050388864963413, 0.50034323886898902, -0.00011386824481751656],
            [0.49950191468729815, 0.50034278368308582, -0.0002594457838509534],
            [0.49949352081828996, -0.49965646741954789, 0.00011386882060004933]
            )
    
    # Create Curve 
    ctrlCurve = cmds.curve(degree=1, point=pointsList[0], name=iconName)
    
    # Iterate through the range of pootm 
    for i in range(len(pointsList)):
        if i < (len(pointsList)-1):
            cmds.curve(iconName, append=True, point=pointsList[i+1])    
    
    # set the attribute
    cmds.setAttr ((iconName + ".scale"), scale, scale, scale)
    
    # delete Histry
    cmds.makeIdentity (iconName, a=1, t=1, r=1, s=1) 

    return ctrlCurve
    

#-------------------------------------------------------------------------------------------------------------------------------------  
"""
< MARTIN > This is the part i started the ribbon tool from

"""
  
ribbonNurb = cmds.nurbsPlane(name="r_rear_ribbon", axis=(0,0,1), width=5, lengthRatio=12, 
                degree=3, patchesU=1, patchesV=9)
print(ribbonNurb)

# creating locators on each isospam on the plane
for objNum in range(objectNumber):
    # Create locators to work as follicles
    ribbonLoc = cmds.spaceLocator(name=f"r_rear_ribbon_loc_{objNum+1}")[0]
    
    # clear the selection
    # cmds.select(clear=True)
    
    # create joints on each locator
    # locJnt = cmds.joint(name=ribbonLoc.replace("_loc_", "_locjnt_"))
    # cmds.joint(locJnt, edit=True, orientJoint="yxz")???/
    
    # clear the selection
    # cmds.select(clear=True)
    
    # Create poing on surface info node 
    ribbonLocPOSI = cmds.createNode("pointOnSurfaceInfo", name=ribbonLoc.replace("_loc_","_loc_posi_"))
    # ribbonJntPOSI = cmds.createNode("pointOnSurfaceInfo", name=ribbonLoc.replace("_loc_","_jnt_posi_"))
    
    # Set the attribute for the U and V Parameters of the POSI
    cmds.setAttr(f"{ribbonLocPOSI}.parameterU", 0.5)
    cmds.setAttr(f"{ribbonLocPOSI}.parameterV", paramerterV)
    
    # cmds.setAttr(f"{ribbonJntPOSI}.parameterU", 0.5)
    # cmds.setAttr(f"{ribbonJntPOSI}.parameterV", paramerterV)
    
    # Connects connect the ribbon to POSI then from POSI to LOC attributes
    # cmds.connectAttr(f"{ribbonNurb[0]}.worldSpace[0]", f"{ribbonJntPOSI}.inputSurface", force=True)
    # cmds.connectAttr(f"{ribbonJntPOSI}.position", f"{locJnt}.translate", force=True)
    
    cmds.connectAttr(f"{ribbonNurb[0]}.worldSpace[0]", f"{ribbonLocPOSI}.inputSurface", force=True)
    cmds.connectAttr(f"{ribbonLocPOSI}.position", f"{ribbonLoc}.translate", force=True)
    
    
    # lets delete the ribbon joint POSI 
    # cmds.delete(ribbonJntPOSI)
    
    
    # reduce the Value of the parameterV to snap the locator to isospam
    paramerterV = paramerterV - 0.1  
    
    # print(f"{ribbonPOSI}: {ribbonLoc}")