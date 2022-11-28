"""
Instruction templates for each task
"""

full_img_instruct = """
FULL IMAGES : Mark DISTRESS or SLIGHT_DISTRESS if ANY distress is visible, else mark NO_DISTRESS or UNKNOWN
"""

board_img_instruct = """
BOARD IMAGES : Mark DISTRESS if boarded window is visible, else mark NO_DISTRESS
"""

tarp_img_instruct = """
TARP IMAGES : Mark DISTRESS if tarped roof is visible, else mark NO_DISTRESS
"""

patch_img_instruct = """
PATCH IMAGES : Mark DISTRESS if patch has distress, else mark NO_DISTRESS
"""

new_patch_img_instruct = """
NEW PATCH IMAGES : Only Mark Distress if distress is seen, else mark TRASH
"""

new_patch_img_instruct = """
NEW TARP IMAGES : Only Mark Distress if distress is seen, else mark TRASH
"""

new_patch_img_instruct = """
NEW BOARD IMAGES : Only Mark Distress if distress is seen, else mark TRASH
"""