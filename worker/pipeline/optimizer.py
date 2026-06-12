"""Pipeline stage that finalizes or optimizes PDF output."""

import shutil

def optimize(input_path: str, output_path: str):
    shutil.copyfile(input_path, output_path)