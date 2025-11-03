import cv2
import torch
import urllib.request # this can be removed when we use camara
import ffmpeg
import numpy as np

#pip install timm #needed for midas

import matplotlib.pyplot as plt #this can be removed its just to show result


# ths needs to be the camara code
#url, filename = ("https://github.com/pytorch/hub/raw/master/images/dog.jpg", "dog.jpg")
#urllib.request.urlretrieve(url, filename)

#model_type = "DPT_Large"     # MiDaS v3 - Large     (highest accuracy, slowest inference speed)
#model_type = "DPT_Hybrid"   # MiDaS v3 - Hybrid    (medium accuracy, medium inference speed)
model_type = "MiDaS_small"  # MiDaS v2.1 - Small   (lowest accuracy, highest inference speed)

midas = torch.hub.load("intel-isl/MiDaS", model_type)

device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
midas.to(device)
midas.eval()

midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")


transform = midas_transforms.small_transform

# filename = camara feed



out, _ = (
    ffmpeg
    .input('/dev/video0', f='v4l2', input_format='mjpeg', video_size='1920x1080')
    .output('pipe:', vframes=1, format='image2', vcodec='mjpeg')
    .run(capture_stdout=True, capture_stderr=True)
)

# Convert the bytes to a numpy array
img = cv2.imdecode(np.frombuffer(out, np.uint8), cv2.IMREAD_COLOR)
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

input_batch = transform(img).to(device)

with torch.no_grad():
    prediction = midas(input_batch)

    prediction = torch.nn.functional.interpolate(
        prediction.unsqueeze(1),
        size=img.shape[:2],
        mode="bicubic",
        align_corners=False,
    ).squeeze()

output = prediction.cpu().numpy()


#this can be removed its just to show result
plt.imshow(output)
plt.savefig('foo.png')
