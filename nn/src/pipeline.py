from opt import opts
from utils.getter import get_instance, get_data
from utils.typing import *
from utils import load_yaml
from models import ModelWithLoss

from torchvision.transforms import transforms as tf


class Pipeline(object):
    """docstring for Pipeline."""

    def __init__(self, opt: opts, cfg_path: Optional[str] = None):
        super(Pipeline, self).__init__()
        self.opt = opt
        assert (
            cfg_path is not None
        ), "learner params is none, \ please create config file follow default format. \n You could find an example in nn/configs/default/learner.yaml"
        self.cfg = load_yaml(cfg_path)

        self.device = get_instance(self.cfg["device"])

        self.transform = [
            tf.ToTensor(),
            tf.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]

        self.train_dataloader, self.val_dataloader = get_data(
            self.cfg["data"], return_dataset=False
        )
        model = get_instance(self.cfg["model"]).to(self.device)

        criterion = get_instance(self.cfg["criterion"]).to(self.device)

        self.model = ModelWithLoss(model, criterion).to(self.device)

        self.metric = {mcfg["name"]: get_instance(mcfg) for mcfg in self.cfg["metric"]}

        self.optimizer = get_instance(
            self.cfg["optimizer"], params=self.model.model.parameters()
        )

        self.scheduler = get_instance(self.cfg["scheduler"], optimizer=self.optimizer)

        self.learner = get_instance(
            self.cfg["learner"],
            cfg=self.opt,
            train_data=self.train_dataloader,
            val_data=self.val_dataloader,
            scheduler=self.scheduler,
            model=self.model,
            metrics=self.metric,
            optimizer=self.optimizer,
        )

    def fit(self):
        self.learner.fit()


if __name__ == "__main__":
    opt = opts().parse()
    train_pipeline = Pipeline(opt, cfg_path="./configs/default/learner.yaml")
    train_pipeline.fit()
