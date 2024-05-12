#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

# <rtc-template block="description">
"""
 @file PersonPosition.py
 @brief ModuleDescription
 @date $Date$


"""
# </rtc-template>
import cv2
from ultralytics import YOLO

import sys
import time
sys.path.append(".")

# Import RTM module
import RTC
import OpenRTM_aist


# Import Service implementation class
# <rtc-template block="service_impl">

# </rtc-template>

# Import Service stub modules
# <rtc-template block="consumer_import">
# </rtc-template>


# This module's spesification
# <rtc-template block="module_spec">
personposition_spec = ["implementation_id", "PersonPosition", 
         "type_name",         "PersonPosition", 
         "description",       "ModuleDescription", 
         "version",           "1.0.0", 
         "vendor",            "arai", 
         "category",          "test", 
         "activity_type",     "STATIC", 
         "max_instance",      "1", 
         "language",          "Python", 
         "lang_type",         "SCRIPT",
         ""]
# </rtc-template>

# <rtc-template block="component_description">
##
# @class PersonPosition
# @brief ModuleDescription
# 
# 
# </rtc-template>
class PersonPosition(OpenRTM_aist.DataFlowComponentBase):
	
    ##
    # @brief constructor
    # @param manager Maneger Object
    # 
    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

        self._d_Position = OpenRTM_aist.instantiateDataType(RTC.TimedShortSeq)
        """
        """
        self._PositionOut = OpenRTM_aist.OutPort("Position", self._d_Position)


		


        # initialize of configuration-data.
        # <rtc-template block="init_conf_param">
		
        # </rtc-template>


		 
    ##
    #
    # The initialize action (on CREATED->ALIVE transition)
    # 
    # @return RTC::ReturnCode_t
    # 
    #
    def onInitialize(self):
        # Bind variables and configuration variable
		
        # Set InPort buffers
		
        # Set OutPort buffers
        self.addOutPort("Position",self._PositionOut)
		
        # Set service provider to Ports
		
        # Set service consumers to Ports
		
        # Set CORBA Service Ports
		
        return RTC.RTC_OK
	
    ###
    ## 
    ## The finalize action (on ALIVE->END transition)
    ## 
    ## @return RTC::ReturnCode_t
    #
    ## 
    #def onFinalize(self):
    #

    #    return RTC.RTC_OK
	
    ###
    ##
    ## The startup action when ExecutionContext startup
    ## 
    ## @param ec_id target ExecutionContext Id
    ##
    ## @return RTC::ReturnCode_t
    ##
    ##
    #def onStartup(self, ec_id):
    #
    #    return RTC.RTC_OK
	
    ###
    ##
    ## The shutdown action when ExecutionContext stop
    ##
    ## @param ec_id target ExecutionContext Id
    ##
    ## @return RTC::ReturnCode_t
    ##
    ##
    #def onShutdown(self, ec_id):
    #
    #    return RTC.RTC_OK
	
    ##
    #
    # The activated action (Active state entry action)
    #
    # @param ec_id target ExecutionContext Id
    # 
    # @return RTC::ReturnCode_t
    #
    #
    def onActivated(self, ec_id):
    
        return RTC.RTC_OK
	
    ##
    #
    # The deactivated action (Active state exit action)
    #
    # @param ec_id target ExecutionContext Id
    #
    # @return RTC::ReturnCode_t
    #
    #
    def onDeactivated(self, ec_id):
    
        return RTC.RTC_OK
	
    ##
    #
    # The execution action that is invoked periodically
    #
    # @param ec_id target ExecutionContext Id
    #
    # @return RTC::ReturnCode_t
    #
    #
    def onExecute(self, ec_id):
        # ウェブカメラをキャプチャするための VideoCapture オブジェクトを作成します
        cap = cv2.VideoCapture(0)
        model = YOLO('yolov8n.pt')
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break
            # ウェブカメラからフレームを読み込みます
            results=model.predict(frame,conf=0.5)
            img=results[0].plot()
            cv2.imshow('Webcam', img)
            for result in results:
                #すべての抽出内容
                cls=result.boxes.cls
                #座標x1y2x1y2
                position=result.boxes.xyxyn#変更可
                #print(cls)
                #人の検出を抽出(cls=０)
                zero_indices = (cls == 0)
                #人だけの位置を取得
                persons=position[zero_indices]
                #画面状に人がいるかの確認
                if  len(persons):
                    xy=[]
                    
                    for i in range (len(persons)):
                        position_x = (float(persons[i][0]) + float(persons[i][2])) / 2.0
                        position_y = (float(persons[i][1]) + float(persons[i][3])) / 2.0
                        print("-------------------------------------------------------")
                        print("現在の人の座標")
                        print("x座標{}、y座標{}".format(position_x,position_y))
                        print(" ")
                        print("-------------------------------------------------------")
                        xy.append(position_x)#x座標の配列に追加
                        xy.append(position_y)#y座標の配列に追加
                    ###################################
                    #for i in range(len(xy)):
                    #    if i%2==0:
                    #        print("x座標",xy[i])
                    #    else:
                    #        print("y座標",xy[i])
                    ###################################
                    #list->TimedShortSeqに型変換
                    OutPosition = RTC.TimedShortSeq(RTC.Time(0, 0), [])
                    print(type(xy))
                    print(type(OutPosition))
                    #出力
                    OutPosition=xy
                    print(OutPosition[0],OutPosition[1])
                    self._PositionOut.write(OutPosition)
                    
                else:
                    print("No persons detected")
            
            # フレームを表示します
            # 'q' キーを押すとループを終了します
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # キャプチャを解放して、ウィンドウをすべて閉じます
        cap.release()
        cv2.destroyAllWindows()
        return RTC.RTC_OK
	
    ###
    ##
    ## The aborting action when main logic error occurred.
    ##
    ## @param ec_id target ExecutionContext Id
    ##
    ## @return RTC::ReturnCode_t
    ##
    ##
    #def onAborting(self, ec_id):
    #
    #    return RTC.RTC_OK
	
    ###
    ##
    ## The error action in ERROR state
    ##
    ## @param ec_id target ExecutionContext Id
    ##
    ## @return RTC::ReturnCode_t
    ##
    ##
    #def onError(self, ec_id):
    #
    #    return RTC.RTC_OK
	
    ###
    ##
    ## The reset action that is invoked resetting
    ##
    ## @param ec_id target ExecutionContext Id
    ##
    ## @return RTC::ReturnCode_t
    ##
    ##
    #def onReset(self, ec_id):
    #
    #    return RTC.RTC_OK
	
    ###
    ##
    ## The state update action that is invoked after onExecute() action
    ##
    ## @param ec_id target ExecutionContext Id
    ##
    ## @return RTC::ReturnCode_t
    ##

    ##
    #def onStateUpdate(self, ec_id):
    #
    #    return RTC.RTC_OK
	
    ###
    ##
    ## The action that is invoked when execution context's rate is changed
    ##
    ## @param ec_id target ExecutionContext Id
    ##
    ## @return RTC::ReturnCode_t
    ##
    ##
    #def onRateChanged(self, ec_id):
    #
    #    return RTC.RTC_OK
	



def PersonPositionInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=personposition_spec)
    manager.registerFactory(profile,
                            PersonPosition,
                            OpenRTM_aist.Delete)

def MyModuleInit(manager):
    PersonPositionInit(manager)

    # create instance_name option for createComponent()
    instance_name = [i for i in sys.argv if "--instance_name=" in i]
    if instance_name:
        args = instance_name[0].replace("--", "?")
    else:
        args = ""
  
    # Create a component
    comp = manager.createComponent("PersonPosition" + args)

def main():
    # remove --instance_name= option
    argv = [i for i in sys.argv if not "--instance_name=" in i]
    # Initialize manager
    mgr = OpenRTM_aist.Manager.init(sys.argv)
    mgr.setModuleInitProc(MyModuleInit)
    mgr.activateManager()
    mgr.runManager()

if __name__ == "__main__":
    main()

