import csv
from src.session_tools import (
    open_browser_session,
    close_browser_session,
    navigate_to_url,
    get_bounding_boxes,
    highlight_bounding_box,
    scroll_page_down,
    scroll_page_up,
    screenshot_element,
    get_structured_page_content,
    get_page_info,
    describe_screenshot_element,
)
from src.models import (
    GetBoundingBoxesInput,
    HighlightBoundingBoxInput,
    NavigateToUrlInput,
    ScreenshotElementInput,
    PageInfoInput,
    PageInfoOutput,
    SelectorType,
    ContainerFinderResult,
)
from src.bounding_box_handler import (
    DOMContainerFinder,
    get_children_of_bbox,
    find_bbox_by_selector,
)
from src.vlm import ModelType
import time
import pandas as pd
import hashlib
import os


def main():

    os.makedirs("screenshots", exist_ok=True)
    dom_container_finder = DOMContainerFinder()

    page_type = "LISTING"
    url = "https://www.bulgari.com/en-us/jewelry"

    # 1. Apri browser e naviga
    open_browser_session()
    navigate_to_url(NavigateToUrlInput(url=url))
    time.sleep(2)

    content = get_structured_page_content().structured_content
    # Salva il contenuto strutturato in un file txt
    with open("structured_content.txt", "w", encoding="utf-8") as f:
        f.write(content)

    page_info = get_page_info(PageInfoInput(page_type=page_type, url=url))

    # 3. Recupera tutti i bounding box visibili
    bbox_output = get_bounding_boxes(GetBoundingBoxesInput(selector="body"))
    bounding_boxes = bbox_output.bounding_boxes

    # 5. Salva in un CSV i dati dei bounding box ordinati per area usando pandas
    bounding_boxes_sorted = sorted(bounding_boxes, key=lambda b: b.area(), reverse=True)

    page_main = find_bbox_by_selector(
        bounding_boxes=bounding_boxes_sorted,
        selector="/html/body[2]/div[3]/div[2]/div[1]/div[4]/main[1]/div[2]/div[3]",
        selector_type=SelectorType.XPATH,
    )

    result = dom_container_finder.find_container(
        bounding_boxes=bounding_boxes_sorted,
        start_selector=page_main.xpath,
        selector_type=SelectorType.XPATH,
    )

    if result.result_type == ContainerFinderResult.SUCCESS:
        print("Container trovato con successo!")
        print(f"Container: {result.container}")
        print(f"Search Path: {[b.xpath for b in result.search_path]}")

        root_container = result.container
        print(f"Root Container: {root_container}")
        root_children = get_children_of_bbox(bounding_boxes_sorted, root_container)

        for bbox in root_children:
            print(f"Processing selector: {bbox}")
            selector = bbox.css_selector.strip()
            hash_name = hashlib.md5(selector.encode()).hexdigest()
            path = os.path.join("screenshots", f"{hash_name}")
            screenshot_output = screenshot_element(
                ScreenshotElementInput(
                    selector=selector, path=path, output_format="jpg"
                )
            )
            print(f"Screenshot salvato in: {path}")

    else:
        print("Nessun container trovato.")
        print(f"Messaggio: {result.message}")
        print(f"Search Path: {[b.xpath for b in result.search_path]}")

    close_browser_session()
    return


if __name__ == "__main__":
    main()
