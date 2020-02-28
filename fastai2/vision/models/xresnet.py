# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/11_vision.models.xresnet.ipynb (unless otherwise specified).

__all__ = ['init_cnn', 'XResNet', 'xresnet18', 'xresnet34', 'xresnet50', 'xresnet101', 'xresnet152', 'xresnet18_deep',
           'xresnet34_deep', 'xresnet50_deep', 'xresnet18_deeper', 'xresnet34_deeper', 'xresnet50_deeper', 'se_kwargs1',
           'se_kwargs2', 'se_kwargs3', 'g0', 'g1', 'g2', 'g3', 'xse_resnet18', 'xse_resnext18', 'xresnext18',
           'xse_resnet34', 'xse_resnext34', 'xresnext34', 'xse_resnet50', 'xse_resnext50', 'xresnext50',
           'xse_resnet101', 'xse_resnext101', 'xresnext101', 'xse_resnet152', 'xsenet154', 'xse_resnext18_deep',
           'xse_resnext34_deep', 'xse_resnext50_deep', 'xse_resnext18_deeper', 'xse_resnext34_deeper',
           'xse_resnext50_deeper']

# Cell
from ...torch_basics import *
from torchvision.models.utils import load_state_dict_from_url

# Cell
def init_cnn(m):
    if getattr(m, 'bias', None) is not None: nn.init.constant_(m.bias, 0)
    if isinstance(m, (nn.Conv2d,nn.Linear)): nn.init.kaiming_normal_(m.weight)
    for l in m.children(): init_cnn(l)

