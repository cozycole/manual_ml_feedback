"""
Instruction templates for each task
"""
from textwrap import dedent
instruct_dict = {
        "full_img_instruct": dedent("""
        FULL IMAGES : Mark DISTRESS or SLIGHT_DISTRESS if ANY distress is visible, else mark NO_DISTRESS or UNKNOWN
        """),
        "board_patch_instruct": dedent("""
        BOARD IMAGES : Mark DISTRESS if boarded window is visible, else mark NO_DISTRESS
        """),
        "tarp_patch_instruct": dedent("""
        TARP IMAGES : Mark DISTRESS if tarped roof is visible, else mark NO_DISTRESS
        """),
        "distress_patch_instruct": dedent("""
        PATCH IMAGES : Mark DISTRESS if patch has distress, else mark NO_DISTRESS
        """),
        "new_distress_patch_instruct": dedent("""
        NEW PATCH IMAGES : Only mark DISTRESS if distress is visible, else mark TRASH
        """),
        "new_tarp_patch_instruct": dedent("""
        NEW TARP IMAGES : Only mark DISTRESS if tarp is visible, else mark TRASH
        """),
        "new_board_patch_instruct": dedent("""
        NEW BOARD IMAGES : Only mark DISTRESS if board is visible, else mark TRASH
        """)
}