from src.models import (
    BoundingBox,
    SelectorType,
    ContainerSearchResult,
    ContainerFinderResult,
)
from typing import Optional, List
from typing import List, Optional


def get_children_of_bbox(
    bounding_boxes: List[BoundingBox], parent_bbox: BoundingBox
) -> List[BoundingBox]:
    """
    Restituisce la lista dei BoundingBox che sono figli diretti del bounding box specificato.
    """
    parent_xpath = parent_bbox.xpath
    children_xpath_prefix = parent_xpath + "/"
    parent_depth = parent_xpath.count("/")
    return [
        bbox
        for bbox in bounding_boxes
        if bbox.xpath.startswith(children_xpath_prefix)
        and bbox.xpath.count("/") == parent_depth + 1
    ]


def find_bbox_by_selector(
    bounding_boxes: List[BoundingBox],
    selector: str,
    selector_type: SelectorType,
) -> Optional[BoundingBox]:
    """
    Restituisce il BoundingBox che corrisponde esattamente al selettore fornito (css_selector o xpath).
    """
    for bbox in bounding_boxes:
        if selector_type == SelectorType.CSS and bbox.css_selector == selector:
            return bbox
        if selector_type == SelectorType.XPATH and bbox.xpath == selector:
            return bbox
    return None


class DOMContainerFinder:
    def __init__(self, max_depth: int = 50):
        self.max_depth = max_depth

    def find_container(
        self,
        bounding_boxes: List[BoundingBox],
        start_selector: str,
        selector_type: SelectorType = SelectorType.CSS,
    ) -> ContainerSearchResult:

        if not bounding_boxes:
            return ContainerSearchResult(
                result_type=ContainerFinderResult.INVALID_SELECTOR,
                container=None,
                search_path=[],
                message="Nessun bounding box fornito",
                depth=0,
            )

        start_element = self._find_element_by_selector(
            bounding_boxes, start_selector, selector_type
        )

        if not start_element:
            return ContainerSearchResult(
                result_type=ContainerFinderResult.SELECTOR_NOT_FOUND,
                container=None,
                search_path=[],
                message=f"Selettore '{start_selector}' non trovato",
                depth=0,
            )

        return self._recursive_search(bounding_boxes, start_element, [])

    def _find_element_by_selector(
        self,
        bounding_boxes: List[BoundingBox],
        selector: str,
        selector_type: SelectorType,
    ) -> Optional[BoundingBox]:
        for bbox in bounding_boxes:
            if selector_type == SelectorType.CSS and bbox.css_selector == selector:
                return bbox
            if selector_type == SelectorType.XPATH and bbox.xpath == selector:
                return bbox
        return None

    def _get_direct_children(
        self, bounding_boxes: List[BoundingBox], parent: BoundingBox
    ) -> List[BoundingBox]:
        parent_xpath = parent.xpath
        children_xpath_prefix = parent_xpath + "/"
        parent_depth = parent_xpath.count("/")

        return [
            bbox
            for bbox in bounding_boxes
            if bbox.xpath.startswith(children_xpath_prefix)
            and bbox.xpath.count("/") == parent_depth + 1
        ]

    def _recursive_search(
        self,
        bounding_boxes: List[BoundingBox],
        current_element: BoundingBox,
        search_path: List[BoundingBox],
    ) -> ContainerSearchResult:
        current_path = search_path + [current_element]

        if len(current_path) > self.max_depth:
            return ContainerSearchResult(
                result_type=ContainerFinderResult.DEPTH_LIMIT_REACHED,
                container=None,
                search_path=current_path,
                message=f"Raggiunta profondità massima ({self.max_depth})",
                depth=len(current_path),
            )

        direct_children = self._get_direct_children(bounding_boxes, current_element)
        num_children = len(direct_children)

        if num_children > 1:
            return ContainerSearchResult(
                result_type=ContainerFinderResult.SUCCESS,
                container=current_element,
                search_path=current_path,
                message=f"Container trovato con {num_children} figli",
                depth=len(current_path),
            )

        elif num_children == 0:
            return ContainerSearchResult(
                result_type=ContainerFinderResult.LEAF_NODE_FOUND,
                container=current_element,
                search_path=current_path,
                message="Nodo foglia trovato (0 figli)",
                depth=len(current_path),
            )

        else:  # num_children == 1
            return self._recursive_search(
                bounding_boxes, direct_children[0], current_path
            )

    def get_container_analysis(self, result: ContainerSearchResult) -> dict:
        analysis = {
            "success": result.result_type
            in {ContainerFinderResult.SUCCESS, ContainerFinderResult.LEAF_NODE_FOUND},
            "result_type": result.result_type.value,
            "message": result.message,
            "search_depth": result.depth,
            "search_path_length": len(result.search_path),
            "container_info": None,
        }

        if result.container:
            analysis["container_info"] = {
                "css_selector": result.container.css_selector,
                "xpath": result.container.xpath,
                "tag": result.container.tag,
                "area": result.container.area(),
                "num_children": result.container.num_children,
                "dimensions": {
                    "x": result.container.x,
                    "y": result.container.y,
                    "width": result.container.width,
                    "height": result.container.height,
                },
            }

        analysis["search_path"] = [
            {
                "xpath": element.xpath,
                "tag": element.tag,
                "num_children": element.num_children,
            }
            for element in result.search_path
        ]

        return analysis
