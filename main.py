from cv2 import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm
import requests
import json
import os

size = (1280, 720)

def download_image(url):
    img = Image.open(requests.get(url, stream=True).raw)
    return img

def pil_to_cv(image):
        open_cv_image = np.array(image)
        open_cv_image = open_cv_image[:, :, ::-1].copy()
        return open_cv_image

def gather_images():
    pics = []

    print("gathering images...")

    stats = json.loads(requests.get("https://ashen-hermit.000webhostapp.com/anime_pics/api/get_stats.php").text)
    print(stats)

    for i in tqdm(range(stats["pages_count"])):
        data = json.loads(requests.get("https://ashen-hermit.000webhostapp.com/anime_pics/api/get.php", params={"page": i}).text)
        for im in data:
            pics.append(im)

    print("images loaded: {}".format(len(pics)))

    with open("pics_links.json", "w+") as file:
        json.dump(pics, file)

    return pics

def load_pics_links_from_json():
    pics = []
    with open("pics_links.json", "r+") as file:
        pics = json.load(file)

    return pics

def add_fractal_frame(frames_list, text, inner_img_url=None, resize = True):
    frame = Image.new("RGB", size, (0, 0, 0))

    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 32)

    rect_size_f = (0.3, 0.3)

    draw = ImageDraw.Draw(frame)
    
    rect = ((size[0]//2-size[0]*rect_size_f[0], size[1]//2-size[1]*rect_size_f[1]),
        (size[0]//2+size[0]*rect_size_f[0], size[1]//2+size[1]*rect_size_f[1]))

    outline_width = 3

    draw.rectangle(rect, outline="white", width=outline_width)
    
    draw.text((size[0]//2 - draw.textsize(text, font=font)[0]//2, size[1]//2+size[1]*rect_size_f[1]+32), text, font=font)

    outline_width = 6

    rect = [(int(rect[0][0]//1)+outline_width, int(rect[0][1]//1)+outline_width), 
            (int((rect[1][0]-rect[0][0])//1)-outline_width*2+1, int((rect[1][1]-rect[0][1])//1)-outline_width*2+1)]

    if inner_img_url:
        inner_img = download_image(inner_img_url)
        if resize:
            width = int(rect[1][1] * inner_img.size[0]/inner_img.size[1])
            frame.paste(inner_img.resize(
                (width, rect[1][1])), 
                (int(size[0]//2-width//2), rect[0][1]))
        else:
            frame.paste(inner_img.resize(rect[1]), rect[0])
    else:
        if len(frames_list)>0:
            frame.paste(frames_list[len(frames_list)-1].resize(rect[1]), rect[0])

    frames_list.append(frame)

def main():
    # pics_links = gather_images()
    batch_size = 50
    pics_links = load_pics_links_from_json()

    for part in range(0, len(pics_links)//batch_size+1):
        pics_batch = pics_links[batch_size*part : min(batch_size*(part+1), len(pics_links))]

        resource_imgs = {
            'mihail': "https://sun9-53.userapi.com/impf/c854528/v854528057/1248c1/enE9wWLTqEI.jpg?size=1620x2160&quality=96&sign=4b0482bd1318435ec839783eb6f3388f&type=album"
        }

        frames_list = []

        if part==0:
            add_fractal_frame(frames_list, "добрый вечер", resource_imgs['mihail'], False)
            add_fractal_frame(frames_list, "я тут это...")
            add_fractal_frame(frames_list, "че хотел сказать...")

        print("rendering video...")

        batch_pics_count = len(pics_batch)
        for i in tqdm(range(batch_pics_count)):
            try:
                add_fractal_frame(frames_list, f"horny pressure: {((((part*batch_size)+i)/len(pics_links))*2000)//1}%", pics_batch[i]['source'])
            except:
                pass

        frames_list = list(map(pil_to_cv, frames_list))

        if not os.path.exists("batches"):
            os.makedirs("batches")

        out = cv2.VideoWriter(f'batches/project_{part}.mp4', cv2.VideoWriter_fourcc(*'MP4V'), 15, size)

        print("exporting video...")

        for i in tqdm(range(len(frames_list))):
            if i<3 and part==0:
                for j in range(8):
                    out.write(frames_list[i])
            else:
                out.write(frames_list[i])
            
        out.release()


if __name__ == "__main__":
    main()