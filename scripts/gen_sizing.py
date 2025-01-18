import re

sizing_file = ""

# width rem
width_rem_format = """.w-{size} {{
    width: {size}rem;
}}\n\n"""

# width percentage
width_precent_format = """.w-{size}p {{
    width: {size}%;
}}\n\n"""

# width vw
width_vw_format = """.w-{size}vw {{
    width: {size}vw;
}}\n\n"""

# height rem
height_rem_format = """.h-{size} {{
    height: {size}rem;
}}\n\n"""

# height percentage
height_percent_format = """.h-{size}p {{
    height: {size}%;
}}\n\n"""

# height vw
height_vh_format = """.h-{size}vh {{
    height: {size}vh;
}}\n\n"""

max_width_rem_format = """.maxw-{size} {{
    max-width: {size}rem;
}}\n\n"""

min_width_rem_format = """.minw-{size} {{
    min-width: {size}rem;
}}\n\n"""

max_width_percent_format = """.maxw-{size}p {{
    max-width: {size}%;
}}\n\n"""

min_width_percent_format = """.minw-{size}p {{
    min-width: {size}%;
}}\n\n"""

max_width_vw_format = """.maxw-{size}vw {{
    max-width: {size}vw;
}}\n\n"""

min_width_vw_format = """.minw-{size}vw {{
    min-width: {size}vw;
}}\n\n"""

max_height_rem_format = """.maxh-{size} {{
    max-height: {size}rem;
}}\n\n"""

min_height_rem_format = """.minh-{size} {{
    min-height: {size}rem;
}}\n\n"""

max_height_percent_format = """.maxh-{size}p {{
    max-height: {size}%;
}}\n\n"""

min_height_percent_format = """.minh-{size}p {{
    min-height: {size}%;
}}\n\n"""

max_height_vh_format = """.maxh-{size}vh {{
    max-height: {size}vh;
}}\n\n"""

min_height_vh_format = """.minh-{size}vh {{
    min-height: {size}vh;
}}\n\n"""

formats_1 = [
    width_rem_format,
    max_width_rem_format,
    min_width_rem_format,
    height_rem_format,
    max_height_rem_format,
    min_height_rem_format
]

formats_10 = [
    width_precent_format, 
    width_vw_format, 
    height_percent_format, 
    height_vh_format,
    max_height_percent_format,
    max_height_vh_format,
    max_width_percent_format,
    max_width_vw_format,
    min_height_percent_format,
    min_height_vh_format,
    min_width_percent_format,
    min_width_vw_format
]

for i in range(10,105,10):
    for format in formats_10:
        sizing_file += format.format(size=i)

for i in range(26):
    for format in formats_1:
        sizing_file += format.format(size=i)

additional = \
""".overflow-scroll {
    overflow: scroll;
}

.overflow-hidden {
    overflow: hidden;
}

.overflow-auto {
    overflow: auto;
}
"""

sizing_file += additional

with open("hub/static/hub/sizing.css", "w") as file:
    file.write(re.sub(r'\s+', '', sizing_file))