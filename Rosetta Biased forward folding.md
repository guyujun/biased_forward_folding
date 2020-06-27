# Biased forward folding: 蛋白可折叠性验证

> 参考1: https://www.rosettacommons.org/docs/latest/Biased-forward-folding
>
> 参考2: https://github.com/emarcos/biased_forward_folding/
>
> 参考3: https://www.rosettacommons.org/docs/latest/application_documentation/structure_prediction/abinitio



## 前言

Rosetta的Ab initio预测蛋白质结构的方法流可以较为准确地验证验证denovo蛋白质序列和结构匹配性。蛋白质的折叠自由能面通常被认为是漏斗形的，而蛋白质的天然结构处于全局能量最小点，与其他折叠中间态的构象有着显著的能量差异。因此在如果人工设计出来的蛋白质也有相类似的能量漏斗，即可以评估出设计来的结构的合理性。

但是Ab initio的计算量是巨大的，因此严重限制了它在denovo design的过程中的应用。而Biased forward folding simulations是一种非常经济的模拟手段，可以快速地鉴定出哪些设计结构在Ab initio模拟时更容易折叠成设计的目的状态。

Biased forward folding的基本思想是使用更小的fragment集合来加速模拟的过程，通常Ab initio模拟时每个9mer窗口会使用200个fragment片段，而在Biased forward folding中仅选取每个窗口中与目标折叠状态RMSD最低的fragment（9-，3-mers）。如果在偏向性如此明显的状态下依然不能采集到的我们的目标状态，那说明在标准的Ab initio folding中，目标状态的采集率也是非常低的，侧面可认为我们设计出来的结构与其序列之间存在不匹配性。

Biased forward folding的方案使得我们在设计的过程中验证成千上万的结构的可折叠性。从而排除那些在实验中可能不进行表达的结构与序列。



## Biased forward folding的使用

follow教程前，前clone本人修改后的仓库:



### 1. 准备Fragment文件

Biased forward folding就是简化版的Ab initio folding. 首先我们需要先获取用于从头折叠模拟的fragment set，生成fragment的方法有许多，可以用Rosetta自带的FragmentPicker，也可以使用Tong Wang等开发的DeepFraglib(http://structpred.life.tsinghua.edu.cn/DeepFragLib.html)。总之生成的规范要符合Rosetta的Fragment格式即可。

**此处我们以FragmentPicker的BestFragmentsProtocol为例进行生成，具体的生成方法可参考：Rosetta Fragment Picker: 短肽片段分选器(https://zhuanlan.zhihu.com/p/66175162)此文。此处不做重复的阐述**

应当注意的事项时：

1. 创建wghts权重文件时加入FragmentCrmsd权重
2. 使用`-frags::describe_fragments`来输出fragment具体信息的文件，如以.fsc结尾的文件。此文件中记载了
3. 使用`-in::file::s`来输入denovo生成好的蛋白结构



以github中案例为例:

此处已经提前准备好了ss2文件以及simple.wghts. 需要进一步把你的环境配置写入flags参数文件中:

- -in::file::vall 需要根据实际的vall路径填写。

```shell
fragment_picker.macosclangrelease @flags
```





### 2. 分离与结构最相似的Fragment子集

此处Biased forward folding的github源有开源的代码，但是由于部分app在Rosetta的public release中已经移除。因此本人提供了最新的修改版，github地址为: 

该仓库中包括了一个pick生成的3mers以及他的打分文件.fsc，以及修改后的脚本lowrms_frags_topN.py（适配python3）。

使用方法: 

```shell
# 获取top3 3mer fragment set
python lowrms_frags_topN.py -frag_qual frags.fsc.3mers -ntop 3 -fullmer frags.3mers -out top3.3mers

# 获取top3 9mer fragment set
python lowrms_frags_topN.py -frag_qual frags.fsc.9mers -ntop 3 -fullmer frags.9mers -out top3.9mers
```

- frag_qual：输入上述的fragment打分文件
- ntop：pick排名前X的fragment用于模拟
- fullmer：fragment原始文件（即FragmentPicker生成的原始文件）
- out：输出的新Fragment子集文件



值得注意的是，此处我们需要同时生成9-和3-mer fragment文件。默认推荐使用Cα原子RMSD最低的前3个Fragment做快速模拟。（即ntop=3）



### 3. 进行Ab initio folding模拟

有了新的Fragment子集后，我们就可以使用标准的ab initio structure prediction app来进行结构模拟，

建议采样30-50条模拟的轨迹来评估我们的目的构象是否在ab initio folding中出现。

运行方法: 

```shell
AbinitioRelax.default.macosclangrelease -in:file:native 2jsvX.pdb -in:file:fasta 2jsvX.fasta -in:file:frag3 top3.3mers -in:file:frag9 top3.9mers -abinitio:relax -relax::fast -abinitio::increase_cycles 10 -ex1 -ex2aro -abinitio::use_filters false -abinitio::rsd_wt_loop 0.5 -abinitio::rsd_wt_helix 0.5 -abinitio::rg_reweight 0.5 -out:pdb -nstruct 30
```

输出30个PDB文件, 如S_00000001.pdb等。

后续可以继续分析是否呈现能量漏斗形，或是否输出的目标PDB与设计的结构RMSD小于某个截断值来判断设计的合理性。

更加具体的Ab initio folding官方教程可以参考这里: https://www.rosettacommons.org/demos/latest/tutorials/denovo_structure_prediction/Denovo_structure_prediction