# Cell
class XResNet(nn.Sequential):
    @delegates(ResBlock)
    def __init__(self, block, expansion, layers, p=0.0, c_in=3, c_out=1000, stem_szs=(32,32,64),
                 widen=1.0, sa=False, act_cls=defaults.activation, **kwargs):
        store_attr(self, 'block,expansion,act_cls')
        stem_szs = [c_in, *stem_szs]
        stem = [ConvLayer(stem_szs[i], stem_szs[i+1], stride=2 if i==0 else 1, act_cls=act_cls)
                for i in range(3)]

        block_szs = [int(o*widen) for o in [64,128,256,512] +[256]*(len(layers)-4)]
        block_szs = [64//expansion] + block_szs
        blocks    = self._make_blocks(layers, block_szs, sa, **kwargs)

        super().__init__(
            *stem, nn.MaxPool2d(kernel_size=3, stride=2, padding=1),
            *blocks,
            nn.AdaptiveAvgPool2d(1), Flatten(), nn.Dropout(p),
            nn.Linear(block_szs[-1]*expansion, c_out),
        )
        init_cnn(self)

    def _make_blocks(self, layers, block_szs, sa, **kwargs):
        return [self._make_layer(ni=block_szs[i], nf=block_szs[i+1], blocks=l,
                                 stride=1 if i==0 else 2, sa=sa and i==len(layers)-4, **kwargs)
                for i,l in enumerate(layers)]

    def _make_layer(self, ni, nf, blocks, stride, sa, **kwargs):
        return nn.Sequential(
            *[self.block(self.expansion, ni if i==0 else nf, nf, stride=stride if i==0 else 1,
                      sa=sa and i==(blocks-1), act_cls=self.act_cls, **kwargs)
              for i in range(blocks)])

# Cell
def _xresnet(pretrained, expansion, layers, **kwargs):
    # TODO pretrain all sizes. Currently will fail with non-xrn50
    url = 'https://s3.amazonaws.com/fast-ai-modelzoo/xrn50_940.pth'
    res = XResNet(ResBlock, expansion, layers, **kwargs)
    if pretrained: res.load_state_dict(load_state_dict_from_url(url, map_location='cpu')['model'], strict=False)
    return res

def xresnet18 (pretrained=False, **kwargs): return _xresnet(pretrained, 1, [2, 2,  2, 2], **kwargs)
def xresnet34 (pretrained=False, **kwargs): return _xresnet(pretrained, 1, [3, 4,  6, 3], **kwargs)
def xresnet50 (pretrained=False, **kwargs): return _xresnet(pretrained, 4, [3, 4,  6, 3], **kwargs)
def xresnet101(pretrained=False, **kwargs): return _xresnet(pretrained, 4, [3, 4, 23, 3], **kwargs)
def xresnet152(pretrained=False, **kwargs): return _xresnet(pretrained, 4, [3, 8, 36, 3], **kwargs)
def xresnet18_deep  (pretrained=False, **kwargs): return _xresnet(pretrained, 1, [2,2,2,2,1,1], **kwargs)
def xresnet34_deep  (pretrained=False, **kwargs): return _xresnet(pretrained, 1, [3,4,6,3,1,1], **kwargs)
def xresnet50_deep  (pretrained=False, **kwargs): return _xresnet(pretrained, 4, [3,4,6,3,1,1], **kwargs)
def xresnet18_deeper(pretrained=False, **kwargs): return _xresnet(pretrained, 1, [2,2,1,1,1,1,1,1], **kwargs)
def xresnet34_deeper(pretrained=False, **kwargs): return _xresnet(pretrained, 1, [3,4,6,3,1,1,1,1], **kwargs)
def xresnet50_deeper(pretrained=False, **kwargs): return _xresnet(pretrained, 4, [3,4,6,3,1,1,1,1], **kwargs)

# Cell
se_kwargs1 = dict(groups=1 , reduction=16)
se_kwargs2 = dict(groups=32, reduction=16)
se_kwargs3 = dict(groups=32, reduction=0)
g0 = [2,2,2,2]
g1 = [3,4,6,3]
g2 = [3,4,23,3]
g3 = [3,8,36,3]

# Cell
def xse_resnet18(c_out=1000, pretrained=False, **kwargs):   return XResNet(SEBlock,  1, g0, c_out=c_out, **se_kwargs1, **kwargs)
def xse_resnext18(c_out=1000, pretrained=False, **kwargs):  return XResNet(SEResNeXtBlock, 1, g0, c_out=c_out, **se_kwargs2, **kwargs)
def xresnext18(c_out=1000, pretrained=False, **kwargs):     return XResNet(SEResNeXtBlock, 1, g0, c_out=c_out, **se_kwargs3, **kwargs)
def xse_resnet34(c_out=1000, pretrained=False, **kwargs):   return XResNet(SEBlock,  1, g1, c_out=c_out, **se_kwargs1, **kwargs)
def xse_resnext34(c_out=1000, pretrained=False, **kwargs):  return XResNet(SEResNeXtBlock, 1, g1, c_out=c_out, **se_kwargs2, **kwargs)
def xresnext34(c_out=1000, pretrained=False, **kwargs):     return XResNet(SEResNeXtBlock, 1, g1, c_out=c_out, **se_kwargs3, **kwargs)
def xse_resnet50(c_out=1000, pretrained=False, **kwargs):   return XResNet(SEBlock,  4, g1, c_out=c_out, **se_kwargs1, **kwargs)
def xse_resnext50(c_out=1000, pretrained=False, **kwargs):  return XResNet(SEResNeXtBlock, 4, g1, c_out=c_out, **se_kwargs2, **kwargs)
def xresnext50(c_out=1000, pretrained=False, **kwargs):     return XResNet(SEResNeXtBlock, 4, g1, c_out=c_out, **se_kwargs3, **kwargs)
def xse_resnet101(c_out=1000, pretrained=False, **kwargs):  return XResNet(SEBlock,  4, g2, c_out=c_out, **se_kwargs1, **kwargs)
def xse_resnext101(c_out=1000, pretrained=False, **kwargs): return XResNet(SEResNeXtBlock, 4, g2, c_out=c_out, **se_kwargs2, **kwargs)
def xresnext101(c_out=1000, pretrained=False, **kwargs):    return XResNet(SEResNeXtBlock, 4, g2, c_out=c_out, **se_kwargs3, **kwargs)
def xse_resnet152(c_out=1000, pretrained=False, **kwargs):  return XResNet(SEBlock,  4, g3, c_out=c_out, **se_kwargs1, **kwargs)
def xsenet154(c_out=1000, pretrained=False, **kwargs):
    return XResNet(SEBlock, g3, groups=64, reduction=16, p=0.2, c_out=c_out)
def xse_resnext18_deep  (c_out=1000, pretrained=False, **kwargs):  return XResNet(SEResNeXtBlock, 1, g0+[1,1], c_out=c_out, **se_kwargs2, **kwargs)
def xse_resnext34_deep  (c_out=1000, pretrained=False, **kwargs):  return XResNet(SEResNeXtBlock, 1, g1+[1,1], c_out=c_out, **se_kwargs2, **kwargs)
def xse_resnext50_deep  (c_out=1000, pretrained=False, **kwargs):  return XResNet(SEResNeXtBlock, 4, g1+[1,1], c_out=c_out, **se_kwargs2, **kwargs)
def xse_resnext18_deeper(c_out=1000, pretrained=False, **kwargs):  return XResNet(SEResNeXtBlock, 1, [2,2,1,1,1,1,1,1], c_out=c_out, **se_kwargs2, **kwargs)
def xse_resnext34_deeper(c_out=1000, pretrained=False, **kwargs):  return XResNet(SEResNeXtBlock, 1, [3,4,4,2,2,1,1,1], c_out=c_out, **se_kwargs2, **kwargs)
def xse_resnext50_deeper(c_out=1000, pretrained=False, **kwargs):  return XResNet(SEResNeXtBlock, 4, [3,4,4,2,2,1,1,1], c_out=c_out, **se_kwargs2, **kwargs)