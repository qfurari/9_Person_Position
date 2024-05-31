import cv2
from ultralytics import YOLO

import sys
import time
sys.path.append(".")

# Import RTM module
import RTC
import OpenRTM_aist

# This module's specification
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

class PersonPosition(OpenRTM_aist.DataFlowComponentBase):
    
    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

        self._d_Position = OpenRTM_aist.instantiateDataType(RTC.TimedShortSeq)
        self._PositionOut = OpenRTM_aist.OutPort("Position", self._d_Position)
    
    def onInitialize(self):
        self.addOutPort("Position", self._PositionOut)
        return RTC.RTC_OK

    def onActivated(self, ec_id):
        # カメラの初期化
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open camera.")
            return RTC.RTC_ERROR

        self.model = YOLO('yolov8s.pt')
        return RTC.RTC_OK
    
    def onDeactivated(self, ec_id):
        # カメラの解像度を取得
        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # 比率の計算
        aspect_ratio = actual_width / actual_height
        aspect_ratio_str = f"{actual_width}:{actual_height}"

        print(f"カメラの解像度: {actual_width}x{actual_height}")
        print(f"比率: {aspect_ratio_str} ({aspect_ratio:.2f}:1)")
        # カメラのリリース
        self.cap.release()
        cv2.destroyAllWindows()
        
        return RTC.RTC_OK
    
    def onExecute(self, ec_id):
        ret, frame = self.cap.read()
        if not ret:
            print("Failed to grab frame")
            return RTC.RTC_ERROR

        results = self.model.predict(frame, conf=0.5)
        img = results[0].plot()
        cv2.imshow('Webcam', img)

        xy = []
        for result in results:
            cls = result.boxes.cls
            position = result.boxes.xyxyn

            # 人のクラスID 0, 猫のクラスID 15, 犬のクラスID 16 を指定
            person_class_id = 0
            cat_class_id = 15
            dog_class_id = 16
            person_indices = (cls == person_class_id)
            cat_indices = (cls == cat_class_id)
            dog_indices = (cls == dog_class_id)

            persons = position[person_indices]
            cats = position[cat_indices]
            dogs = position[dog_indices]

            if len(persons) or len(cats) or len(dogs):
                for i in range(len(persons)):
                    person_x = int((((persons[i][0]) + (persons[i][2])) * 640) / 2)
                    person_y = int((((persons[i][1]) + (persons[i][3])) * 480) / 2)
                    print("-------------------------------------------------------")
                    print("現在の人の座標")
                    print("x座標{}、y座標{}".format(person_x, person_y))
                    print("-------------------------------------------------------")
                    xy.extend([person_x, person_y])
                    
                for i in range(len(cats)):
                    cats_x = int((((cats[i][0]) + (cats[i][2])) * 640) / 2)
                    cats_y = int((((cats[i][1]) + (cats[i][3])) * 480) / 2)
                    print("-------------------------------------------------------")
                    print("現在の猫の座標")
                    print("x座標{}、y座標{}".format(cats_x, cats_y))
                    print("-------------------------------------------------------")
                    xy.extend([cats_x, cats_y])

                for i in range(len(dogs)):
                    dogs_x = int((((dogs[i][0]) + (dogs[i][2])) * 640) / 2)
                    dogs_y = int((((dogs[i][1]) + (dogs[i][3])) * 480) / 2)
                    print("-------------------------------------------------------")
                    print("現在の犬の座標")
                    print("x座標{}、y座標{}".format(dogs_x, dogs_y))
                    print("-------------------------------------------------------")
                    xy.extend([dogs_x, dogs_y])

                for i in range(0, len(xy), 2):
                    print(f"すべてのx座標{xy[i]},すべてのy座標:{xy[i+1]}")
                    self._d_Position.data = [xy[i], xy[i + 1]]
                    self._PositionOut.write(self._d_Position)
            else:
                print("No persons, cats, or dogs detected")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            return RTC.RTC_ERROR

        return RTC.RTC_OK

def PersonPositionInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=personposition_spec)
    manager.registerFactory(profile,
                            PersonPosition,
                            OpenRTM_aist.Delete)

def MyModuleInit(manager):
    PersonPositionInit(manager)
    instance_name = [i for i in sys.argv if "--instance_name=" in i]
    if instance_name:
        args = instance_name[0].replace("--", "?")
    else:
        args = ""
    comp = manager.createComponent("PersonPosition" + args)

def main():
    argv = [i for i in sys.argv if not "--instance_name=" in i]
    mgr = OpenRTM_aist.Manager.init(argv)
    mgr.setModuleInitProc(MyModuleInit)
    mgr.activateManager()
    mgr.runManager()

if __name__ == "__main__":
    main()
