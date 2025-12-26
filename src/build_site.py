import re
import os
from jinja2 import Environment, FileSystemLoader
import urllib.parse

# Configuration
PLAN_FILE = 'road_trip_plan.md'
TEMPLATE_DIR = 'src/templates'
TEMPLATE_FILE = 'index.html'
OUTPUT_DIR = 'docs'
OUTPUT_FILE = 'index.html'

def parse_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    itinerary_html = ""
    shortlist_html = ""
    
    current_section = None
    day_card_open = False
    
    # Buffers for Shortlist sections
    hotels_content = []
    food_content = []
    packing_content = []
    
    current_shortlist_buffer = None

    for line in lines:
        line = line.strip()
        
        # --- Itinerary Parsing ---
        if line.startswith('### Day'):
            if day_card_open:
                itinerary_html += '            </div>\n        </div>\n\n' # Close previous day
            
            # Extract Day Title and Date
            # Format: ### Day 1: Friday Dec 26 - The Departure
            match = re.match(r'### (Day \d+): (.+?) - (.+)', line)
            if match:
                day_num, date, title = match.groups()
                itinerary_html += f'''            <!-- {day_num} -->
            <div class="day-card">
                <div class="day-header">
                    <h3>{day_num}: {title}</h3>
                    <span class="date">{date}</span>
                </div>
                <div class="day-body">
'''
                day_card_open = True
                current_section = "itinerary"
                continue

        # Time Blocks (Itinerary)
        # Format: *   **10:30 AM EST**: Depart Atlanta.
        if current_section == "itinerary" and line.startswith('*   **'):
            match = re.match(r'\*   \*\*(.+?)\*\*: (.+)', line)
            if match:
                time, title = match.groups()
                # Clean title formatting if needed (basic)
                description = "" 
                itinerary_html += f'''                    <div class="time-block">
                        <span class="time">{time}</span>
                        <div class="details">
                            <strong>{title}</strong>
'''
                continue
        
        # Details/Notes (Itinerary)
        # Format:     *   *Stop*: 30 mins.
        if current_section == "itinerary" and line.startswith('    *   '):
            note = line.replace('    *   ', '').replace('*', '') # Basic cleanup
            # Provide nicer formatting for labels like "Drive:", "Activity:"
            if ':' in note:
                parts = note.split(':', 1)
                if len(parts) == 2:
                    label, text = parts
                    itinerary_html += f'                            <p><span style="color:#666;">{label}:</span> {text}</p>\n'
                else:
                    itinerary_html += f'                            <p>{note}</p>\n'
            else:
                itinerary_html += f'                            <p>{note}</p>\n'
            continue
            
        # Close Time Block div (implicit - just add closing tag if we see a new time block? No, simpler to just let them flow. 
        # Actually, HTML structure requires closing </div> for time-block.
        # My parsing above leaves the div open. I should close it before starting a new one.
        # This simple parser is getting tricky. Let's fix the time block closure logic.
        # Improved Logic: We will append the closing </div></div> only when we start a NEW time block or end the day.
        # But wait, my snippet above:
        # <div class="details"> ... <p>...</p> (missing closing div for details and time-block)
        
        # Let's adjust: The parsing loop logic needs to be a bit more stateful or accumulate lines.
        # For simplicity in this script, I'll switch to a block-based accumulator if I can, OR just inject closing tags carefully.
        
        # --- Shortlist Parsing ---
        if line.startswith('## 🏨 Action Items') or line.startswith('## 🏨 Hotels'):
            current_section = "hotels"
            current_shortlist_buffer = hotels_content
            continue
        elif line.startswith('## 🍔 Food'):
            current_section = "food"
            current_shortlist_buffer = food_content
            continue
        elif line.startswith('## 🎒 Packing'):
            current_section = "packing"
            current_shortlist_buffer = packing_content
            continue
        elif line.startswith('## '): # key to switch out of itinerary
            current_section = None
            current_shortlist_buffer = None
            
        # Capture Shortlist Content
        if current_shortlist_buffer is not None:
             if line.startswith('*   ') or line.startswith('    *   ') or line.startswith('1.  '):
                 # Convert markdown list to HTMLish text for now
                 # Process links [Text](url) -> <a href="url" target="_blank">Text</a>
                 html_line = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" target="_blank">\1</a>', line)
                 # Process bold **Text** -> <strong>Text</strong>
                 html_line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_line)
                 
                 # Strip list bullets
                 html_line = re.sub(r'^[\*\d]+\.\s+', '', html_line).strip()
                 html_line = html_line.replace('✅', '✅ ') # Ensure space
                 
                 # Add line break
                 current_shortlist_buffer.append(f'{html_line}<br>')

    # Final cleanup for Itinerary
    if day_card_open:
        itinerary_html += '                </div>\n            </div>\n' # Missing the closing divs for the last time block...
    
    # RE-DOING Itinerary Construction to be robust
    # Instead of string concatenation on the fly which is messy for nesting, let's parsing into a data structure first.
    return parse_markdown_to_data(lines)

