from nncore.core.models import MODEL_REGISTRY
from torchvision.models.segmentation import deeplabv3_resnet50

MODEL_REGISTRY.register(deeplabv3_resnet50)