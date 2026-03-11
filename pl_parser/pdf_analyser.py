"""PDF analyser script - analyses a PDF and generates a report."""

import argparse
import json
import sys
from pathlib import Path

import pymupdf

# An image is "big enough to contain text" if it covers at least this fraction of the page area.
IMAGE_SIZE_THRESHOLD = 0.15


def _image_dpi(img_info: dict) -> int | None:
    """Calculate the average DPI of an image from its pixel size and page bounding box."""
    bbox = img_info.get("bbox")
    width_px = img_info.get("width")
    height_px = img_info.get("height")

    if not bbox or not width_px or not height_px:
        return None

    bbox_width_pt = bbox[2] - bbox[0]
    bbox_height_pt = bbox[3] - bbox[1]

    if bbox_width_pt <= 0 or bbox_height_pt <= 0:
        return None

    # 1 inch = 72 points
    dpi_x = width_px / (bbox_width_pt / 72)
    dpi_y = height_px / (bbox_height_pt / 72)
    return round((dpi_x + dpi_y) / 2)


def _is_large_image(img_info: dict, page_area: float) -> bool:
    """Return True if the image covers at least IMAGE_SIZE_THRESHOLD of the page."""
    bbox = img_info.get("bbox")
    if not bbox or page_area <= 0:
        return False
    img_area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
    return (img_area / page_area) >= IMAGE_SIZE_THRESHOLD


def analyse_pdf(pdf_path: str) -> dict:
    """Analyse a PDF file and return a report dictionary."""
    path = Path(pdf_path)

    if not path.exists():
        print(f"Error: file '{pdf_path}' not found.", file=sys.stderr)
        sys.exit(1)

    if path.suffix.lower() != ".pdf":
        print(f"Error: '{pdf_path}' does not have a .pdf extension.", file=sys.stderr)
        sys.exit(1)

    file_size = path.stat().st_size
    doc = pymupdf.open(str(path))
    page_count = doc.page_count

    pages_with_large_images: list[int] = []
    image_dpi_list: list[int] = []
    image_only_pages = 0

    for page_num, page in enumerate(doc, start=1):
        page_rect = page.rect
        page_area = page_rect.width * page_rect.height
        images = page.get_image_info(hashes=False, xrefs=True)

        large_images = [img for img in images if _is_large_image(img, page_area)]

        if large_images:
            pages_with_large_images.append(page_num)
            for img in large_images:
                dpi = _image_dpi(img)
                if dpi is not None:
                    image_dpi_list.append(dpi)

            # Page is "image-only" when it has a large image and almost no extractable text.
            text = page.get_text().strip()
            if len(text) < 50:
                image_only_pages += 1

    doc.close()

    if not pages_with_large_images:
        content_type = "text"
    elif image_only_pages == page_count:
        content_type = "image"
    else:
        content_type = "both"

    return {
        "file": path.name,
        "page_count": page_count,
        "size": file_size,
        "content_type": content_type,
        "pages_with_large_images": pages_with_large_images,
        "image_dpi": image_dpi_list,
    }


def _format_as_text(report: dict) -> str:
    """Format the report as a human-readable string."""
    large_img_pages = (
        ", ".join(str(p) for p in report["pages_with_large_images"]) or "none"
    )
    dpi_values = ", ".join(str(d) for d in report["image_dpi"]) or "N/A"

    return (
        f"File:                    {report['file']}\n"
        f"Pages:                   {report['page_count']}\n"
        f"Size:                    {report['size']} bytes\n"
        f"Content type:            {report['content_type']}\n"
        f"Pages with large images: {large_img_pages}\n"
        f"Image DPI:               {dpi_values}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyse a PDF file and generate a report."
    )
    parser.add_argument("pdf", help="Path to the PDF file to analyse")
    parser.add_argument(
        "--astext",
        action="store_true",
        help="Output a human-readable text report instead of JSON (default)",
    )

    args = parser.parse_args()
    report = analyse_pdf(args.pdf)

    if args.astext:
        print(_format_as_text(report))
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
