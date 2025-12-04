#!/usr/bin/env python3
"""Convert HTML file to PDF using Playwright."""

import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright


async def html_to_pdf(html_path: str, output_path: str = None) -> None:
    """
    Convert an HTML file to PDF using Playwright.
    
    Args:
        html_path: Path to the input HTML file
        output_path: Path to the output PDF file (defaults to html_path with .pdf extension)
    """
    html_path = Path(html_path)
    if not html_path.exists():
        raise FileNotFoundError(f"HTML file not found: {html_path}")
    
    if output_path is None:
        output_path = html_path.with_suffix('.pdf')
    else:
        output_path = Path(output_path)
    
    # Convert to absolute paths for file:// URL
    html_abs_path = html_path.resolve()
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Load the HTML file
            await page.goto(f"file://{html_abs_path}", wait_until="networkidle")
            
            # Import and apply Inter font from Google Fonts
            await page.add_style_tag(content="""
                @import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap');
                
                * {
                    font-family: "Inter", sans-serif !important;
                    font-optical-sizing: auto;
                    font-style: normal;
                }
            """)
            
            # Wait for font to load from Google Fonts
            await page.wait_for_timeout(500)
            
            # Generate PDF with 95% scale and 0 margins (negative margins applied via CSS above)
            await page.pdf(
                path=str(output_path),
                format="A4",
                print_background=True,
                scale=0.91,
                margin={"top": "0px", "right": "25px", "bottom": "0px", "left": "25px"},
            )
            
            await browser.close()
        
        print(f"✓ PDF generated successfully: {output_path}")
    except Exception as e:
        error_msg = str(e)
        if "missing dependencies" in error_msg.lower():
            print("\n❌ Error: Missing system dependencies for Playwright")
            print("\nPlease install the required dependencies:")
            print("  sudo apt-get install libnspr4 libnss3 libasound2t64")
            print("\nOr run:")
            print("  sudo playwright install-deps")
            sys.exit(1)
        else:
            print(f"\n❌ Error converting HTML to PDF: {e}")
            raise


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python html_to_pdf.py <html_file> [output_pdf]")
        print("Example: python html_to_pdf.py cv.html")
        sys.exit(1)
    
    html_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    asyncio.run(html_to_pdf(html_file, output_file))


if __name__ == "__main__":
    main()

