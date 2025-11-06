import cv2

cap = cv2.VideoCapture(0)
cap.set(1280)
cap.set(720)

while True: 
    ret, frame = cap,read()
    cv2.imshow('Live Video', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
