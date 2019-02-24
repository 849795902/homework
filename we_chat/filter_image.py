import cv2 as cv
import os

file_path = "F:/shentong_images"
new_file_path = "F:/shentong_images/target"

file_list = os.listdir(file_path)
for image in file_list:
    dst = cv.imread(os.path.join(file_path, image), 1)
    try:
        cv.imshow("dst", dst)
    except Exception as e:
        print(e)
        continue
    print("1:保留，其他：舍去")
    flag=cv.waitKey(0)
    if flag == 49:
        cv.imwrite(os.path.join(new_file_path, image), dst)
    cv.destroyAllWindows()
