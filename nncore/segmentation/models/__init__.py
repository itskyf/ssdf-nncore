from nncore.core.models import MODEL_REGISTRY
from torchvision.models.segmentation.segmentation import deeplabv3_resnet50
from .mobileunet import MobileUnet

MODEL_REGISTRY.register(deeplabv3_resnet50)
