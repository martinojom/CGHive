
'''
------------------------------------------------------------------------------------------------

 CGHive Auto Limb Tool v1 This is the beginning of my maya rigging series
 Auther Name = Martin Ojom
 Company Name = CGHive

        NOTE:
            This AutoLimb tool is a product of CGHive that was written by Martin Ojom


------------------------------------------------------------------------------------------------
'''
import maya.cmds as cmds

def autoLimbTool(*args):
    # setup the variable which could come from the UI

    # Is this the front leg?:
    whichLeg = cmds.optionMenu("legMenu", query=True, value=True)

    # Is this the front or rear leg?
    if whichLeg == "Front":
        isRearLeg = 0
    else:
        isRearLeg = 1

    # check the ckeckboxes
    rollCheck = cmds.checkBox("rollCheck", query=True, value=True)
    stretchCheck = cmds.checkBox("stretchCheck", query=True, value=True)
    
    # How many Joint are we working with?
    limbJoints = 4
    
    # Use this information to start generating the name we need
    if isRearLeg:
        limbType = 'rear' 
        print('working on the REAR leg')
        
    else:
        limbType = 'front'
        print('working on the FRONT leg')
        
    # check the selection is valid
    selectionCheck = cmds.ls(selection=True, type='joint')
    
    # Error check to make sure the joint is selected
    if not selectionCheck:
        cmds.error('Please select the root joint')
    else:
        jointRoot = cmds.ls(selection=True, type='joint')[0]
        
    # Now we have a selected joint we can check for the prefix to see whick side it is
    whichSide = jointRoot[0:2]
    
    # Make sure the prefix is usable
    if not 'l_' in whichSide:
        if not 'r_' in whichSide:    
            cmds.error('Please use joints with a usable prifix either l_ or r_')
    
    # Now build the names we need
    limbName = whichSide + 'leg_' + limbType
    
    mainControl = limbName + '_ctrl'
    pawControlName = limbName + '_IK_ctrl'
    kneeControlName = limbName + "_tibia_ctrl"
    hockControlName = limbName + "_hock_ctrl"
    rootControlName = limbName + "_root_ctrl"
    
    #-----------------------------------------------------------------------
    # Build the list of joints we are working with, using the root as a start point
    
    # Find its children
    jointHierchy = cmds.listRelatives(jointRoot, allDescendents=True, type="joint")
    
    # Add the selected joint infont of the list
    jointHierchy.append(jointRoot)
    
    # Reverse the list so we can work in order
    jointHierchy.reverse()
    
    # clear selection
    cmds.select(clear=True)
    
    #--------------------------------------------------------------------
    # Dulicate the main joint chain and rename eaach joint
    
    # First define what joint chains we need
    newJointList = ["_ik", "_fk", "_stretch"]
    
    # Add the extra driver joints if this is the rear leg
    if isRearLeg:
        newJointList.append("_driver")
        
    # Build the joints 
    for newJoint in newJointList:
        for i in range(limbJoints):
            newJointName = jointHierchy[i] + newJoint
            
            cmds.joint(name=newJointName)
            cmds.matchTransform(newJointName, jointHierchy[i])
            cmds.makeIdentity(newJointName, apply=True, translate=False, rotate=True, scale=False)
        
        cmds.select(clear=True)
        
    #-----------------------------------------------------------------------
    # Constraint the main joints to the ik fk joint so that we can blend between them
    for i in range(limbJoints):
        cmds.parentConstraint((jointHierchy[i] + "_ik"), (jointHierchy[i] + "_fk"), jointHierchy[i],
                                maintainOffset=True, weight=True)
    
    #----------------------------------------------------------------------------------------------------------------
    # SETUP FK
    
    #connect the FK controls to the joints
    for i in range(limbJoints):
        cmds.parentConstraint(jointHierchy[i] + "_FK_ctrl", jointHierchy[i] + "_fk", weight=True, maintainOffset=True)
    
    #----------------------------------------------------------------------------------------------------------------
    # SETUP IK

    # If its the rear leg, create the ik handle from  the femus to the metacarpus
    if isRearLeg:
        cmds.ikHandle(name=limbName + "_driver_ikHandle", solver="ikRPsolver", startJoint=jointHierchy[0] + "_driver", 
                        endEffector=jointHierchy[3] + "_driver")   
    
    # Next, create the main ik handle from the femur to the metatarsus
    cmds.ikHandle(name=limbName + "_knee_ikHandle", solver="ikRPsolver", startJoint=jointHierchy[0] + "_ik", 
                        endEffector=jointHierchy[2] + "_ik")   
    
    # Finally, create the main ik handle from the metatarsus to the metacarpus
    cmds.ikHandle(name=limbName + "_hock_ikHandle", solver="ikSCsolver", startJoint=jointHierchy[2] + "_ik", 
                        endEffector=jointHierchy[3] + "_ik")   
    
    # Create the knee control offset group
    cmds.group(limbName + "_knee_ikHandle", name=limbName + "_knee_control")
    cmds.group(limbName + "_knee_control", name=limbName + "_knee_control_offset")

    # Find the ankle pivot
    anklePivot = cmds.xform(jointHierchy[3], query=True, worldSpace=True, pivots=True)

    # set the group pivot to match the ankle position
    cmds.xform(((limbName + "_knee_control"), (limbName + "_knee_control_offset")), worldSpace=True, pivots=(anklePivot[0], anklePivot[1], anklePivot[2]))

    # Parent the ik handle and group to the paw control
    cmds.parent(limbName + "_hock_ikHandle", pawControlName) 

    # If its the rear leg, adjust the hierachy to the driver leg control the ik handle
    if isRearLeg:
        cmds.parent(limbName + "_knee_control_offset", jointHierchy[2] + "_driver")
        cmds.parent(limbName + "_hock_ikHandle", jointHierchy[3] + "_driver")

        cmds.parent(limbName + "_driver_ikHandle", pawControlName)
    else:
        cmds.parent(limbName + "_knee_control_offset", "root_ctrl")
        cmds.pointConstraint(pawControlName, limbName + "_knee_control_offset", weight=True)

    #------------------------------------------------------------------------------------
    # Make the paw control driver the ankle joint to maintain orientation
    cmds.orientConstraint(pawControlName, jointHierchy[3] + "_ik", weight=True) 

    # Add the pole vector to the driver IK handle if ist the rear leg, if its the front add it to the  knee ik handle
    if isRearLeg:
        cmds.poleVectorConstraint(kneeControlName, limbName + "_driver_ikHandle", weight=True)
    else:
        cmds.poleVectorConstraint(kneeControlName, (limbName + "_knee_ikHandle"), weight=True)

    # #---------------------------------------------------------------------------------
    # Add hock control

    # Check if its the front or rear leg
    if isRearLeg:
        muitiValue = 2.5
    else:
        muitiValue = 5

    cmds.shadingNode('multiplyDivide', asUtility=True, name=limbName + "_hock_multi")

    cmds.connectAttr(hockControlName + ".translate", limbName + "_hock_multi.input1", force=True)

    cmds.connectAttr(limbName + "_hock_multi.outputZ", limbName + "_knee_control.rotateX", force=True)
    cmds.connectAttr(limbName + "_hock_multi.outputX", limbName + "_knee_control.rotateZ", force=True)

    cmds.setAttr(limbName + "_hock_multi.input2X", muitiValue*-1)
    cmds.setAttr(limbName + "_hock_multi.input2Z", muitiValue)

    # #---------------------------------------------------------------------------------
    # Add the IK and FK blending

    for i in range(limbJoints):
        getConstrait = cmds.listConnections(jointHierchy[i], type='parentConstraint')[0]
        getWeights = cmds.parentConstraint(getConstrait, query=True, weightAliasList=True)

        cmds.connectAttr(mainControl + ".FK_IK_Switch", getConstrait + "." + getWeights[0], force=True)
        cmds.connectAttr(limbName + "_fkik_reverse.outputX", getConstrait + "." + getWeights[1], force=True)

    #---------------------------------------------------------------------------------
    # Update the hierachy

    # Add a group for the limb
    cmds.group(empty=1, name=limbName + "_grp")

    # Move if to the root position and freeze the transforms
    cmds.matchTransform(limbName + "_grp", jointRoot)
    cmds.makeIdentity(limbName + "_grp", apply=True, translate=True, rotate=True, scale=False)
     

    # Parent the joint to the new group
    cmds.parent(jointRoot + "_ik", jointRoot + "_fk", jointRoot + "_stretch", limbName + "_grp")

    if isRearLeg:
        cmds.parent(jointRoot + "_driver", limbName + "_grp")

    # Make the new group follow the root control
    cmds.parentConstraint(rootControlName, limbName + "_grp", weight=True, maintainOffset=True)

    # Move the group to the rig system folder
    cmds.parent(limbName + "_grp", "rig_systems")

    # Clear the selection
    cmds.select(clear=True)

    #---------------------------------------------------------------------------------
    # Make Stretchy
    #---------------------------------------------------------------------------------

    if stretchCheck:
        # create the locator which dictates the end position
        cmds.spaceLocator(name=limbName + "_stretchEndPos_loc")

        # Move it to the end joint
        cmds.matchTransform(limbName + "_stretchEndPos_loc", jointHierchy[3])
        cmds.parent(limbName + "_stretchEndPos_loc", pawControlName)

        # start to build the distance nodes
        # First, we will need to to add all the distance nodes together, so we need a plusMinusAverage nod
        cmds.shadingNode("plusMinusAverage", asUtility=True, name=limbName + "_length")

        # Build the distance node for each section
        for i in range(limbJoints):

            #ignore the last joint or it will try to use the toes
            if i is not limbJoints -1:
                cmds.shadingNode("distanceBetween", asUtility=True, name=jointHierchy[i] + "_distnode")

                cmds.connectAttr(jointHierchy[i] + "_stretch.worldMatrix", jointHierchy[i] + "_distnode.inMatrix1", force=True)
                cmds.connectAttr(jointHierchy[i+1] + "_stretch.worldMatrix", jointHierchy[i] + "_distnode.inMatrix2", force=True)

                cmds.connectAttr(jointHierchy[i+1] + "_stretch.rotatePivotTranslate", jointHierchy[i] + "_distnode.point1", force=True)
                cmds.connectAttr(jointHierchy[i+1] + "_stretch.rotatePivotTranslate", jointHierchy[i] + "_distnode.point2", force=True)

                cmds.connectAttr(jointHierchy[i] + "_distnode.distance", limbName + "_length.input1D[" + str(i) + "]", force=True)

        # Now get the distance from the root to the stretch end locator - we  use this to check the leg is stretching
        cmds.shadingNode("distanceBetween", asUtility=True, name=limbName + "_stretch_distnode") 

        cmds.connectAttr(jointHierchy[0] + "_stretch.worldMatrix", limbName + "_stretch_distnode.inMatrix1", force=True)
        cmds.connectAttr(limbName + "_stretchEndPos_loc.worldMatrix", limbName + "_stretch_distnode.inMatrix2", force=True)

        cmds.connectAttr(jointHierchy[0] + "_stretch.rotatePivotTranslate", limbName + "_stretch_distnode.point1", force=True)
        cmds.connectAttr(limbName + "_stretchEndPos_loc.rotatePivotTranslate", limbName + "_stretch_distnode.point2", force=True)

        # Create nodes to check for stretching, and to control how the stretch works
        
        # Scale factor compare the length of the leg with the stretch locator, so we can see when the actuslly stretching
        cmds.shadingNode("multiplyDivide", asUtility=True, name=limbName + "_scaleFactor")
        
        # We use the condition node to pass this onto the joints, so the leg only stretches the way we want it to
        cmds.shadingNode("condition", asUtility=True, name=limbName + "_condition")

        # Ajust the node settings
        cmds.setAttr(limbName + "_scaleFactor.operation", 2)

        cmds.setAttr(limbName + "_condition.operation", 2)
        cmds.setAttr(limbName + "_condition.secondTerm", 1)

        # Connect the stretch to the scale the facto multiply divide node
        cmds.connectAttr(limbName + "_stretch_distnode.distance", limbName + "_scaleFactor.input1X", force=True)

        # Connect the full leg distance to the scale factor multiply divide node
        cmds.connectAttr(limbName + "_length.output1D", limbName + "_scaleFactor.input2X", force=True)

        # Next, Connect the stretch Factor node to the first term in the condition node 
        cmds.connectAttr(limbName + "_scaleFactor.outputX", limbName + "_condition.firstTerm", force=True)
        
        # Also connect the coloe if true attribute, so we can use this as the stretch value  
        cmds.connectAttr(limbName + "_scaleFactor.outputX", limbName + "_condition.colorIfTrueR", force=True)

        # Also connect the coloe if true attribute, so we can use this as the stretch value  
        for i in range(limbJoints):
            cmds.connectAttr(limbName + "_condition.outColorR", jointHierchy[i] + "_ik.scaleX", force=True)

            # Also effect the driver skeleton, if this is the rear leg
            if isRearLeg:
                cmds.connectAttr(jointHierchy[i] + "_ik.scaleX", jointHierchy[i] + "_driver.scaleX", force=True)

        # Add the ability to turn the stretching off 
        cmds.shadingNode("blendColors", asUtility=True, name=limbName + "_blendColors")
        cmds.setAttr(limbName + "_blendColors.color2", 1,0,0, type="double3")

        cmds.connectAttr(limbName + "_scaleFactor.outputX", limbName + "_blendColors.color1R", force=True)
        cmds.connectAttr(limbName + "_blendColors.outputR", limbName + "_condition.colorIfTrueR", force=True)

        # Connect to the par control attribute
        cmds.connectAttr(pawControlName + ".Stretchiness", limbName + "_blendColors.blender", force=True)

        # Wire up the attribute so we can cotrol how the stretch works
        cmds.setAttr(pawControlName + ".StretchType", 0)
        cmds.setAttr(limbName + "_condition.operation", 1) # Not Equals

        cmds.setDrivenKeyframe(limbName + "_condition.operation", currentDriver=pawControlName + ".StretchType")

        cmds.setAttr(pawControlName + ".StretchType", 1)
        cmds.setAttr(limbName + "_condition.operation", 3) # Greater Than

        cmds.setDrivenKeyframe(limbName + "_condition.operation", currentDriver=pawControlName + ".StretchType")
        
        cmds.setAttr(pawControlName + ".StretchType", 2)
        cmds.setAttr(limbName + "_condition.operation", 5) # Less or Equal

        cmds.setDrivenKeyframe(limbName + "_condition.operation", currentDriver=pawControlName + ".StretchType")

        cmds.setAttr(pawControlName + ".StretchType", 1)

        # Clear the selection
        cmds.select(clear=True)

        #---------------------------------------------------------------------------------
        # Volume Preservation 
        #---------------------------------------------------------------------------------

        #Create the main multiply divide node whick will calculate the volume
        cmds.shadingNode("multiplyDivide", asUtility=True, name=limbName + "_volume")

        # set the operation to power:
        cmds.setAttr(limbName + "_volume.operation", 3)

        # connect the main stretch value to the valume node:
        cmds.connectAttr(limbName + "_blendColors.outputR", limbName + "_volume.input1X", force=True)

        # connect the condition node so we can control scaling:
        cmds.connectAttr(limbName + "_volume.outputX", limbName + "_condition.colorIfTrueG", force=True)

        # Connect to the fibula joint:
        cmds.connectAttr(limbName + "_condition.outColorG", jointHierchy[1] + ".scaleY", force=True)
        cmds.connectAttr(limbName + "_condition.outColorG", jointHierchy[1] + ".scaleZ", force=True)

        # Connect to the metatarsus joint:
        cmds.connectAttr(limbName + "_condition.outColorG", jointHierchy[2] + ".scaleY", force=True)
        cmds.connectAttr(limbName + "_condition.outColorG", jointHierchy[2] + ".scaleZ", force=True)

        # Connect the volume attribute:
        cmds.connectAttr(mainControl + ".Volume_Offset", limbName + "_volume.input2X", force=True)

    #---------------------------------------------------------------------------------
    # Add Roll Joints & Systems
    #---------------------------------------------------------------------------------

    if rollCheck:
        # Check if we are working on the right side and if so we can move to the correct side
        if whichSide == "l_":
            flipSide = 1
        else: 
            flipSide = -1

        # Create the main roll and follow joints
        rollJointList = [jointHierchy[0], jointHierchy[3], jointHierchy[0], jointHierchy[0]]

        for i in range(len(rollJointList)):

            # set the joint names
            if i > 2:
                rollJointName = rollJointList[i] + "_follow_tip"
            elif i > 1:
                rollJointName = rollJointList[i] + "_follow"
            else:
                rollJointName = rollJointList[i] + "_roll"
            
            cmds.joint(name=rollJointName, radius=1)
            cmds.matchTransform(rollJointName, rollJointList[i])
            cmds.makeIdentity(rollJointName, apply=True, translate=False, rotate=True, scale=False)


            if i < 2:
                cmds.parent(rollJointName, rollJointList[i])
            elif i > 2: 
                cmds.parent(rollJointName, rollJointList[2] + "_follow")

            cmds.select(clear=True)

            # show the local rotation axes to help visualie the rotaion
            # cmds.toggle(rollJointName, localAxis=True)

        # let work on the femur first and adjust the following joints.
        cmds.pointConstraint(jointHierchy[0], jointHierchy[1], rollJointList[2] + "_follow_tip", 
                            weight=True, maintainOffset=False, name="TemperaryPointConstraint")
        cmds.delete("TemperaryPointConstraint")

        # Now move them out
        cmds.move(0,0,-5*flipSide, rollJointList[2] + "_follow", relative=True, objectSpace=True, 
                worldSpaceDistance=True)

        # Create the aim locator whick the femur roll joint will always follow
        cmds.spaceLocator(name=rollJointList[0] + "_roll_aim")

        # Move it to the root joint and parent it to the following joint so it moves with it
        cmds.matchTransform(rollJointList[0] + "_roll_aim", rollJointList[2] + "_follow")
        cmds.parent(rollJointList[0] + "_roll_aim", rollJointList[2] + "_follow")

        # Move the locator out too
        cmds.move(0,0,-5*flipSide, rollJointList[0] + "_roll_aim", relative=True, objectSpace=True, 
                worldSpaceDistance=True)
        
        # Make the roll joint aim at the fibula joint, but also keep lookin at the aim locator for reference
        cmds.aimConstraint(rollJointList[1], rollJointList[0] + "_roll", weight=True, aimVector=(1,0,0), 
                        upVector=(0,0,1), worldUpType="object", worldUpObject=rollJointList[0] + "_roll_aim", 
                        maintainOffset=True)
        
        # Add an ik handle so the follow joints, follow the leg
        cmds.ikHandle(name=limbName + "_follow_ikHandle", solver="ikRPsolver", startJoint=rollJointList[2] + "_follow", 
                            endEffector=rollJointList[2] + "_follow_tip")  
        
        # Now move it to the fibula and parent it too
        cmds.parent(limbName + "_follow_ikHandle", rollJointList[1])
        cmds.matchTransform(limbName + "_follow_ikHandle", rollJointList[1])

        # Also reset the pole vector to stop the limb twisting
        cmds.setAttr(limbName + "_follow_ikHandle.poleVectorX", 0)
        cmds.setAttr(limbName + "_follow_ikHandle.poleVectorY", 0)
        cmds.setAttr(limbName + "_follow_ikHandle.poleVectorZ", 0)

        #-----------------------------------------------------------------------------------------------------------
        # Lower leg systems

        # Create the aim locator thick the femur roll joint will always follow
        cmds.spaceLocator(name=rollJointList[1] + "_roll_aim")

        # Move it the ankle joint and parent to the ankle joint too
        cmds.matchTransform(rollJointList[1] + "_roll_aim", rollJointList[1] + "_roll")
        cmds.parent(rollJointList[1] + "_roll_aim", jointHierchy[3])

        # Also move it out to the side
        cmds.move(5*flipSide, 0, 0, rollJointList[1] + "_roll_aim", relative=True, objectSpace=True, worldSpaceDistance=True)

        # Make the ankle joint aim at the febula joint, but also keep looking at the locotor for refference
        cmds.aimConstraint(rollJointList[2], rollJointList[1] + "_roll", weight=True, aimVector=(0,1,0), 
                        upVector=(1,0,0), worldUpType="object", worldUpObject=rollJointList[1] + "_roll_aim", 
                        maintainOffset=True)
        
        # Update the hierachy, parenting the following joints to the main group
        cmds.parent(rollJointList[0] + "_follow", limbName + "_grp")
    
        cmds.select(clear=True)

        print("ROLL JOINT CREATED")

    # -----> this sphere is just for testing to notice the undo times<--------
    cmds.polySphere(radius =5)

    # ALL CREATED AND DONE:
    print("PERFECT >MARTIN< : ALL DONE") 
    
    
