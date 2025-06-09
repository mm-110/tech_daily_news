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
)

from src.vlm import ModelType
import time
import pandas as pd
import hashlib
import os


def main():
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
    df = pd.DataFrame(
        [
            {
                "css_selector": bbox.css_selector,
                "xpath": bbox.xpath,
                "x": bbox.x,
                "y": bbox.y,
                "width": bbox.width,
                "height": bbox.height,
                "area": bbox.area(),
                "tag": str(bbox.tag),
                "num_children": bbox.num_children,
            }
            for bbox in bounding_boxes_sorted
        ]
    )
    df.to_csv("bounding_boxes.csv", index=False)
    print(f"Salvati {len(bounding_boxes_sorted)} bounding box in bounding_boxes.csv")
    print(f"{df.shape}")

    # Screenshot solo dei primi 10 bounding box con area maggiore e num_children > 1, evitando box contenuti l'uno nell'altro
    # top_boxes = (
    #     df[df["num_children"] > 1].sort_values("area", ascending=False).head(30)
    # )  # prendi più di 10 per sicurezza
    # selected = []
    # for _, row in top_boxes.iterrows():
    #     x0, y0, w0, h0 = row["x"], row["y"], row["width"], row["height"]
    #     contained = False
    #     for sel in selected:
    #         x1, y1, w1, h1 = sel["x"], sel["y"], sel["width"], sel["height"]
    #         # Se il box corrente è completamente contenuto in uno già selezionato
    #         if (
    #             x0 >= x1
    #             and y0 >= y1
    #             and (x0 + w0) <= (x1 + w1)
    #             and (y0 + h0) <= (y1 + h1)
    #         ):
    #             contained = True
    #             break
    #     if not contained:
    #         selected.append(row)
    #     if len(selected) == 10:
    #         break

    os.makedirs("screenshots", exist_ok=True)
    # Cerca il bounding box con lo xpath richiesto
    # target_xpath = "/html/body/div[2]/div[2]/div/div[2]/div"
    # bbox = next((b for b in bounding_boxes if b.xpath == target_xpath), None)
    # if bbox:
    #     selector = bbox.css_selector.strip()
    #     hash_name = hashlib.md5(selector.encode()).hexdigest()
    #     path = os.path.join("screenshots", f"{hash_name}")
    #     print(f"Screenshot per tag: {bbox.tag}")
    #     screenshot_output = screenshot_element(
    #         ScreenshotElementInput(selector=selector, path=path, output_format="jpg")
    #     )
    #     description = describe_screenshot_element(
    #         screenshot_output=screenshot_output,
    #         page_info=page_info,
    #         bounding_box=bbox,
    #         model=ModelType.LLAMA
    #     )
    #     print(f"Descrizione VLM:\n{description}\n{'-'*60}")
    # else:
    #     print(f"[WARN] Nessun bounding box trovato con xpath: {target_xpath}")

    # --- LOGICA CONTAINER E CHILDREN ---
    # Usa il DataFrame già creato (df)
    # max_area = df[df['num_children'] > 1]['area'].max()
    # candidates = df[(df['num_children'] > 1) & (df['area'] == max_area)]
    # real_container = candidates.loc[candidates['xpath'].str.len().idxmax()]
    # print("Container selezionato:")
    # print(real_container)

    # container_xpath = real_container['xpath']
    # num_children = real_container['num_children']
    # children_xpath_prefix = container_xpath + '/'

    # children = df[
    #     df['xpath'].str.startswith(children_xpath_prefix) &
    #     (df['xpath'].str.count('/') == container_xpath.count('/') + 1)
    # ]

    # print(f"\nNumero di figli trovati: {len(children)} (num_children dichiarati: {num_children})")

    # for i, row in children.iterrows():
    #     print(i, "\n", row)
    #     selector = row['css_selector'].strip()
    #     hash_name = hashlib.md5(selector.encode()).hexdigest()
    #     path = os.path.join("screenshots", f"{hash_name}")
    #     bbox = next((b for b in bounding_boxes if b.xpath == row['xpath']), None)
    #     if not bbox:
    #         print(f"[WARN] BoundingBoxInfo non trovato per {selector}")
    #         continue
    #     print(f"Screenshot per tag: {bbox.tag}")
    #     screenshot_output = screenshot_element(
    #         ScreenshotElementInput(selector=selector, path=path, output_format="jpg")
    #     )
        # description = describe_screenshot_element(
        #     screenshot_output=screenshot_output,
        #     page_info=page_info,
        #     bounding_box=bbox,
        #     model=ModelType.LLAMA
        # )
        # print(f"Descrizione VLM:\n{description}\n{'-'*60}")

    # --- LOGICA CONTAINER E CHILDREN RICORSIVA ---
    max_area = df[df['num_children'] > 1]['area'].max()
    candidates = df[(df['num_children'] > 1) & (df['area'] == max_area)]
    real_container = candidates.loc[candidates['xpath'].str.len().idxmax()]
    print("Container selezionato:")
    print(real_container)

    def find_deepest_with_multiple_children(row, df):
        """
        Ricorsivamente trova il discendente più profondo che ha più di 1 figlio (basato su xpath),
        oppure restituisce l'elemento stesso se ha più di 1 figlio diretto.
        """
        xpath = row['xpath']
        children_xpath_prefix = xpath + '/'
        # Trova figli diretti
        children = df[
            df['xpath'].str.startswith(children_xpath_prefix) &
            (df['xpath'].str.count('/') == xpath.count('/') + 1)
        ]
        if len(children) == 1:
            # Ricorsione sul figlio unico
            return find_deepest_with_multiple_children(children.iloc[0], df)
        else:
            # Se ha più di 1 figlio (o nessuno), restituisci l'elemento attuale
            return row

    container_xpath = real_container['xpath']
    num_children = real_container['num_children']
    children_xpath_prefix = container_xpath + '/'

    children = df[
        df['xpath'].str.startswith(children_xpath_prefix) &
        (df['xpath'].str.count('/') == container_xpath.count('/') + 1)
    ]

    print(f"\nNumero di figli trovati: {len(children)} (num_children dichiarati: {num_children})")

    descrizioni = []
    results = []
    for i, row in children.iterrows():
        target_row = find_deepest_with_multiple_children(row, df)
        print(f"[{i}] Elemento selezionato per screenshot:")
        print(target_row)
        selector = target_row['css_selector'].strip()
        hash_name = hashlib.md5(selector.encode()).hexdigest()
        path = os.path.join("screenshots", f"{hash_name}")
        bbox = next((b for b in bounding_boxes if b.xpath == target_row['xpath']), None)
        if not bbox:
            print(f"[WARN] BoundingBoxInfo non trovato per {selector}")
            continue
        print(f"Screenshot per tag: {bbox.tag}")
        screenshot_output = screenshot_element(
            ScreenshotElementInput(selector=selector, path=path, output_format="jpg")
        )
        description = describe_screenshot_element(
            screenshot_output=screenshot_output,
            page_info=page_info,
            bounding_box=bbox,
            model=ModelType.OPENAI
        )
        # Crea un dizionario con tutte le info del bounding box + descrizione
        result = dict(target_row)
        result['description'] = description
        results.append(result)
        descrizioni.append(description)
        print(f"Descrizione VLM:\n{description}\n{'-'*60}")
    # Salva il nuovo DataFrame con le descrizioni
    results_df = pd.DataFrame(results)
    results_df.to_csv("bounding_boxes_with_descriptions.csv", index=False)
    # Salva tutte le descrizioni in un file txt
    # with open("descriptions.txt", "w", encoding="utf-8") as f:
    #     for d in descrizioni:
    #         f.write(str(d))
    #         f.write("\n\n---\n\n")
    close_browser_session()
    return


if __name__ == "__main__":
    main()
