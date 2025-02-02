import argparse
from argparse import Namespace
from datetime import datetime
from pathlib import Path
from typing import Dict

import yaml


class opts(object):
    def __init__(self, cfg_path: str):

        with open(cfg_path, "r") as f:
            self.args = yaml.load(f, Loader=yaml.Loader)['opts']

        self.parser = argparse.ArgumentParser()

        self.parser.add_argument("--id")
        self.parser.add_argument("--test", action="store_true", default=False)
        self.parser.add_argument(
            "--debug",
            type=int,
            help="level of visualization."
            "1: only show the final detection results"
            "2: show the network output features"
            "3: use matplot to display"  # useful when lunching training with ipython notebook
            "4: save all visualizations to disk",
        )
        self.parser.add_argument(
            "--demo", help="save lastest sample", action="store_true", default=False
        )
        self.parser.add_argument(
            "--fp16",
            help="use floating point (only work in gpu machine)",
            action="store_true",
            default=False,
        )
        self.parser.add_argument(
            "--load-model", default="", help="path to pretrained model"
        )
        self.parser.add_argument(
            "--cfg-pipeline", default=None, help="path to pipeline yaml"
        )
        self.parser.add_argument(
            "--resume",
            action="store_true",
            help="resume an experiment. "
            "Reloaded the optimizer parameter and "
            "set load_model to model_last.pth "
            "in the exp dir if load_model is empty.",
        )

        # system
        self.parser.add_argument(
            "--gpus", help="-1 for CPU, use comma for multiple gpus"
        )
        self.parser.add_argument(
            "--num-workers", type=int, help="dataloader threads. 0 for single-thread.",
        )
        self.parser.add_argument("--seed", type=int, help="random seed")
        # log
        self.parser.add_argument(
            "--verbose", type=int, help="disable progress bar and print to screen.",
        )
        self.parser.add_argument("--config-path", type=str)

        # train
        self.parser.add_argument("--nepochs", type=int, help="total training epochs.")
        self.parser.add_argument("--batch-size", type=int, help="batch size")
        self.parser.add_argument(
            "--num-iters", type=int, help="default: #samples / batch_size."
        )
        self.parser.add_argument(
            "--val-step", type=int, help="number of epochs to run validation.",
        )

        self.parser.add_argument(
            "--log-step", type=int, help="number of epochs to logging.",
        )
        self.parser.add_argument(
            "--save-dir", type=str, help="saving path",
        )

    @staticmethod
    def fill(a: Dict, b: Dict) -> Dict:
        for k, v in b.items():
            if a.get(k, None) is None:
                a.update({k: v})
        return a

    def parse_args(self):
        args = vars(self.parser.parse_args())
        if args["config_path"] is None:
            self.args = self.fill(args, self.args)
        else:
            with open(args['config_path'], 'rt') as f:
                self.args = yaml.load(f)['opts']

    def parse(self):
        args = self.args
        opt = Namespace(**args)

        opt.gpus_str = opt.gpus
        opt.gpus = list(map(int, opt.gpus.split(",")))
        opt.save_dir = (
            Path(opt.save_dir)
            / f'{opt.id}_{datetime.now().strftime("%Y_%m_%d-%H_%M_%S")}'
        )
        if opt.debug > 0:
            opt.num_workers = 0
            opt.batch_size = 1
            opt.gpus = [opt.gpus[0]]
            opt.master_batch_size = -1
        print(f"The output will be saved to {opt.save_dir}")
        return opt

