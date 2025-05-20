import base64

from bs4 import BeautifulSoup

from .chains.image_explorer import create_image_explorer_chain
from .chains.image_generator import create_image_generator_chain
from .chains.slide_maker import HtmlSlide
from .chains.slide_refiner import create_slide_refiner_chain


def edit_slide(slide: HtmlSlide) -> HtmlSlide:
    refiner = create_slide_refiner_chain()
    refined_slide = refiner.invoke({"before_slide": slide.html})
    soup = BeautifulSoup(refined_slide.html, "html.parser")
    # imgタグを探す
    img_tags = soup.find_all("img")
    for img_tag in img_tags:
        src = img_tag.get("src")
        alt = img_tag.get("alt")
        if not src or not alt:
            continue
        # srcがgenerated-imageかsearched-imageかを判断
        if src.startswith("generated-image"):
            generator = create_image_generator_chain()
            images = generator.invoke(alt)
            img_tag["src"] = f"data:image/png;base64,{base64.b64encode(images[0].tobytes()).decode('utf-8')}"
        elif src.startswith("searched-image"):
            explorer = create_image_explorer_chain()
            images = explorer.invoke(alt)
            img_tag["src"] = f"data:image/png;base64,{base64.b64encode(images[0].tobytes()).decode('utf-8')}"
        else:
            continue
    return HtmlSlide(html=soup.prettify())
