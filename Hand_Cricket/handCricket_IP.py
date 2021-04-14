import cv2
import numpy as np
import math
import random
from time import sleep

cap = cv2.VideoCapture(0)


def check_status(player_score, bot_score):
    if player_score > bot_score:
        print('___CONGRATUTATIONLS___')
        print('___YOU WIN ___')
        print('YOU SCORED',player_score)

    elif player_score<bot_score:
        print('___BETTER LUCK NEXT TIME___')
        print('___COMPUTER WINS___')
        print('COMPUTER SCORED',bot_score)
    elif player_score == bot_score:
        print('___EQUAL SCORES___')
        print('Its a TIE___')
        print('BOTH SCORED', bot_score)
    else:
        pass


player_score = 0
bot_score = 0

player = False
bot = True

player_status = False
bot_status = False

while (1):

    try:


        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        kernel = np.ones((3, 3), np.uint8)

        # define region of interest
        roi = frame[100:400, 100:400]

        cv2.rectangle(frame, (100, 100), (400, 400), (0, 255, 0), 0)

        cv2.putText(frame, "Put hand in the box", (100, 90), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0))
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)



        # define range of skin color in HSV
        lower_skin = np.array([0, 20, 80], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)

        # extract skin colur imagw
        mask = cv2.inRange(hsv, lower_skin, upper_skin)

        # extrapolate the hand to fill dark spots within
        mask = cv2.dilate(mask, kernel, iterations=4)

        # blur the image
        mask = cv2.GaussianBlur(mask, (5, 5), 100)

        # find contours
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # find contour of max area(hand)
        if len(contours) > 0:
            # find contour of max area(hand)
            areas = [cv2.contourArea(c) for c in contours]
            max_index = np.argmax(areas)
            cnt = contours[max_index]

        cv2.drawContours(frame, cnt, -1,3)

        # approx the contour a little
        epsilon = 0.0005 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)

        # make convex hull around hand
        hull = cv2.convexHull(cnt)

        # define area of hull and area of hand
        areahull = cv2.contourArea(hull)
        areacnt = cv2.contourArea(cnt)

        # find the percentage of area not covered by hand in convex hull
        arearatio = ((areahull - areacnt) / areacnt) * 100
        # print(arearatio)

        # find the defects in convex hull with respect to hand
        hull = cv2.convexHull(approx, returnPoints=False)
        defects = cv2.convexityDefects(approx, hull)
        # print(defects)

        # sleep(2)
        # l = no. of defects
        count_defect = 0

        # code for finding no. of defects due to fingers
        for i in range(defects.shape[0]):
            s, e, f, d = defects[i, 0]
            start = tuple(approx[s][0])
            end = tuple(approx[e][0])
            far = tuple(approx[f][0])

            # find length of all sides of triangle
            a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
            b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
            c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)

            # apply cosine rule here
            angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 57
            # print(angle)

            # ignore angles > 90
            if angle <= 90:
                count_defect += 1
                cv2.circle(roi, far, 5, (255, 0, 0), -1)

            # draw lines around hand
            cv2.line(roi, start, end, (0, 255, 0), 3)

        count_defect += 1

        # - - - - - - - - - - - - - - - - - -

        player_num = count_defect

        if cv2.waitKey(10) & 0xFF == ord(' '):

            # print corresponding gestures which are in their ranges
            font = cv2.FONT_HERSHEY_SIMPLEX

            if count_defect == 1:
                if arearatio < 20:
                    cv2.putText(frame, '0', (0, 150), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                else:
                    cv2.putText(frame, '1', (0, 150), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

            elif count_defect == 2:
                cv2.putText(frame, '2', (0, 150), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

            elif count_defect == 3:
                cv2.putText(frame, '3', (0, 150), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

            elif count_defect == 4:
                cv2.putText(frame, '4', (0, 150), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

            elif count_defect == 5:
                cv2.putText(frame, '5', (0, 150), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

            if player is False:  # i.e. player will bat first
                print('BAT NOW !')
                bot_num = random.randint(0, 5)

                if player_num == bot_num:
                    print('{} - {}'.format(player_num, bot_num), end=' ')
                    print(' You are out!')
                    # print('Final score of Player: {}'.format(player_score))
                    print()
                    print()
                    print('Computer will bat now!')
                    player_status = True
                    player = True
                    bot = False

                else:
                    player_score += player_num
                    print('{} - {}'.format(player_num, bot_num))
                    print('Your current score: {}'.format(player_score))



            elif bot is False:  # i.ie if player is out, bot will bat
                bot_num = random.randint(0, 5)

                if bot_num == player_num:
                    print('{} - {}'.format(bot_num, player_num), end=' ')
                    print('Computer is out!')
                    bot_status = True
                    # print('Final score of Bot: {}'.format(bot_score))
                    print()
                    print()
                    check_status(player_score, bot_score)

                else:
                    bot_score += bot_num
                    print('{} - {}'.format(bot_num, player_num))
                    print('Computer current score: {}'.format(bot_score))


    except:
        pass

    cv2.putText(frame, "{}".format(player_score), (820, 370), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0))
    cv2.putText(frame, "{}".format(bot_score), (1050, 370), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0))

    if player_status == True:
        cv2.putText(frame, "OUT !", (820, 470), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 155))

    if bot_status == True:
        cv2.putText(frame, "OUT !", (1050, 470), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 155))


    # show the windows
    #cv2.imshow('mask', mask)
    cv2.imshow('frame', frame)

    k = cv2.waitKey(50) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()
cap.release()