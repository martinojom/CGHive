
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

def autoLimbTool():
    # setup the variable which could come from the UI
    
    # Is this the front or rear leg?
    isRearLeg = 1
    
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
    cmds.parent(limbName + "_knee_control_offset", limbName + "_hock_ikHandle", pawControlName) 

    # If its the rear leg, adjust the hierachy to the driver leg control the ik handle
    if isRearLeg:
        cmds.parent(limbName + "_knee_control_offset", jointHierchy[2] + "_driver")
        cmds.parent(limbName + "_hock_ikHandle", jointHierchy[3] + "_driver")

        cmds.parent(limbName + "_driver_ikHandle", pawControlName)

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

    # -----> this sphere is just for testing to notice the undo times<--------
    cmds.polySphere(radius =5)

    # Clear the selection
    cmds.select(clear=True)






    # ALL CREATED AND DONE
    print("PERFECT >MARTIN< : ALL DONE") 
    
    
     
    
    
    
    
    
    
    
    
    
    
    
    
    

 