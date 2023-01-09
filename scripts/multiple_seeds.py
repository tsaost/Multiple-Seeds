# Multiple Seeds script for Automatic1111
# Version: 1.0
# Release date: 11/29/2022
# Author: Zyin

import re
import copy
import modules.scripts as scripts
import gradio as gr

import modules.shared as shared

from modules.processing import process_images, Processed

class Script(scripts.Script):
    def title(self):
        return "Multiple Seeds"

    def show(self, is_img2img):
        return not is_img2img #only show in txt2img. not relevant for img2img

    def ui(self, is_img2img):
        with gr.Row():
            with gr.Column():
                gr.Textbox(label="Text box that doesn't do anything", lines=2, placeholder="This handy textbox can be used as temporary storage for seeds while you keep searching for good seeds")
                seed_textbox = gr.Textbox(label="Seeds", lines=1, placeholder="List of seed values (Seperate with commas, spaces, or newlines)")
                gr.HTML(
                    """
                    <div style=" margin-left: 20px;">
                    This script will only activate when one or more seeds are typed in this Seeds textbox.
                    <br>If there are no seeds entered, then images will be generated as normal, as if this script wasn't running.
                    <br>But if there are seeds entered, Batch count and Batch size above are ignored, and each seed will be generated one at a time.
                    <br>If there is just two seeks, then do all the seeds between the two
                    </div>
                    """)

        return [seed_textbox]

    def run(self, p, seed_textbox):

        if seed_textbox.strip() == "":
            return #generate images as if this script isn't activated

        seeds = []
        seeds = re.split(",| |\n", seed_textbox) #split by comma, space, or newline
        seeds = list(filter(None, seeds)) # filter out any bad data created by multiple seperators in the textbox

        if len(seeds) == 2 and seeds[0] < seeds[1]:
            seeds = list(range(seeds[0], seeds[1]))

        if p.enable_hr:
            print(f"Will create {len(seeds)} images ({len(seeds)*2} jobs with Highres fix) with seeds: {seed_textbox}")
        else:
            print(f"Will create {len(seeds)} images with seeds: {seed_textbox}")

        p.all_seeds = seeds
        p.n_iter = 1  # override users 'Batch count'
        p.batch_size = 1  # override users 'Batch size'
        images_list = []
        for seed in seeds:
            #print("Seed: ["+seed+"]\n")
            shared.state.job_count = len(seeds) # for some reason, this line fixes the broken progress bar when using "Highres. fix" (p.enable_hr)
            p.seed = seed.strip()
            proc = process_images(p)
            images_list += proc.images
        info_text = "Seeds:\n" + seed_textbox
        return Processed(p, images_list, seeds[0], info_text, None, None, seeds)
        #(StableDiffusionProcessing, images_list, seed = -1, info = "", subseed = None, all_prompts = None, all_seeds = None, all_subseeds = None, index_of_first_image = 0, infotexts = None):
