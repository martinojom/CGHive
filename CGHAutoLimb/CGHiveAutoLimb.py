#------------------------------------------------------------------------------------------------
#
# CGHive Auto Limb Tool v1 This is the beginning of my maya rigging series
#
#------------------------------------------------------------------------------------------------

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
            cmds.makeIdentity(newJointName, apply=True, translate=True, rotate=True, scale=True)
        
        cmds.select(clear=True)
        
    #-----------------------------------------------------------------------
    # Constraint the main joints to the ik fk joint so that we can blend between them
    for i in range(limbJoints):
        cmds.parentConstraint((jointHierchy[i] + "_FK_ctrl"), (jointHierchy[i] + "_fk"), jointHierchy[i],
                                maintainOffset=True, weight=True)
    
    #-----------------------------------------------------------------------
    # setup FK
    
    #connect the  main 
    
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
        cmds.






    # ALL CREATED AND DONE
    print("PERFECT >MARTIN< : ALL DONE")
    
    
     
    
    
    
    
    
    
    
    
    
    
    
    
    

 