def parse_markdown_to_data(lines):
    days = []
    current_day = None
    
    hotels = []
    food = []
    packing = []
    
    current_list = None
    current_header_context = None
    
    for raw_line in lines:
        line = raw_line.strip()
            
        # Day Header
        match = re.match(r'### (Day \d+): (.+?) - (.+)', line)
        if match:
            day_num, date, title = match.groups()
            current_day = {
                'id': day_num.replace(' ', '').lower(),
                'title': f"{day_num}: {title}",
                'date': date,
                'items': []
            }
            days.append(current_day)
            current_list = None # Stop capturing shortlist
            continue
            
        # Determine indentation level
        indent_level = len(raw_line) - len(raw_line.lstrip())
        is_top_level = indent_level == 0

        # Time Block (Must be top level)
        if is_top_level:
            match = re.match(r'\*   \*\*(.+?)\*\*: (.+)', line.strip())
            if match and current_day:
                time, title = match.groups()
                
                # Formatting for Special Items
                title_clean_text = title.replace('**', '') # Copy for map query
                
                title_class = ""
                if "DECISION POINT" in title:
                    title = title.replace("DECISION POINT:", "").strip()
                    # Clean remaining bold markers
                    title = re.sub(r'\*\*(.*?)\*\*', r'\1', title)
                    title = f'<span style="color: #e67e22; font-weight: bold;">⚠️ DECISION: {title}</span>'
                elif "PRIORITY ACTION" in title:
                     title = title.replace("PRIORITY ACTION:", "").strip()
                     # Clean remaining bold markers
                     title = re.sub(r'\*\*(.*?)\*\*', r'\1', title)
                     title = f'<span style="color: #d35400; font-weight: bold;">🔥 ACTION: {title}</span>'
                else:
                     # Clean bold markers from standard titles
                     # We wrap the whole title in <strong> in the template, so just remove markdown markers.
                     title = title.replace('**', '')

                # Generate Google Maps Link
                # Heuristic: Filter out non-places and generate query
                map_query = title_clean_text
                prefixes = ["Arrive ", "Depart ", "Lunch @ ", "Lunch: ", "Dinner: ", "DECISION POINT: ", "PRIORITY ACTION: ", "Stop: "]
                for p in prefixes:
                    if map_query.startswith(p):
                        map_query = map_query[len(p):].strip()
                        break
                
                # Exclude keywords that likely aren't specific places worth mapping
                exclude_keywords = ["Packing Session", "Return from", "Charge Car", "Book Tours", "The Prep", "Check-in"]
                should_map = not any(k in title_clean_text for k in exclude_keywords) and len(map_query) > 3
                
                if should_map:
                    encoded_query = urllib.parse.quote(map_query)
                    map_url = f"https://www.google.com/maps/search/?api=1&query={encoded_query}"
                    title += f' <a href="{map_url}" target="_blank" style="text-decoration:none; font-size: 0.9em;" title="View on Google Maps">📍</a>'
    
                current_day['items'].append({
                    'time': time,
                    'title': title,
                    'notes': []
                })
                continue

        # Notes (including nested lists for Options)
        # Check keys for indentation
        if indent_level > 0 and current_day and current_day['items']:
            note_raw = line.strip().lstrip('*').strip() 
            
            # Format Links
            note_raw = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" target="_blank">\1</a>', note_raw)
            # Format Bold
            note_raw = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', note_raw)
            
            # Detect labels
            colon_index = note_raw.find(':')
            # Check if colon exists and is early (likely a label), and http is NOT in the label part
            if colon_index != -1 and colon_index < 50 and "http" not in note_raw[:colon_index]:
                parts = note_raw.split(':', 1)
                # Clean label formatting (remove italics/bold markers)
                label_clean = parts[0].strip().replace('*', '').replace('**', '')
                text = parts[1].strip()
                current_day['items'][-1]['notes'].append({'label': label_clean, 'text': text})
            else:
                current_day['items'][-1]['notes'].append({'text': note_raw})
            continue
            
        # Shortlists
        if line.startswith('## 🏨'):
            current_list = hotels
            current_day = None
            continue
        elif line.startswith('## 🍔'):
            current_list = food
            current_day = None
            continue
        elif line.startswith('## 🎒'):
            current_list = packing
            current_day = None
            continue
        elif line.startswith('## '):
            current_list = None
            current_day = None
            continue

        # Shortlists section headers (standalone bold text, not bullets)
        # Note: We check for startswith('**') first. 
        # A bullet line usually starts with "* " or "  *", whereas a header starts immediately with "**".
        # Even though "**" starts with "*", checking startswith('**') is specific enough for our format.
        if current_list is not None and line.startswith('**') and line.endswith('**'):
            # This is a section header like "**Nashville (Fri Night)**"
            header_text = line.strip('*').strip()
            # We add it as a string to be handled as a header in render_card
            current_list.append(f'<br><strong>{header_text}</strong>')
            
            # Store current header for context (e.g. city name)
            # Remove parenthesis content for cleaner search query: "Nashville (Fri Night)" -> "Nashville"
            current_header_clean = re.sub(r'\(.*?\)', '', header_text).strip()
            # Use a slightly hacky way to attach this metadata to the list object or just track it?
            # Since the list is simple items, we can't attach it to the list itself easily without changing structure.
            # But we are in a simple loop. Let's just store it in a local variable `current_header_context`
            # and use it when parsing subsequent items until a new header appears.
            # NOTE: We need to define `current_header_context` inside the function scope first.
            current_header_context = current_header_clean
            continue

        # List Items parsing (generic for all shortlists)
        if current_list is not None:
             # Check raw_line for bullet patterns (before stripping)
             if raw_line.lstrip().startswith('*   '):
                 # Remove the bullet and clean the text
                 text = raw_line.lstrip()[1:].lstrip()  # Remove leading spaces, then first char (*), then remaining spaces
                 
                 # Check for Link pattern: [Name](Url) - Desc or [Name](Url)
                 # Regex explanation:
                 # \[ (.*?) \]  -> Capture Name
                 # \( (.*?) \)  -> Capture URL
                 # \s* [-:]? \s* (.*) -> Optional separator and Capture Description
                 link_match = re.match(r'\[(.*?)\]\((.*?)\)\s*[-:]?\s*(.*)', text)
                 
                 if link_match:
                     name, url, desc = link_match.groups()
                     
                     search_url = None
                     if current_list == hotels and current_header_context:
                         # Generate Google Search URL for prices
                         # Query: "{Hotel Name} {City} hotel prices"
                         query = f"{name} {current_header_context} hotel prices"
                         encoded_query = urllib.parse.quote(query)
                         search_url = f"https://www.google.com/search?q={encoded_query}"
                     
                     current_list.append({
                         'type': 'link_card',
                         'title': name,
                         'url': url,
                         'desc': desc,
                         'search_url': search_url
                     })
                 else:
                     # Standard text item
                     # Links
                     text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" target="_blank">\1</a>', text)
                     # Bold
                     text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
                     
                     current_list.append({
                         'type': 'text',
                         'content': text
                     })

    # --- RENDER HTML STRINGS ---
    
    # 1. Itinerary HTML
    itinerary_html = ""
    for day in days:
        # Add Google Maps link manually based on day for now (hardcoded based on day number to match logic)
        map_link = ""
        if "Day 1" in day['title']:
            map_link = '<br><a href="https://www.google.com/maps/dir/Atlanta,+GA/Chattanooga,+TN/Jack+Daniel\'s+Distillery,+Lynchburg,+TN/Nashville,+TN" target="_blank" class="map-link">📍 View Day 1 Route</a>'
        elif "Day 2" in day['title']:
            map_link = '<br><a href="https://www.google.com/maps/dir/Nashville,+TN/Jim+Beam+American+Stillhouse,+Clermont,+KY/Heaven+Hill+Bourbon+Experience,+Bardstown,+KY/Louisville,+KY" target="_blank" class="map-link">📍 View Day 2 Route</a>'
        elif "Day 3" in day['title']:
             map_link = '<br><a href="https://www.google.com/maps/dir/Louisville,+KY/Buffalo+Trace+Distillery,+Frankfort,+KY/The+Stave,+Millville,+KY/Castle+%26+Key+Distillery,+Frankfort,+KY/Woodford+Reserve+Distillery,+Versailles,+KY/Angel\'s+Envy+Distillery,+Louisville,+KY/Louisville,+KY" target="_blank" class="map-link">📍 View Day 3 Route</a>'
        elif "Day 4" in day['title']:
             map_link = '<br><a href="https://www.google.com/maps/dir/Louisville,+KY/Chattanooga,+TN/Atlanta,+GA" target="_blank" class="map-link">📍 View Day 4 Route</a>'

        day_block = f'''
            <!-- {day['title']} -->
            <div class="day-card">
                <div class="day-header">
                    <h3>{day['title']}</h3>
                    <span class="date">{day['date']}</span>
                </div>
                <div class="day-body">
'''
        for item in day['items']:
            notes_html = ""
            for note in item['notes']:
                if 'label' in note:
                    notes_html += f'<p><span style="color:#666;">{note["label"]}:</span> {note["text"]}</p>'
                else:
                    notes_html += f'<p>{note["text"]}</p>'
                    
            day_block += f'''                    <div class="time-block">
                        <span class="time">{item['time']}</span>
                        <div class="details">
                            <strong>{item['title']}</strong>
                            {notes_html}
                        </div>
                    </div>
'''
        day_block += f'''                    <div class="map-link-container">
                        {map_link}
                    </div>
                </div>
            </div>
'''
        itinerary_html += day_block

    # 2. Shortlist HTML
    def render_card(title, items):
        if not items:
             return ""
        
        html_parts = []
        current_grid_open = False
        
        def ensure_grid(open_grid):
            nonlocal current_grid_open
            if open_grid and not current_grid_open:
                html_parts.append('<div class="options-grid">')
                current_grid_open = True
            elif not open_grid and current_grid_open:
                html_parts.append('</div>')
                current_grid_open = False

        for item in items:
            # Handle Headers (City separators)
            if isinstance(item, str): 
                ensure_grid(False)
                html_parts.append(f'<div class="list-sub-header">{item}</div>')
                
            # Handle Items
            elif isinstance(item, dict):
                if item['type'] == 'link_card':
                    ensure_grid(True)
                    desc_html = f'<p>{item["desc"]}</p>' if item['desc'] else ''
                    
                    search_link_html = ""
                    if 'search_url' in item and item['search_url']:
                         search_link_html = f'''
                            <div style="margin-top:0.8rem; padding-top:0.8rem; border-top:1px solid rgba(255,255,255,0.1);">
                                <a href="{item['search_url']}" target="_blank" style="color: #bbb; font-size: 0.85rem; display: flex; align-items: center; gap: 0.5rem; transition: color 0.2s;">
                                    🔍 <span style="text-decoration: underline;">Check Prices & Reviews</span>
                                </a>
                            </div>
                        '''

                    # New Div Structure for Link Card (replaces direct <a>)
                    html_parts.append(f'''
                        <div class="option-card" style="cursor: default;">
                            <div style="display:flex; justify-content:space-between; align-items:start;">
                                <h4 style="margin-bottom:0;"><a href="{item['url']}" target="_blank" style="text-decoration:none; color:inherit;">{item['title']} ↗</a></h4>
                            </div>
                            {desc_html}
                            {search_link_html}
                        </div>
                    ''')

                elif item['type'] == 'text':
                     ensure_grid(False) # Break grid for simple text lists
                     html_parts.append(f'<div class="list-item-simple">• {item["content"]}</div>')

        ensure_grid(False) # Close grid
        
        inner_html = "".join(html_parts)
        
        return f'''
            <div class="stat-card" style="flex: 1; min-width: 300px; padding: 1.5rem;">
                <h3>{title}</h3>
                <div class="details">
                    {inner_html}
                </div>
            </div>
'''

    shortlist_html = render_card("🏨 Hotels", hotels) + \
                     render_card("🍔 Food & Drink", food) + \
                     render_card("🎒 Packing List", packing)

    return itinerary_html, shortlist_html

def check_structure():
    # Verify we can find the template
    if not os.path.exists(os.path.join(TEMPLATE_DIR, TEMPLATE_FILE)):
        print(f"Error: Template not found at {os.path.join(TEMPLATE_DIR, TEMPLATE_FILE)}")
        exit(1)

def build():
    check_structure()
    
    print(f"Reading {PLAN_FILE}...")
    itinerary, shortlist = parse_markdown(PLAN_FILE)
    
    print("rendering template...")
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template(TEMPLATE_FILE)
    
    output_content = template.render(
        itinerary_content=itinerary,
        shortlist_content=shortlist
    )
    
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_content)
        
    print(f"Successfully generated {output_path}")

if __name__ == "__main__":
    build()
