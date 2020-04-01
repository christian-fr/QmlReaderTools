__author__ = "Christian Friedrich"
__maintainer__ = "Christian Friedrich"
__license__ = "GPL v3"
__version__ = "0.1.0"
__status__ = "Prototype"
__name__ = "ImagePostprocessing"
# last edited: 2020/03/12

from math import ceil

from PIL import Image


class ImagePostProcessing:
    """
    """

    def __init__(self):
        self.input_file = 'output_file.png'
        self.output_file = 'output_file'
        self.aspect_ratio = 0.7
        self.px_overlap = 30
        self.image = self.load_image(self.input_file)
        self.image = self.image.convert("RGB")
        self.get_size()
        self.list_of_images = []
        self.post_process_iteration()
        self.write_images()

    @staticmethod
    def load_image(path):
        return Image.open(path)

    def get_size(self):
        """
        :return: none
        """

        self.width = self.image.size[0]
        self.height = self.image.size[1]

    def post_process_iteration(self, workaround=True):
        page_height = int((self.width + self.px_overlap) / self.aspect_ratio)
        image_height = int(page_height - self.px_overlap)
        print("width")
        print(self.width)
        print("height")
        print(self.height)
        print("px_overlap")
        print(self.px_overlap)
        print("page_height")
        print(page_height)
        number_of_images = ceil(self.height / image_height)
        print(number_of_images)
        self.list_of_images = []
        for i in range(0, number_of_images):
            index_string = format(i, '03d')
            output_filename = 'outfile' + index_string + '.png'
            # im.crop((left, upper, right, lower))

            if workaround is False and i is (number_of_images - 1):
                # img_temp = ImageOps.expand(
                temp_img = self.image.crop((0, (i * image_height), self.width, self.height))
                temp_img.save('test.png')

                '''
                    (0, (i * image_height), self.width, ((i + 1) * image_height) + self.px_overlap)),
                    border=page_height, fill=(255, 255, 255))\
                    .crop(page_height, page_height, self.width, page_height)
                )
                '''
            # workaround until ImageOps.expand is workable

            if workaround is True and i is number_of_images - 1:
                self.image.crop((0, (self.height - page_height), self.width, self.height)).save(
                    output_filename)
            else:
                self.image.crop((0, (i * image_height), self.width, ((i + 1) * image_height) + self.px_overlap)).save(
                    output_filename)

            # img_temp.save('outfile' + format(i, '02d') + '.png')

    def write_images(self):
        pass
