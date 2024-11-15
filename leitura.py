import cv2
import numpy as np
import utlis

def adjust_brightness_contrast(img_gray):
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(img_gray)
def apply_gamma_correction(img, gamma=1.2):
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(img, table)

def start_reading(self):
    path = self
    width_img = 700
    height_img = 700
    questions = 25
    choices = 5
    ans = [0, 1, 1, 1, 0, 0, 2, 1, 3, 3, 2, 2, 1, 1, 2, 2, 1, 3, 4, 2, 1, 2, 1, 1, 2]
    #######################

    img = cv2.imread(path)

    # PREPROCESSAMENTO
    img = cv2.resize(img, (width_img, height_img))
    img = apply_gamma_correction(img)
    img_contours = img.copy()
    # img_final = img.copy()
    img_biggest_contours = img.copy()
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_gray = adjust_brightness_contrast(img_gray)

    img_blur = cv2.GaussianBlur(img_gray, (7, 7), 1)
    #cv2.imshow("img_blur", img_gray)
    img_canny = cv2.Canny(img_blur, 10, 50)
    #cv2.imshow("GaussianBlur, Canny, CLAHE, Gamma Correction", img_gray)
    # CONTORNOS
    contours, hierarchy = cv2.findContours(img_canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(img_contours, contours, -1, (0, 255, 0), 10)

    # RETANGULOS
    rect_contours = utlis.rect_contour(contours)
    biggest_contour = utlis.get_corner_points(rect_contours[0])
    grade_points = utlis.get_corner_points(rect_contours[1])
    # print(biggest_contour)

    if biggest_contour.size != 0 and grade_points.size != 0:
        cv2.drawContours(img_biggest_contours, biggest_contour, -1, (255, 0, 0), 20)  # azul
        cv2.drawContours(img_biggest_contours, grade_points, -1, (0, 255, 0), 20)  # verde

        #cv2.imshow("maiores contornos", img_biggest_contours)

        biggest_contour = utlis.reorder(biggest_contour)
        grade_points = utlis.reorder(grade_points)

        pt1 = np.float32(biggest_contour)
        pt2 = np.float32([[0, 0], [width_img, 0], [0, height_img], [width_img, height_img]])
        matrix = cv2.getPerspectiveTransform(pt1, pt2)
        img_warp_colored = cv2.warpPerspective(img, matrix, (width_img, height_img))

        pt_g1 = np.float32(grade_points)
        pt_g2 = np.float32([[0, 0], [325, 0], [0, 150], [325, 150]])
        matrix_g = cv2.getPerspectiveTransform(pt_g1, pt_g2)
        img_grade_display = cv2.warpPerspective(img, matrix_g, (325, 150))
        #cv2.imshow("ok", img_grade_display)

    # Aonde ta marcado
    img_warp_gray = cv2.cvtColor(img_warp_colored, cv2.COLOR_BGR2GRAY)
    img_thresh = cv2.adaptiveThreshold(img_warp_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV, 11, 2)
    #cv2.imshow("im_thresh and img_warp_gray", img_thresh)
    boxes = utlis.split_boxes(img_thresh)
    # Sabendo qual a questão tem mais pixels
    my_pixel_val = np.zeros((questions, choices))
    count_c = 0
    count_r = 0
    for image in boxes:
        total_pixel = cv2.countNonZero(image)
        my_pixel_val[count_r][count_c] = total_pixel
        count_c += 1
        if count_c == choices:
            count_r += 1
            count_c = 0

    # Bota cada alternativa numa linha
    my_index = []
    for x in range(0, questions):
        arr = my_pixel_val[x]
        my_index_val = np.where(arr == np.amax(arr))
        my_index.append(my_index_val[0][0])
    print(my_index)
    cv2.waitKey(0)
    return my_index
