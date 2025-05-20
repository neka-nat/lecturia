import base64
import uuid

from bs4 import BeautifulSoup
from loguru import logger

from .chains.image_explorer import create_image_explorer_chain
from .chains.image_generator import create_image_generator_chain
from .chains.slide_maker import HtmlSlide
from .chains.slide_refiner import create_slide_refiner_chain


def edit_slide(slide: HtmlSlide) -> HtmlSlide:
    logger.info("Editing slide")
    refiner = create_slide_refiner_chain()
    refined_slide = refiner.invoke({"before_slide": slide.html})
    soup = BeautifulSoup(refined_slide.html, "html.parser")
    # imgタグを探す
    img_tags = soup.find_all("img")
    image_map = {}
    for img_tag in img_tags:
        src = img_tag.get("src")
        alt = img_tag.get("alt")
        if not src or not alt:
            continue
        # srcがgenerated-imageかsearched-imageかを判断
        if src.startswith("generated-image"):
            logger.info(f"Generating image for {alt}")
            generator = create_image_generator_chain()
            images = generator.invoke(alt)
            img_tag["src"] = uuid.uuid4().hex
            image_map[img_tag["src"]] = images[0]
        elif src.startswith("searched-image"):
            logger.info(f"Searching image for {alt}")
            explorer = create_image_explorer_chain()
            images = explorer.invoke(alt.split(","))
            img_tag["src"] = uuid.uuid4().hex
            image_map[img_tag["src"]] = images[0]
        else:
            continue
    return HtmlSlide(html=soup.prettify(), image_map=image_map)
