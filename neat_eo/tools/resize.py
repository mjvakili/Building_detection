import glob

def crop(img, height,width, imgheight, imgwidth):
	for i in range(int(imgheight//height)):
		for j in range(int(imgwidth//width)):
			box = (j*width, i*height, (j+1)*width, (i+1)*height)
			yield img.crop(box)


def resize(heigth, width):
	for imgdir in os.listdir('./labels'):
		basename = '*.png'
		filelist = glob.glob(os.path.join('labels',imgdir,'masks', basename))
		filelist.sort(reverse=True)

		for filenum, file in tqdm(enumerate(filelist)):
			img = Image.open(file)
			imgwidth, imgheight = img.size
			height = int(imgheight/2)
			width = int(imgwidth/2)

			for k, piece in enumerate(crop(img,height,width,imgwidth,imgheight)):
				img_piece = piece
				path = os.path.join(file[:-4] + str(k+1) + ".png")
				img_piece.save(path)

			os.remove(file)
	
