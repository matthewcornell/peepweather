from PIL import Image
from PIL import ImageDraw


def imageForForecast(forecast):
    """
    :return: a PIL Image corresponding to forecast to be used for sticker embedding
    """
    # todo get a temporary png file so we have an Image to work with. later it will be generated
    # dynamically - Sticker.generateImage(forecast)
    image = Image.open('/Users/matt/IdeaProjects/rc-weather-flask/app/static/sticker-126x187-temp.png')
    return image