def autoLimbToolUI():
    # check if the window exists if it does deleteUI:
    if cmds.window("autoLimToolUI", exists=True): cmds.deleteUI("autoLimToolUI")

    # Create a window:
    window = cmds.window("autoLimToolUI", title="CGHive Limb Tool v1.0", width=200, height=200, maximizeButton=False, 
                         minimizeButton=False)
    
    # Create the main layout:
    # mainMainLayout = cmds.columnLayout(columnAttach=('both', 5), columnAlign="right", adjustableColumn=True, parent=window)
    # cmds.separator(width=5, parent=mainMainLayout, annotation="Separating the UI elements")
    mainLayout = cmds.formLayout(numberOfDivisions=100, parent=window)

    # Leg menu and menu items:
    legMenu = cmds.optionMenu("legMenu", label="Which Leg?", height=20, annotation="which side are working on?")
    cmds.menuItem(label="Front", parent=legMenu)
    cmds.menuItem(label="Rear", parent=legMenu)

    # Checkboxes
    rollCheck = cmds.checkBox("rollCheck", label="Roll Joint", height=20, annotation="Add Roll Joints?", 
                              value=0)
    stretchCheck = cmds.checkBox("stretchCheck", label="Stretchy", height=20, annotation="Stretchy limb?", 
                              value=0)

    # Add a separetor for some spacing:
    separator01 = cmds.separator(width=5, parent=mainLayout, annotation="Separating the UI elements")
    separator02 = cmds.separator(width=5, parent=mainLayout, annotation="Separating the UI elements")
     
    # Buttons:
    button = cmds.button(label="[GO]", command=autoLimbTool, parent=mainLayout)

    # Adjust the layout:
    cmds.formLayout(mainLayout, edit=True, 
                    attachForm=[(legMenu, "top", 5), (legMenu, "left", 5), (legMenu, "right", 5),
                                 (separator01, "left", 5), (separator01, "right", 5),
                                 (button, "top", 5), (button, "left", 5), (button, "right", 5)
                                ],
                    attachControl=[(separator01, "top", 5, legMenu),
                                     (rollCheck, "top", 5, separator01),
                                     (stretchCheck, "top", 5, separator01),

                                     (separator02, "top", 5, rollCheck),
                                     (button, "top", 5, separator02)

                                ],
                    attachPosition=[(rollCheck, "left", 5, 15),
                                    (stretchCheck, "right", 5, 85)
                                    ]
                    )


    # Show the window
    cmds.showWindow(window)



     
    
    
    
    
    
    
    
    
    
    
    
    
    

 