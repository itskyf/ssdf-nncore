from typing import Dict

import torch
import torch.nn as nn
import torch.nn.functional as F

from . import CRITERION_REGISTRY

"""
Source: https://github.com/hubutui/DiceLoss-PyTorch/blob/master/loss.py
"""


@CRITERION_REGISTRY.register()
class BinaryDiceLoss(nn.Module):
    """
    Dice loss of binary class
    Args:
        smooth: A float number to smooth loss, and avoid NaN error, default: 1
        p: Denominator value: \sum{x^p} + \sum{y^p}, default: 2
        predict: A tensor of shape [batch_size, W, H]
        target: A tensor of shape same with predict
        reduction: Reduction method to apply, return mean over batch if 'mean',
            return sum if 'sum', return a tensor of shape [batch_size,] if 'none'
    Returns:
        Loss tensor according to arg reduction
    Raise:
        Exception if unexpected reduction
    """

    def __init__(self, smooth=1, p=2, reduction="mean"):
        super(BinaryDiceLoss, self).__init__()
        self.smooth = smooth
        self.p = p
        self.reduction = reduction

    def forward(self, predict, target):
        assert (
            predict.shape[0] == target.shape[0]
        ), "predict & target batch size don't match"
        predict = predict.contiguous().view(predict.shape[0], -1)
        target = target.contiguous().view(target.shape[0], -1)

        num = torch.sum(torch.mul(predict, target), dim=1) + self.smooth
        den = torch.sum(predict.pow(self.p) +
                        target.pow(self.p), dim=1) + self.smooth

        loss = 1 - num / den

        if self.reduction == "mean":
            return loss.mean()
        elif self.reduction == "sum":
            return loss.sum()
        elif self.reduction == "none":
            return loss
        else:
            raise Exception("Unexpected reduction {}".format(self.reduction))


@CRITERION_REGISTRY.register()
class DiceLoss(nn.Module):
    """Dice loss, need one hot encode input
    Args:
        weight: An array of shape [num_classes]
        ignore_index: class index to ignore
        predict: A tensor of shape [batch_size, num_classes, W, H]
        target: A tensor of same shape with predict
        other args pass to BinaryDiceLoss
    Return:
        same as BinaryDiceLoss
    """

    def __init__(self, weight=None, ignore_index=None, **kwargs):
        super(DiceLoss, self).__init__()
        self.kwargs = kwargs
        self.weight = weight
        self.ignore_index = ignore_index

    def forward(self, predict, target):
        assert predict.shape == target.shape, "predict & target shape do not match"
        dice = BinaryDiceLoss(**self.kwargs)
        total_loss = 0
        predict = F.softmax(predict, dim=1)

        for i in range(target.shape[1]):
            if i != self.ignore_index:
                dice_loss = dice(predict[:, i], target[:, i])
                if self.weight is not None:
                    assert (
                        self.weight.shape[0] == target.shape[1]
                    ), "Expect weight shape [{}], get[{}]".format(
                        target.shape[1], self.weight.shape[0]
                    )
                    dice_loss *= self.weights[i]
                total_loss += dice_loss

        return total_loss / target.shape[1]


@CRITERION_REGISTRY.register()
class Dicewithstat(nn.Module):
    r"""Dicewithstat is warper of cross-entropy loss"""

    def __init__(self, weight=None, ignore_index=None):
        super(Dicewithstat, self).__init__()
        self.loss = DiceLoss(weight=None, ignore_index=None)

    def forward(self, pred, batch):
        pred = pred["out"] if isinstance(pred, Dict) else pred
        # in torchvision models, pred is a dict[key=out, value=Tensor]
        target = batch["mask"] if isinstance(batch, Dict) else batch
        # custom label is storaged in batch["mask"]
        print("Dicewithstat: pred:", pred.shape, "target:", target.shape)
        loss = self.loss(pred, target)
        loss_dict = {"loss": loss}
        return loss, loss_dict
